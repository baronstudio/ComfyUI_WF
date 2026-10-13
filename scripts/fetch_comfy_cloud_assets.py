#!/usr/bin/env python3
"""
Récupère les assets du compte Comfy Cloud (cloud.comfy.org) en local.

Dépendances : aucune (stdlib Python >= 3.10).
Config      : fichier .env à la racine du repo (voir .env.example) :
                COMFY_CLOUD_API_KEY=comfyui-xxxx                 (obligatoire)
                COMFY_CLOUD_BASE_URL=https://cloud.comfy.org     (optionnel)
                COMFY_CLOUD_OUT_DIR=comfy_cloud_assets           (optionnel)

Exemples :
  python scripts/fetch_comfy_cloud_assets.py --list              # inventaire, rien n'est téléchargé
  python scripts/fetch_comfy_cloud_assets.py                     # tout télécharger
  python scripts/fetch_comfy_cloud_assets.py --tag output        # seulement les sorties de rendu
  python scripts/fetch_comfy_cloud_assets.py --since 2026-10-01 --name qwen
  python scripts/fetch_comfy_cloud_assets.py --out D:/Renders/comfy --workers 6

Sécurité : le téléchargement se fait en deux temps (lecture du 302 avec la clé,
puis GET de l'URL signée SANS header) pour ne jamais envoyer la clé au stockage.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE_URL = "https://cloud.comfy.org"
DEFAULT_OUT_DIR = "comfy_cloud_assets"
PAGE_SIZE = 500  # max autorisé par l'API
USER_AGENT = "ComfyUI_WF-asset-fetcher/1.0"
TIMEOUT = 60


# --------------------------------------------------------------------------- #
# .env
# --------------------------------------------------------------------------- #
def load_dotenv(path: Path) -> None:
    """Charge KEY=VALUE dans os.environ sans écraser les variables déjà définies."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Empêche urllib de suivre les redirections (on lit Location nous-mêmes)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER_NO_REDIRECT = urllib.request.build_opener(_NoRedirect)
_OPENER_PLAIN = urllib.request.build_opener()


class ApiError(RuntimeError):
    pass


class ComfyCloud:
    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    # ---- helpers ---------------------------------------------------------- #
    def _headers(self, bearer: bool = False) -> dict[str, str]:
        h = {"User-Agent": USER_AGENT, "Accept": "application/json, */*"}
        if bearer:
            h["Authorization"] = f"Bearer {self.api_key}"
        else:
            h["X-API-Key"] = self.api_key
        return h

    def _get_json(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params, doseq=True)
        req = urllib.request.Request(url, headers=self._headers())
        for attempt in range(3):
            try:
                with _OPENER_PLAIN.open(req, timeout=TIMEOUT) as r:
                    return json.loads(r.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", "replace")[:300]
                if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                if e.code == 401:
                    raise ApiError(
                        "401 Unauthorized : clé API refusée (vérifie COMFY_CLOUD_API_KEY)."
                    ) from None
                raise ApiError(f"HTTP {e.code} sur {path} : {body}") from None
            except urllib.error.URLError as e:
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise ApiError(f"Connexion impossible à {url} : {e.reason}") from None
        raise ApiError(f"Échec après 3 tentatives : {path}")

    def _resolve_signed_url(self, path: str, bearer: bool) -> tuple[str | None, bytes | None]:
        """
        Appelle un endpoint de téléchargement SANS suivre la redirection.
        Retourne (url_signée, None) sur 302, (None, bytes) si le serveur renvoie
        directement le fichier (200), lève ApiError sinon.
        """
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, headers=self._headers(bearer=bearer))
        try:
            with _OPENER_NO_REDIRECT.open(req, timeout=TIMEOUT) as r:
                return None, r.read()
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308):
                loc = e.headers.get("Location")
                if not loc:
                    raise ApiError(f"Redirection sans Location sur {path}") from None
                return urllib.parse.urljoin(url, loc), None
            raise ApiError(f"HTTP {e.code} sur {path}") from None
        except urllib.error.URLError as e:
            raise ApiError(f"Connexion impossible ({path}) : {e.reason}") from None

    # ---- API -------------------------------------------------------------- #
    def iter_assets(
        self,
        include_tags=None,
        exclude_tags=None,
        name_contains=None,
        include_public=False,
        sort="created_at",
        order="desc",
    ):
        offset = 0
        while True:
            params: dict = {
                "limit": PAGE_SIZE,
                "offset": offset,
                "sort": sort,
                "order": order,
                "include_public": "true" if include_public else "false",
            }
            if include_tags:
                params["include_tags"] = ",".join(include_tags)
            if exclude_tags:
                params["exclude_tags"] = ",".join(exclude_tags)
            if name_contains:
                params["name_contains"] = name_contains
            data = self._get_json("/api/assets", params)
            assets = data.get("assets", [])
            yield from assets
            if not data.get("has_more") or not assets:
                return
            offset += len(assets)

    def download_asset(self, asset: dict, dest: Path) -> str:
        """
        Télécharge un asset vers `dest`. Essaie successivement :
          1. GET /api/v2/assets/{id}/content   (Bearer)
          2. GET /api/assets/{id}/content      (X-API-Key)
          3. GET /api/view?filename=...        (X-API-Key)
        Retourne le nom de la route qui a fonctionné.
        """
        aid = asset["id"]
        name = asset["name"]
        view_params = {
            "filename": name,
            "type": (asset.get("tags") or ["output"])[0],
            "subfolder": "",
        }
        candidates = [
            ("v2/content", f"/api/v2/assets/{urllib.parse.quote(aid)}/content", True),
            ("v1/content", f"/api/assets/{urllib.parse.quote(aid)}/content", False),
            ("v1/view", "/api/view?" + urllib.parse.urlencode(view_params), False),
        ]
        last_err: Exception | None = None
        for label, path, bearer in candidates:
            try:
                signed, body = self._resolve_signed_url(path, bearer)
            except ApiError as e:
                last_err = e
                continue
            if body is not None:
                _atomic_write(dest, body)
                return label
            if signed:
                # Garde-fou : la clé n'est JAMAIS envoyée à l'hôte de stockage.
                _download_plain(signed, dest)
                return label
        raise ApiError(
            f"Aucune route de téléchargement n'a fonctionné pour {name} ({aid}) : {last_err}"
        )


def _download_plain(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})  # pas de clé ici
    tmp = dest.with_name(dest.name + ".part")
    with _OPENER_PLAIN.open(req, timeout=TIMEOUT) as r, open(tmp, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    tmp.replace(dest)


def _atomic_write(dest: Path, data: bytes) -> None:
    tmp = dest.with_name(dest.name + ".part")
    tmp.write_bytes(data)
    tmp.replace(dest)


# --------------------------------------------------------------------------- #
# Organisation locale
# --------------------------------------------------------------------------- #
_SAFE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def safe_name(name: str) -> str:
    name = _SAFE.sub("_", name).strip(" .")
    return name or "sans_nom"


def bucket_for(asset: dict) -> str:
    """Sous-dossier local : tag connu (output / input / temp / models) sinon premier tag, sinon 'autres'."""
    tags = [t for t in (asset.get("tags") or []) if t]
    for known in ("output", "input", "temp", "models"):
        if known in tags:
            return known
    return safe_name(tags[0]) if tags else "autres"


def local_path(out_dir: Path, asset: dict) -> Path:
    base = safe_name(asset["name"])
    p = out_dir / bucket_for(asset) / base
    # Collision avec un autre asset de même nom : on suffixe l'id court
    if p.exists() and not (out_dir / ".ids" / asset["id"]).exists():
        stem, suffix = os.path.splitext(base)
        p = out_dir / bucket_for(asset) / f"{stem}__{asset['id'][:8]}{suffix}"
    return p


def parse_since(s: str | None) -> datetime | None:
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    raise SystemExit(f"--since : format invalide '{s}' (attendu YYYY-MM-DD)")


def asset_dt(asset: dict) -> datetime | None:
    v = asset.get("created_at")
    if not v:
        return None
    try:
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def human(n: float) -> str:
    for unit in ("o", "Ko", "Mo", "Go", "To"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "o" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} Po"


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):  # accents corrects dans la console Windows
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--list", action="store_true", help="inventaire seulement, aucun téléchargement")
    ap.add_argument(
        "--out", help=f"dossier de destination (défaut : $COMFY_CLOUD_OUT_DIR ou ./{DEFAULT_OUT_DIR})"
    )
    ap.add_argument(
        "--tag", action="append", default=[], metavar="TAG",
        help="ne garder que les assets portant ce tag (répétable, ex: --tag output)",
    )
    ap.add_argument(
        "--exclude-tag", action="append", default=[], metavar="TAG",
        help="exclure les assets portant ce tag (répétable, ex: --exclude-tag models)",
    )
    ap.add_argument("--name", metavar="TEXTE", help="filtre : nom contenant TEXTE (insensible à la casse)")
    ap.add_argument("--since", metavar="YYYY-MM-DD", help="ne garder que les assets créés depuis cette date")
    ap.add_argument("--max", type=int, metavar="N", help="s'arrêter après N assets (les plus récents d'abord)")
    ap.add_argument("--include-public", action="store_true", help="inclure les assets publics/partagés")
    ap.add_argument("--workers", type=int, default=4, help="téléchargements en parallèle (défaut 4)")
    ap.add_argument("--force", action="store_true", help="re-télécharger même si le fichier existe déjà")
    ap.add_argument("--env", default=str(REPO_ROOT / ".env"), help="chemin du fichier .env")
    args = ap.parse_args(argv)

    load_dotenv(Path(args.env))
    api_key = os.environ.get("COMFY_CLOUD_API_KEY", "").strip()
    if not api_key or api_key.startswith("comfyui-xxxx"):
        print(
            "ERREUR : COMFY_CLOUD_API_KEY manquante. Copie .env.example en .env et colle ta clé.",
            file=sys.stderr,
        )
        return 2
    base_url = os.environ.get("COMFY_CLOUD_BASE_URL", DEFAULT_BASE_URL).strip() or DEFAULT_BASE_URL
    out_dir = Path(
        args.out or os.environ.get("COMFY_CLOUD_OUT_DIR") or (REPO_ROOT / DEFAULT_OUT_DIR)
    ).expanduser()

    api = ComfyCloud(api_key, base_url)
    since = parse_since(args.since)

    # ---- inventaire ------------------------------------------------------- #
    print(f"Inventaire des assets sur {base_url} …", file=sys.stderr)
    assets: list[dict] = []
    try:
        for a in api.iter_assets(
            include_tags=args.tag or None,
            exclude_tags=args.exclude_tag or None,
            name_contains=args.name,
            include_public=args.include_public,
        ):
            dt = asset_dt(a)
            if since and dt and dt < since:
                break  # tri created_at desc : tout ce qui suit est plus ancien
            assets.append(a)
            if args.max and len(assets) >= args.max:
                break
    except ApiError as e:
        print(f"ERREUR : {e}", file=sys.stderr)
        return 1

    total_size = sum(int(a.get("size") or 0) for a in assets)
    print(f"{len(assets)} asset(s), {human(total_size)}", file=sys.stderr)

    if args.list:
        print(f"{'date':<17} {'taille':>10}  {'tags':<22} nom")
        for a in assets:
            dt = asset_dt(a)
            print(
                f"{dt.strftime('%Y-%m-%d %H:%M') if dt else '?':<17} "
                f"{human(int(a.get('size') or 0)):>10}  "
                f"{','.join(a.get('tags') or [])[:22]:<22} {a['name']}"
            )
        return 0

    if not assets:
        return 0

    # ---- téléchargement --------------------------------------------------- #
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / ".ids").mkdir(exist_ok=True)
    manifest_path = out_dir / "manifest.json"
    manifest: dict[str, dict] = {}
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = {}

    todo: list[tuple[dict, Path]] = []
    skipped = 0
    for a in assets:
        dest = local_path(out_dir, a)
        if not args.force and dest.exists() and dest.stat().st_size == int(a.get("size") or -1):
            skipped += 1
            manifest.setdefault(a["id"], {**a, "local_path": str(dest.relative_to(out_dir))})
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        todo.append((a, dest))

    print(f"{skipped} déjà présent(s), {len(todo)} à télécharger → {out_dir}", file=sys.stderr)

    ok = failed = 0
    done_bytes = 0

    def work(item):
        a, dest = item
        route = api.download_asset(a, dest)
        (out_dir / ".ids" / a["id"]).touch()
        return a, dest, route

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        futures = {ex.submit(work, it): it for it in todo}
        for fut in as_completed(futures):
            a, dest = futures[fut]
            try:
                a, dest, route = fut.result()
                ok += 1
                size = int(a.get("size") or 0)
                done_bytes += size
                manifest[a["id"]] = {**a, "local_path": str(dest.relative_to(out_dir)), "route": route}
                print(
                    f"  ok    [{ok + failed}/{len(todo)}] {dest.relative_to(out_dir)}  ({human(size)})",
                    file=sys.stderr,
                )
            except Exception as e:  # noqa: BLE001
                failed += 1
                print(f"  ÉCHEC [{ok + failed}/{len(todo)}] {a['name']} : {e}", file=sys.stderr)

    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"\nTerminé : {ok} téléchargé(s) ({human(done_bytes)}), {skipped} ignoré(s), {failed} échec(s).",
        file=sys.stderr,
    )
    print(f"Manifeste : {manifest_path}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
