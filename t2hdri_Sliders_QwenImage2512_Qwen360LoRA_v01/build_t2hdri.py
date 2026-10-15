#!/usr/bin/env python3
"""Builder for t2hdri_Sliders_QwenImage2512_Qwen360LoRA_v01 (ComfyUI UI-format JSON)."""
import json, sys, os

WF = "t2hdri_Sliders_QwenImage2512_Qwen360LoRA_v01"
OUT = sys.argv[1] if len(sys.argv) > 1 else f"{WF}.json"

nodes = []
links = []
_nid = [0]
_lid = [0]

def add(type_, title, pos, size, widgets=None, inputs=(), outputs=(), color=None, mode=0):
    """inputs: list of (name, type, kind) kind in {'link','widget','opt'}; outputs: list of (name,type)."""
    _nid[0] += 1
    n = {
        "id": _nid[0], "type": type_, "pos": list(pos), "size": list(size), "flags": {}, "order": 0,
        "mode": mode, "inputs": [], "outputs": [],
        "properties": {"Node name for S&R": type_},
        "widgets_values": widgets if widgets is not None else [],
    }
    for name, t, kind in inputs:
        e = {"localized_name": name, "name": name, "type": t, "link": None}
        if kind == "widget":
            e["widget"] = {"name": name}
        if kind == "opt":
            e["shape"] = 7
        if kind == "autogrow":
            e["label"] = name.split(".")[-1]
        if kind == "autogrow_opt":
            e["label"] = name.split(".")[-1]
            e["shape"] = 7
        n["inputs"].append(e)
    for name, t in outputs:
        n["outputs"].append({"localized_name": name, "name": name, "type": t, "links": []})
    if title:
        n["title"] = title
    if color:
        n["color"], n["bgcolor"] = color
    nodes.append(n)
    return n["id"]

def node(i):
    return nodes[i - 1]

def link(src, src_slot, dst, dst_name):
    _lid[0] += 1
    s = node(src); d = node(dst)
    out = s["outputs"][src_slot]
    inp = next(x for x in d["inputs"] if x["name"] == dst_name)
    assert inp["link"] is None, (dst, dst_name)
    t = out["type"]
    out["links"].append(_lid[0])
    inp["link"] = _lid[0]
    links.append([_lid[0], src, src_slot, dst, d["inputs"].index(inp), t])
    return _lid[0]

# colours (group / node)
C_CTRL = ("#223", "#335")
C_MOD = ("#323", "#535")
C_PRE = ("#233", "#355")
C_PRO = ("#332", "#553")
C_GEN = ("#223", "#335")
C_SEAM = ("#333", "#444")
C_OUT = ("#223", "#346")

# ------------------------------------------------------------------ PRESET TABLES (EN, locked)
TIME = [
    "deep night, moon as the only light source, dark navy sky full of stars, faint cold moonlight, very dark ground, silhouettes only, a few distant lights barely visible",
    "pre-dawn blue hour, sun still below the horizon, a pale orange glow along the horizon, cool blue shadowless light, dew on the ground, soft and quiet",
    "sunrise, sun disc just above the horizon, very long soft shadows, warm orange and pink light, golden rim light on edges, slight morning mist in the distance",
    "mid-morning, sun at medium height in the sky, fresh clear light, medium-long shadows, slightly cool blue sky, crisp air",
    "midday, sun very high in the sky, short shadows directly under objects, neutral white light, bright sky, high contrast",
    "mid-afternoon, sun at medium height in the sky, warm neutral light, medium shadows, slightly warm sky",
    "golden hour before sunset, sun disc low above the horizon, very long shadows, warm amber and gold light, glowing backlit foliage",
    "dusk blue hour after sunset, sun just below the horizon, fading orange band along the horizon, deep blue sky above, soft cool light, first stars, lamps starting to glow",
]
TIME_LABELS = ["0 nuit", "1 aube (avant lever)", "2 lever du soleil", "3 matin", "4 midi", "5 après-midi", "6 golden hour", "7 crépuscule"]

SEASON = [
    "spring season, fresh light-green young foliage, blossoming trees, lush green grass with wild flowers, damp dark soil, puddles, soft clear air, mild light",
    "summer season, dense deep-green mature foliage, tall dry grass turning yellow, sun-baked dusty ground, hard bright light, warm haze on the horizon, heat shimmer in the distance",
    "autumn season, foliage in orange, red and yellow, fallen leaves covering the ground, wet dark soil, low warm sun, thin mist in the distance, soft golden light",
    "winter season, bare leafless trees, dormant brown grass, frost and patches of snow on the ground, pale low sun, cold blue-grey light, long shadows, crisp clear cold air",
]
SEASON_LABELS = ["0 printemps", "1 été", "2 automne", "3 hiver"]

CLOUDS = {
 "spring": [
    "completely clear deep-blue spring sky, sun disc fully visible, crisp shadows",
    "a few small white cumulus clouds scattered in a blue spring sky, sun fully visible, sharp shadows",
    "scattered fair-weather cumulus clouds covering half the spring sky, sun mostly visible, shadows slightly softened",
    "broken cloud layer of spring showers, grey and white cumulus covering most of the sky, sun disc hidden behind the clouds, soft diffuse light, bright gaps",
    "fully overcast grey spring sky, flat diffuse light, sun disc hidden, wet glistening ground, light drizzle in the air",
 ],
 "summer": [
    "flawless clear deep-blue summer sky, sun disc fully visible, hard crisp shadows, strong contrast",
    "a few small puffy white cumulus in a deep-blue summer sky, sun fully visible, hard shadows",
    "scattered puffy cumulus clouds over half the summer sky, warm hazy horizon, sun mostly visible",
    "large towering cumulus and cumulonimbus covering most of the summer sky, dramatic contrast between bright cloud tops and shadowed bases, sun disc hidden, patches of sunlight on the ground",
    "heavy overcast summer sky, dark grey storm clouds, flat dim light, sun disc hidden, humid heavy air, threatening thunderstorm",
 ],
 "autumn": [
    "clear pale-blue autumn sky, sun disc fully visible, low golden light, long soft shadows",
    "a few thin wispy cirrus clouds in a pale-blue autumn sky, sun fully visible",
    "scattered altocumulus clouds over half the autumn sky, sun visible through gaps, soft golden shadows, haze on the horizon",
    "broken grey stratocumulus covering most of the autumn sky, sun disc hidden, soft diffuse golden-grey light, low mist in the distance",
    "fully overcast grey autumn sky, flat diffuse light, sun disc hidden, wet dark ground, mist and drizzle",
 ],
 "winter": [
    "clear cold winter sky, very pale blue, low sun disc fully visible, long sharp shadows, crisp air",
    "a few thin high clouds in a pale winter sky, low sun fully visible, long shadows",
    "scattered grey-white clouds over half the winter sky, low sun visible through gaps, soft long shadows",
    "broken low grey stratus covering most of the winter sky, sun disc hidden, dim flat cold light",
    "heavy uniform overcast winter sky, flat white-grey light, sun disc hidden, snow-laden clouds, light falling snow, dim and cold",
 ],
}
HEIGHT = [
    "captured from human eye level, about 1.8 metres above the ground, grass and ground texture close and detailed in the lower half, horizon exactly at mid-height, objects nearby at their natural scale",
    "captured from about 30 metres above the ground, rooftop or low drone altitude, the ground recedes below with rooftops, treetops and paths seen from above, the horizon still exactly at mid-height, buildings and trees appear small, aerial perspective",
    "captured from about 100 metres above the ground, high drone altitude, the whole landscape laid out far below, roads and buildings tiny, the horizon exactly at mid-height, strong aerial perspective, distant haze, open sky dominates",
]
HEIGHT_LABELS = ["0 hauteur d'homme (1,80 m)", "1 30 m (toit / drone bas)", "2 100 m (drone haut)"]
CLOUD_LABELS = ["0 ciel dégagé", "1 quelques nuages", "2 nuages épars", "3 ciel chargé", "4 couvert"]
CLOUD_LINES = CLOUDS["spring"] + CLOUDS["summer"] + CLOUDS["autumn"] + CLOUDS["winter"]

def fixed_table(lines):
    w = max(len(l) for l in lines)
    return "\n".join(l.ljust(w) for l in lines), w

TIME_TXT, W_T = fixed_table(TIME)
SEASON_TXT, W_S = fixed_table(SEASON)
CLOUD_TXT, W_C = fixed_table(CLOUD_LINES)
HEIGHT_TXT, W_H = fixed_table(HEIGHT)

TRIGGER = "equirectangular 360 degree panorama with equirectangular projection, photograph of"
BASE_PROMPT = ("a quiet mountain pasture above a small alpine village in the French Alps, wooden chalets with stone bases, "
               "a gravel path, pine forest on the slopes and rocky summits all around, shot on a full-frame mirrorless camera, "
               "sharp realistic photograph")
RULES360 = ("Full spherical outdoor view, straight horizon in the exact middle, seamless left and right edges, "
            "continuous sky at the top, continuous ground at the bottom, one single coherent place with the same lighting, sun direction, "
            "weather, colours and time of day everywhere. Sharp photographic detail, natural textures on grass, foliage, bark and walls, "
            "realistic daylight and shadows, real camera photograph, not an illustration, not a 3D render. No people, no text, no frame, no vignette.")
NEG = ("illustration, cartoon, drawing, painting, anime, 3d render, cgi, video game, flat colors, cel shading, smooth plastic surfaces, "
       "oversaturated, blurry, text, watermark, frame")
PRESET_PHOTO = ("professional architectural and landscape photography, neutral colour grading, natural dynamic range, fine film grain, "
                "accurate perspective, sharp from near to far")

# ------------------------------------------------------------------ NOTE
MANUAL = f"""# {WF} — Mode d'emploi

**Environment map extérieure 360° (équirectangulaire 2:1) à partir d'un prompt texte** + 4 barrettes verrouillées : **heure de la journée**, **saison**, **nuages**, **hauteur de prise de vue**. Qwen-Image-2512 + LoRA *qwen-360-diffusion* génère la sphère complète en 2048 × 1024, raccord gauche/droite optionnel, upscale ×4 puis **4096 × 2048** exact. Sorties : **PNG 16 bits** + **EXR 32 bits float**. Comfy Cloud, **100 % nœuds natifs**.

Dérivé de `i2hdri_4Input_QwenImage2512_Qwen25VL_v07` : plus de photos, plus de Qwen2.5-VL, plus d'esquisse, **plus de passe 2** (elle lissait vers un rendu dessiné).

## Entrées
1. **✏️ Prompt de base (EN)** — uniquement : *type d'environnement / style, lieu, type de caméra ou boîtier*. Ne pas y mettre l'heure, la saison ni la météo : les barrettes s'en chargent (et l'emporteraient en cas de contradiction).
2. **🎛️ Heure (0–7)** : 0 nuit · 1 aube · 2 lever du soleil · 3 matin · 4 midi · 5 après-midi · 6 golden hour · 7 crépuscule. Règle la **hauteur** du soleil, la couleur de la lumière et la longueur des ombres. **Le LoRA 360 place le soleil près du centre du pano** quelle que soit la consigne : l'orientation réelle se fait dans Blender (Mapping, rotation Z) ou avec l'add-on *Sun Position*.
3. **🎛️ Saison (0–3)** : 0 printemps · 1 été · 2 automne · 3 hiver. Végétation, état du sol, qualité de lumière.
4. **🎛️ Nuages (0–4)** : 0 dégagé · 1 quelques nuages · 2 épars · 3 chargé · 4 couvert. **Pondéré par la saison** : la table contient 4 × 5 = 20 descriptions (cumulus d'été, stratus bas d'hiver…).
5. **🎛️ Hauteur de prise de vue (0–2)** : 0 hauteur d'homme (1,80 m) · 1 ≈ 30 m (toit, drone bas) · 2 ≈ 100 m (drone haut). L'horizon reste au milieu (équirectangulaire), c'est le sol qui s'éloigne. Le LoRA 360 est surtout entraîné au sol : au-dessus de 30 m, résultat plus variable, essayer plusieurs seeds.

Les textes des barrettes sont **verrouillés** dans le groupe *PRESETS* (tables à largeur fixe, lues par position). Ne pas les éditer à la main : une ligne plus longue que les autres décale toute la table. Pour les changer, régénérer le WF.

## Pipeline
1. **Presets** — chaque barrette (entier) → `Math Expression` calcule la position dans la table → `Substring` → `Trim`.
2. **Prompt** — trigger LoRA 360 + prompt de base + « Time of day: … » + « Season: … » + « Sky: … » + « Camera height: … » + consignes 360 fixes. **👁️ Prompt assemblé** montre le texte final.
3. **Génération** — latent vide 2048 × 1024 (`EmptySD3LatentImage`), KSampler denoise 1.0.
4. **Raccord gauche/droite** (option, ON) — décalage 180°, bande de 256 px repeinte, remise en place.
5. **Upscale** ×4 RealESRGAN → **4096 × 2048** exact.
6. **Sauvegarde** — PNG 16 bits (sRGB) + EXR 32 bits float (linéaire Rec.709).

## Réglages
- **Mode rapide (défaut)** : LoRA Lightning, **🎛️ Steps** 8, CFG 1 (prompt négatif sans effet, éviter les formulations négatives dans le prompt de base).
- **🎛️ Mode QUALITÉ** (ON) : sans Lightning, **🎛️ Steps mode QUALITÉ** 30, **🎛️ CFG mode QUALITÉ** 3 → négatif anti-illustration actif. 4 à 6 fois plus long. S'applique à la génération et au raccord.
- **🎛️ Raccord** 0.5–0.7 : monter si un élément fort traverse les bords (Sud).
- **🎛️ Seed** : changer pour une autre interprétation du même brief.
- **➕ Rendu photo pro** : preset de style bypassé par défaut (Ctrl+B pour l'activer).

## Modèles
- `diffusion_models/qwen_image_2512_fp8_e4m3fn.safetensors`
- `loras/Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors`
- `loras/qwen-360-diffusion-2512-int8-bf16-v2.safetensors`
- `text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors` · `vae/qwen_image_vae.safetensors`
- `upscale_models/RealESRGAN_x4plus.pth`

## Limites
- **Pas un vrai HDRI** : génération LDR, l'EXR est linéaire mais le soleil ne dépasse pas 1. Monter *Strength* du World ou ajouter une *Sun lamp* (add-on Blender *Sun Position* : lat/long + date + heure → soleil exact).
- **Soleil au centre** : testé, le modèle ignore les consignes de point cardinal (Est / Sud / bords) et met le soleil vers le centre de l'image ; les presets ne demandent donc que la hauteur. Tourner le HDRI en Z (Mapping) dans Blender pour l'orienter ; les ombres de l'image restent cohérentes avec le soleil.
- Zénith / nadir souvent flous ou étirés.
- Nuit (Heure 0) : le LoRA 360 est surtout entraîné sur du jour ; résultat variable.
- `Save Image (Advanced)` : vérifier les menus *format* / *bit_depth* au chargement.
"""

# ================================================================== NODES
add("MarkdownNote", "📖 Mode d'emploi", (40, 40), (520, 1900), [MANUAL])

# ---- 🎛️ CONTRÔLES  x 600..960
cx, y = 620, 60
def ctrl(type_, title, widgets, h):
    global y
    i = add(type_, title, (cx, y), (320, h), widgets, outputs=[(type_.replace("Primitive", "").upper(), type_.replace("Primitive", "").upper())], color=C_CTRL)
    y += h + 30
    return i
N_BASE = add("PrimitiveStringMultiline", "✏️ Prompt de base (EN) : style d'environnement, lieu, boîtier / caméra", (cx, y), (320, 240), [BASE_PROMPT], outputs=[("STRING", "STRING")], color=C_PRO)
y += 240 + 30
N_TIME   = ctrl("PrimitiveInt", "🎛️ Heure (0–7) : 0 nuit · 2 lever · 4 midi · 6 golden hour", [4, "fixed"], 82)
N_SEASON = ctrl("PrimitiveInt", "🎛️ Saison (0–3) : printemps · été · automne · hiver", [1, "fixed"], 82)
N_CLOUD  = ctrl("PrimitiveInt", "🎛️ Nuages (0–4) : dégagé → couvert (pondéré saison)", [1, "fixed"], 82)
N_HEIGHT = ctrl("PrimitiveInt", "🎛️ Hauteur de prise de vue (0–2) : 1,80 m · 30 m · 100 m", [0, "fixed"], 82)
N_SEED   = ctrl("PrimitiveInt", "🎛️ Seed", [360001, "fixed"], 82)
N_STEPS  = ctrl("PrimitiveInt", "🎛️ Steps (8 conseillé, 6–10)", [8, "fixed"], 82)
N_SEAMON = ctrl("PrimitiveBoolean", "🎛️ Raccord gauche/droite (seam fix)", [True], 58)
N_SEAMDN = ctrl("PrimitiveFloat", "🎛️ Raccord (denoise bande, 0.5–0.7)", [0.6], 58)
N_QUAL   = ctrl("PrimitiveBoolean", "🎛️ Mode QUALITÉ (sans Lightning, lent)", [False], 58)
N_STEPSQ = ctrl("PrimitiveInt", "🎛️ Steps mode QUALITÉ (25–40)", [30, "fixed"], 82)
N_CFGQ   = ctrl("PrimitiveFloat", "🎛️ CFG mode QUALITÉ (2.5–4)", [3.0], 58)
N_CFGL   = ctrl("PrimitiveFloat", "CFG mode Lightning (laisser 1.0)", [1.0], 58)
CTRL_H = y

# ---- MODÈLES  x 1000..1400 (same as v07)
mx = 1020
N_UNET = add("UNETLoader", "Qwen-Image-2512 (diffusion)", (mx, 60), (360, 82), ["qwen_image_2512_fp8_e4m3fn.safetensors", "default"], outputs=[("MODEL", "MODEL")], color=C_MOD)
N_LORA_L = add("LoraLoaderModelOnly", "LoRA Lightning 2512 — 4 steps", (mx, 180), (360, 82), ["Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors", 1.0], inputs=[("model", "MODEL", "link")], outputs=[("MODEL", "MODEL")], color=C_MOD)
N_LORA_360 = add("LoraLoaderModelOnly", "LoRA qwen-360-diffusion 2512 v2", (mx, 300), (360, 82), ["qwen-360-diffusion-2512-int8-bf16-v2.safetensors", 1.0], inputs=[("model", "MODEL", "link")], outputs=[("MODEL", "MODEL")], color=C_MOD)
N_AURA = add("ModelSamplingAuraFlow", "", (mx, 420), (360, 58), [3.1], inputs=[("model", "MODEL", "link")], outputs=[("MODEL", "MODEL")], color=C_MOD)
N_CLIP = add("CLIPLoader", "Text encoder Qwen2.5-VL 7B", (mx, 520), (360, 106), ["qwen_2.5_vl_7b_fp8_scaled.safetensors", "qwen_image", "default"], outputs=[("CLIP", "CLIP")], color=C_MOD)
N_VAE = add("VAELoader", "VAE Qwen Image", (mx, 660), (360, 58), ["qwen_image_vae.safetensors"], outputs=[("VAE", "VAE")], color=C_MOD)
N_UPM = add("UpscaleModelLoader", "Upscale ×4", (mx, 760), (360, 58), ["RealESRGAN_x4plus.pth"], outputs=[("UPSCALE_MODEL", "UPSCALE_MODEL")], color=C_MOD)
N_LORA_360Q = add("LoraLoaderModelOnly", "LoRA qwen-360-diffusion (mode QUALITÉ, sans Lightning)", (mx, 860), (360, 82), ["qwen-360-diffusion-2512-int8-bf16-v2.safetensors", 1.0], inputs=[("model", "MODEL", "link")], outputs=[("MODEL", "MODEL")], color=C_MOD)
N_AURAQ = add("ModelSamplingAuraFlow", "AuraFlow (mode QUALITÉ)", (mx, 980), (360, 58), [3.1], inputs=[("model", "MODEL", "link")], outputs=[("MODEL", "MODEL")], color=C_MOD)
def switch(title, pos, t, default, color):
    return add("ComfySwitchNode", title, pos, (320, 80), [default], inputs=[("on_false", t, "opt"), ("on_true", t, "opt"), ("switch", "BOOLEAN", "widget")], outputs=[("output", t)], color=color)
N_SW_MODEL = switch("Modèle : Lightning / QUALITÉ", (mx, 1080), "MODEL", False, C_MOD)
N_SW_STEPS = switch("Steps : Lightning / QUALITÉ", (mx, 1190), "INT", False, C_MOD)
N_SW_CFG = switch("CFG : Lightning / QUALITÉ", (mx, 1300), "FLOAT", False, C_MOD)

link(N_UNET, 0, N_LORA_L, "model"); link(N_LORA_L, 0, N_LORA_360, "model"); link(N_LORA_360, 0, N_AURA, "model")
link(N_UNET, 0, N_LORA_360Q, "model"); link(N_LORA_360Q, 0, N_AURAQ, "model")
link(N_AURA, 0, N_SW_MODEL, "on_false"); link(N_AURAQ, 0, N_SW_MODEL, "on_true"); link(N_QUAL, 0, N_SW_MODEL, "switch")
link(N_STEPS, 0, N_SW_STEPS, "on_false"); link(N_STEPSQ, 0, N_SW_STEPS, "on_true"); link(N_QUAL, 0, N_SW_STEPS, "switch")
link(N_CFGL, 0, N_SW_CFG, "on_false"); link(N_CFGQ, 0, N_SW_CFG, "on_true"); link(N_QUAL, 0, N_SW_CFG, "switch")

# ---- PRESETS  x 1440..2560
px_tab, px_math, px_sub = 1460, 1900, 2240
def table(title, pos, h, text):
    return add("PrimitiveStringMultiline", title, pos, (400, h), [text], outputs=[("STRING", "STRING")], color=C_PRE)
def math1(title, pos, expr):
    return add("ComfyMathExpression", title, pos, (320, 110), [expr],
               inputs=[("values.a", "FLOAT,INT,BOOLEAN", "autogrow"), ("values.b", "FLOAT,INT,BOOLEAN", "autogrow_opt")],
               outputs=[("FLOAT", "FLOAT"), ("INT", "INT"), ("BOOL", "BOOLEAN")], color=C_PRE)
def math2(title, pos, expr):
    return add("ComfyMathExpression", title, pos, (320, 130), [expr],
               inputs=[("values.a", "FLOAT,INT,BOOLEAN", "autogrow"), ("values.b", "FLOAT,INT,BOOLEAN", "autogrow"), ("values.c", "FLOAT,INT,BOOLEAN", "autogrow_opt")],
               outputs=[("FLOAT", "FLOAT"), ("INT", "INT"), ("BOOL", "BOOLEAN")], color=C_PRE)
def substr(title, pos):
    return add("StringSubstring", title, pos, (300, 150), ["", 0, 0],
               inputs=[("string", "STRING", "widget"), ("start", "INT", "widget"), ("end", "INT", "widget")], outputs=[("STRING", "STRING")], color=C_PRE)
def trim(title, pos):
    return add("StringTrim", title, pos, (300, 80), ["", "Both"], inputs=[("string", "STRING", "widget")], outputs=[("STRING", "STRING")], color=C_PRE)

def preset_block(y0, h_tab, title, text, w, n_idx, src_nodes, expr_start, expr_end):
    t = table(title, (px_tab, y0), h_tab, text)
    if len(src_nodes) == 1:
        ms = math1(f"Début = index borné × {w+1}", (px_math, y0), expr_start)
        me = math1(f"Fin = début + {w}", (px_math, y0 + 140), expr_end)
    else:
        ms = math2(f"Début = (saison × 5 + nuages) bornés × {w+1}", (px_math, y0), expr_start)
        me = math2(f"Fin = début + {w}", (px_math, y0 + 160), expr_end)
    for m in (ms, me):
        for k, s in enumerate(src_nodes):
            link(s, 0, m, "values." + "abc"[k])
    sb = substr("Ligne de la table (position)", (px_sub, y0))
    tr = trim("Texte du preset (sans remplissage)", (px_sub, y0 + 180))
    link(t, 0, sb, "string"); link(ms, 1, sb, "start"); link(me, 1, sb, "end"); link(sb, 0, tr, "string")
    return tr

N_TIME_TXT = preset_block(60, 270, "🔒 Table HEURE (8 lignes, largeur fixe — ne pas éditer)", TIME_TXT, W_T, N_TIME, [N_TIME], f"min(max(a,0),7)*{W_T+1}", f"min(max(a,0),7)*{W_T+1}+{W_T}")
N_SEASON_TXT = preset_block(380, 270, "🔒 Table SAISON (4 lignes, largeur fixe — ne pas éditer)", SEASON_TXT, W_S, N_SEASON, [N_SEASON], f"min(max(a,0),3)*{W_S+1}", f"min(max(a,0),3)*{W_S+1}+{W_S}")
N_CLOUD_TXT = preset_block(700, 400, "🔒 Table NUAGES × SAISON (20 lignes, largeur fixe — ne pas éditer)", CLOUD_TXT, W_C, N_CLOUD, [N_SEASON, N_CLOUD], f"(min(max(a,0),3)*5+min(max(b,0),4))*{W_C+1}", f"(min(max(a,0),3)*5+min(max(b,0),4))*{W_C+1}+{W_C}")

N_HEIGHT_TXT = preset_block(1140, 230, "🔒 Table HAUTEUR (3 lignes, largeur fixe — ne pas éditer)", HEIGHT_TXT, W_H, N_HEIGHT, [N_HEIGHT], f"min(max(a,0),2)*{W_H+1}", f"min(max(a,0),2)*{W_H+1}+{W_H}")

# ---- PROMPT  x 2600..3420
qx1, qx2 = 2620, 3040
N_TRIG = add("PrimitiveStringMultiline", "Trigger 360 (ne pas modifier)", (qx1, 60), (380, 110), [TRIGGER], outputs=[("STRING", "STRING")], color=C_PRO)
N_RULES = add("PrimitiveStringMultiline", "Consignes 360 (EN, fixes)", (qx1, 210), (380, 220), [RULES360], outputs=[("STRING", "STRING")], color=C_PRO)
N_NEG = add("CLIPTextEncode", "Négatif (actif seulement en mode QUALITÉ, CFG > 1)", (qx1, 470), (380, 120), [NEG], inputs=[("clip", "CLIP", "link")], outputs=[("CONDITIONING", "CONDITIONING")], color=C_PRO)
N_PREV_PROMPT = add("PreviewAny", "👁️ Prompt assemblé", (qx1, 630), (380, 320), [], inputs=[("source", "*", "link")], color=C_PRO)

def concat(title, pos, delim, mode=0, b_widget=""):
    return add("StringConcatenate", title, pos, (340, 150), ["", b_widget, delim],
               inputs=[("string_a", "STRING", "widget"), ("string_b", "STRING", "widget")], outputs=[("STRING", "STRING")], color=C_PRO, mode=mode)
N_C1 = concat("Trigger + prompt de base", (qx2, 60), " ")
N_C2 = concat("+ Heure (barrette)", (qx2, 240), ". Time of day: ")
N_C3 = concat("+ Saison (barrette)", (qx2, 420), ". Season: ")
N_C4 = concat("+ Nuages (barrette)", (qx2, 600), ". Sky: ")
N_C4b = concat("+ Hauteur de prise de vue (barrette)", (qx2, 780), ". Camera height: ")
N_C5 = concat("➕ Rendu photo pro (OFF — Ctrl+B pour activer)", (qx2, 960), ". ", mode=4, b_widget=PRESET_PHOTO)
N_C6 = concat("+ Consignes 360", (qx2, 1140), "\n\n")
N_POS = add("CLIPTextEncode", "PROMPT 360 (positif)", (qx2, 1320), (340, 100), [""], inputs=[("clip", "CLIP", "link"), ("text", "STRING", "widget")], outputs=[("CONDITIONING", "CONDITIONING")], color=C_PRO)

link(N_TRIG, 0, N_C1, "string_a"); link(N_BASE, 0, N_C1, "string_b")
link(N_C1, 0, N_C2, "string_a"); link(N_TIME_TXT, 0, N_C2, "string_b")
link(N_C2, 0, N_C3, "string_a"); link(N_SEASON_TXT, 0, N_C3, "string_b")
link(N_C3, 0, N_C4, "string_a"); link(N_CLOUD_TXT, 0, N_C4, "string_b")
link(N_C4, 0, N_C4b, "string_a"); link(N_HEIGHT_TXT, 0, N_C4b, "string_b")
link(N_C4b, 0, N_C5, "string_a")            # string_b stays a widget (preset text)
link(N_C5, 0, N_C6, "string_a"); link(N_RULES, 0, N_C6, "string_b")
link(N_C6, 0, N_PREV_PROMPT, "source"); link(N_C6, 0, N_POS, "text")
link(N_CLIP, 0, N_POS, "clip"); link(N_CLIP, 0, N_NEG, "clip")

# ---- GÉNÉRATION  x 3460..3840
gx = 3480
N_LAT = add("EmptySD3LatentImage", "Latent vide 2048 × 1024 (taille native LoRA 360)", (gx, 60), (340, 130), [2048, 1024, 1], outputs=[("LATENT", "LATENT")], color=C_GEN)
def ksampler(title, pos, denoise):
    return add("KSampler", title, pos, (320, 262), [360001, "fixed", 8, 1.0, "euler", "simple", denoise],
               inputs=[("model", "MODEL", "link"), ("positive", "CONDITIONING", "link"), ("negative", "CONDITIONING", "link"), ("latent_image", "LATENT", "link"),
                       ("seed", "INT", "widget"), ("steps", "INT", "widget"), ("cfg", "FLOAT", "widget"), ("denoise", "FLOAT", "widget")],
               outputs=[("LATENT", "LATENT")], color=C_GEN)
N_KS = ksampler("KSampler — GÉNÉRATION 360° (txt2img, denoise 1.0)", (gx, 230), 1.0)
N_DEC = add("VAEDecode", "", (gx, 530), (300, 46), [], inputs=[("samples", "LATENT", "link"), ("vae", "VAE", "link")], outputs=[("IMAGE", "IMAGE")], color=C_GEN)
N_PREV_GEN = add("PreviewImage", "👁️ Génération 2048 × 1024", (gx, 610), (340, 240), [], inputs=[("images", "IMAGE", "link")], color=C_GEN)
link(N_LAT, 0, N_KS, "latent_image"); link(N_SW_MODEL, 0, N_KS, "model"); link(N_POS, 0, N_KS, "positive"); link(N_NEG, 0, N_KS, "negative")
link(N_SEED, 0, N_KS, "seed"); link(N_SW_STEPS, 0, N_KS, "steps"); link(N_SW_CFG, 0, N_KS, "cfg")
link(N_KS, 0, N_DEC, "samples"); link(N_VAE, 0, N_DEC, "vae"); link(N_DEC, 0, N_PREV_GEN, "images")

# ---- RACCORD  x 3880..4580 (from v07)
sx1, sx2 = 3900, 4240
def crop(title, pos, w, h, x, y_):
    return add("ImageCrop", title, pos, (300, 130), [w, h, x, y_], inputs=[("image", "IMAGE", "link")], outputs=[("IMAGE", "IMAGE")], color=C_SEAM)
N_CR_R = crop("Moitié droite", (sx1, 60), 1024, 1024, 1024, 0)
N_CR_L = crop("Moitié gauche", (sx1, 220), 1024, 1024, 0, 0)
N_ST1 = add("ImageStitch", "Décalage 180° (raccord au centre)", (sx1, 380), (300, 150), ["right", False, 0, "white"], inputs=[("image1", "IMAGE", "link"), ("image2", "IMAGE", "opt")], outputs=[("IMAGE", "IMAGE")], color=C_SEAM)
N_SM0 = add("SolidMask", "Masque vide 2048 × 1024", (sx1, 560), (300, 106), [0.0, 2048, 1024], outputs=[("MASK", "MASK")], color=C_SEAM)
N_SM1 = add("SolidMask", "Bande 256 px", (sx1, 700), (300, 106), [1.0, 256, 1024], outputs=[("MASK", "MASK")], color=C_SEAM)
N_MC = add("MaskComposite", "Bande au centre (x 896)", (sx1, 840), (300, 130), [896, 0, "add"], inputs=[("destination", "MASK", "link"), ("source", "MASK", "link")], outputs=[("MASK", "MASK")], color=C_SEAM)
N_M2I = add("MaskToImage", "", (sx1, 1010), (300, 26), [], inputs=[("mask", "MASK", "link")], outputs=[("IMAGE", "IMAGE")], color=C_SEAM)
N_BLUR = add("ImageBlur", "Fondu de la bande", (sx1, 1070), (300, 82), [31, 10.0], inputs=[("image", "IMAGE", "link")], outputs=[("IMAGE", "IMAGE")], color=C_SEAM)
N_I2M = add("ImageToMask", "", (sx1, 1190), (300, 58), ["red"], inputs=[("image", "IMAGE", "link"), ], outputs=[("MASK", "MASK")], color=C_SEAM)
N_ENC = add("VAEEncode", "", (sx2, 60), (300, 46), [], inputs=[("pixels", "IMAGE", "link"), ("vae", "VAE", "link")], outputs=[("LATENT", "LATENT")], color=C_SEAM)
N_SNM = add("SetLatentNoiseMask", "", (sx2, 150), (300, 46), [], inputs=[("samples", "LATENT", "link"), ("mask", "MASK", "link")], outputs=[("LATENT", "LATENT")], color=C_SEAM)
N_KS2 = ksampler("KSampler — RACCORD (bande centrale)", (sx2, 240), 0.6)
N_DEC2 = add("VAEDecode", "", (sx2, 540), (300, 46), [], inputs=[("samples", "LATENT", "link"), ("vae", "VAE", "link")], outputs=[("IMAGE", "IMAGE")], color=C_SEAM)
N_COMP = add("ImageCompositeMasked", "Colle la bande seule", (sx2, 630), (300, 150), [0, 0, False], inputs=[("destination", "IMAGE", "link"), ("source", "IMAGE", "link"), ("mask", "MASK", "opt")], outputs=[("IMAGE", "IMAGE")], color=C_SEAM)
N_CR_R2 = crop("Moitié droite", (sx2, 820), 1024, 1024, 1024, 0)
N_CR_L2 = crop("Moitié gauche", (sx2, 980), 1024, 1024, 0, 0)
N_ST2 = add("ImageStitch", "Remise en place (−180°)", (sx2, 1140), (300, 150), ["right", False, 0, "white"], inputs=[("image1", "IMAGE", "link"), ("image2", "IMAGE", "opt")], outputs=[("IMAGE", "IMAGE")], color=C_SEAM)
N_SW_SEAM = switch("Raccord : OFF / ON", (sx2, 1330), "IMAGE", True, C_SEAM)

link(N_DEC, 0, N_CR_R, "image"); link(N_DEC, 0, N_CR_L, "image")
link(N_CR_R, 0, N_ST1, "image1"); link(N_CR_L, 0, N_ST1, "image2")
link(N_SM0, 0, N_MC, "destination"); link(N_SM1, 0, N_MC, "source"); link(N_MC, 0, N_M2I, "mask"); link(N_M2I, 0, N_BLUR, "image"); link(N_BLUR, 0, N_I2M, "image")
link(N_ST1, 0, N_ENC, "pixels"); link(N_VAE, 0, N_ENC, "vae"); link(N_ENC, 0, N_SNM, "samples"); link(N_I2M, 0, N_SNM, "mask")
link(N_SNM, 0, N_KS2, "latent_image"); link(N_SW_MODEL, 0, N_KS2, "model"); link(N_POS, 0, N_KS2, "positive"); link(N_NEG, 0, N_KS2, "negative")
link(N_SEED, 0, N_KS2, "seed"); link(N_SW_STEPS, 0, N_KS2, "steps"); link(N_SW_CFG, 0, N_KS2, "cfg"); link(N_SEAMDN, 0, N_KS2, "denoise")
link(N_KS2, 0, N_DEC2, "samples"); link(N_VAE, 0, N_DEC2, "vae")
link(N_ST1, 0, N_COMP, "destination"); link(N_DEC2, 0, N_COMP, "source"); link(N_I2M, 0, N_COMP, "mask")
link(N_COMP, 0, N_CR_R2, "image"); link(N_COMP, 0, N_CR_L2, "image"); link(N_CR_R2, 0, N_ST2, "image1"); link(N_CR_L2, 0, N_ST2, "image2")
link(N_DEC, 0, N_SW_SEAM, "on_false"); link(N_ST2, 0, N_SW_SEAM, "on_true"); link(N_SEAMON, 0, N_SW_SEAM, "switch")

# ---- SORTIE  x 4620..5160
ox = 4640
N_UP = add("ImageUpscaleWithModel", "Upscale ×4 (8192 × 4096)", (ox, 60), (320, 46), [], inputs=[("upscale_model", "UPSCALE_MODEL", "link"), ("image", "IMAGE", "link")], outputs=[("IMAGE", "IMAGE")], color=C_OUT)
N_SC = add("ImageScale", "→ 4096 × 2048 exact", (ox, 150), (320, 130), ["lanczos", 4096, 2048, "disabled"], inputs=[("image", "IMAGE", "link")], outputs=[("IMAGE", "IMAGE")], color=C_OUT)
N_SAVE_PNG = add("SaveImageAdvanced", "💾 Pano 4K — PNG 16 bits (sRGB)", (ox, 320), (360, 200), [f"{WF}/pano_png16", "png", "16-bit", "sRGB"], inputs=[("images", "IMAGE", "link")], color=C_OUT)
N_SAVE_EXR = add("SaveImageAdvanced", "💾 Pano 4K — EXR 32 bits float (linéaire)", (ox, 560), (360, 200), [f"{WF}/pano_exr32", "exr", "32-bit float", "sRGB"], inputs=[("images", "IMAGE", "link")], color=C_OUT)
N_PREV_FIN = add("PreviewImage", "👁️ Pano final", (ox, 800), (480, 300), [], inputs=[("images", "IMAGE", "link")], color=C_OUT)
link(N_UPM, 0, N_UP, "upscale_model"); link(N_SW_SEAM, 0, N_UP, "image"); link(N_UP, 0, N_SC, "image")
link(N_SC, 0, N_SAVE_PNG, "images"); link(N_SC, 0, N_SAVE_EXR, "images"); link(N_SC, 0, N_PREV_FIN, "images")

# ================================================================== GROUPS
groups = [
    {"id": 1, "title": "🎛️ CONTRÔLES", "bounding": [600, 0, 360, CTRL_H + 10], "color": "#335", "font_size": 24, "flags": {}},
    {"id": 2, "title": "MODÈLES", "bounding": [1000, 0, 400, 1420], "color": "#535", "font_size": 24, "flags": {}},
    {"id": 3, "title": "PRESETS VERROUILLÉS — heure / saison / nuages (tables à largeur fixe, lues par position)", "bounding": [1440, 0, 1120, 1420], "color": "#355", "font_size": 24, "flags": {}},
    {"id": 4, "title": "PROMPT — trigger + prompt de base + barrettes + consignes 360", "bounding": [2600, 0, 820, 1460], "color": "#553", "font_size": 24, "flags": {}},
    {"id": 5, "title": "GÉNÉRATION — Qwen-Image-2512 + LoRA 360 (txt2img 2048 × 1024)", "bounding": [3460, 0, 380, 890], "color": "#335", "font_size": 24, "flags": {}},
    {"id": 6, "title": "RACCORD GAUCHE / DROITE (option)", "bounding": [3880, 0, 700, 1460], "color": "#444", "font_size": 24, "flags": {}},
    {"id": 7, "title": "SORTIE — 4096×2048 PNG16 + EXR32", "bounding": [4620, 0, 540, 1140], "color": "#346", "font_size": 24, "flags": {}},
]

# ================================================================== ORDER (topological)
deps = {n["id"]: set() for n in nodes}
for l in links:
    deps[l[3]].add(l[1])
order, seen = [], set()
def visit(i):
    if i in seen: return
    seen.add(i)
    for d in sorted(deps[i]): visit(d)
    order.append(i)
for n in nodes: visit(n["id"])
for k, i in enumerate(order): node(i)["order"] = k

wf = {
    "id": "t2hdri-sliders-qwenimage2512-qwen360lora-v01",
    "revision": 0,
    "last_node_id": _nid[0], "last_link_id": _lid[0],
    "nodes": nodes, "links": links, "groups": groups,
    "config": {}, "extra": {"ds": {"scale": 0.35, "offset": [0, 120]}, "workflow_name": WF}, "version": 0.4,
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=1)
print("written", OUT, "nodes", len(nodes), "links", len(links), "W_T W_S W_C", W_T, W_S, W_C)
json.dump({"TIME": TIME, "SEASON": SEASON, "CLOUDS": CLOUDS, "HEIGHT": HEIGHT, "TIME_LABELS": TIME_LABELS, "SEASON_LABELS": SEASON_LABELS, "CLOUD_LABELS": CLOUD_LABELS},
          open(os.path.join(os.path.dirname(OUT) or ".", "presets.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
