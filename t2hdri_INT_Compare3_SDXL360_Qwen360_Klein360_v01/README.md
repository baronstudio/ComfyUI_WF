# t2hdri_INT_Compare3_SDXL360_Qwen360_Klein360_v01

**En une phrase** : banc d'essai qualité pour l'**environment map INTÉRIEURE 360°** (équirectangulaire 2048 × 1024) — trois solutions de génération en parallèle (SDXL 360 Diffusion, Qwen-Image-2512 + qwen-360-diffusion, Flux.2 Klein 9B base + LoRA 360) alimentées par **le même prompt, les mêmes barrettes, la même seed et la même résolution**, pour choisir celle qu'on fiabilise en v1. 100 % nœuds natifs.

> Étape 1 du plan : comparer → étape 2 : choix du modèle → étape 3 : WF final (raccord gauche/droite, upscale ×4 → 4096 × 2048, PNG 16 bits + EXR 32 bits, boost HDR des fenêtres). Ces étapes aval ne sont **pas** dans ce fichier.

## Pipeline

1. **Presets verrouillés** — chaque barrette (`PrimitiveInt`) → `Math Expression` (index borné) → `Substring` sur table à largeur fixe → `Trim`. Lumière = Ambiance × Ensoleillement (16 lignes) ; Style déco = 15 styles + 1 ligne vide (actif seulement si Mobilier = 3).
2. **Prompt commun** — ✏️ prompt de base + « Lighting : … » + « Room state : … » + style + « Camera height : … » + consignes 360 intérieures fixes (`StringConcatenate`). Chaque bloc ajoute **son propre trigger** devant ce corps ; les trois prompts sont visibles dans des 👁️.
3. **Bloc A — SDXL 360 Diffusion** : checkpoint complet, LoRA View360 (360Redmond) optionnelle (OFF), KSampler `dpmpp_2m` / `karras`, négatif actif.
4. **Bloc B — Qwen-Image-2512** : Lightning + LoRA `qwen-360-diffusion` v2, AuraFlow 3.1, KSampler `euler` / `simple`, CFG 1.
5. **Bloc C — Flux.2 Klein 9B base** : LoRA 360 (crafiq), `Flux2Scheduler` + `CFGGuider` + `SamplerCustomAdvanced`, pas de négatif.
6. Chaque bloc sauvegarde son PNG (`SaveImage`) : `A_SDXL360`, `B_Qwen360`, `C_Klein360`.

## Barrettes

| Barrette | Valeurs | Ce que le preset décrit |
|---|---|---|
| 🎛️ Ambiance (0–3) | 0 matin · 1 jour · 2 soir · 3 nuit | couleur et provenance de la lumière, lampes allumées ou non |
| 🎛️ Ensoleillement (0–3) | 0 aucun soleil direct · 1 soleil doux · 2 rayons marqués · 3 contre-jour éblouissant | exposition : plus il monte, plus l'éclairage intérieur s'atténue ; pondéré par l'ambiance (16 lignes) |
| 🎛️ Mobilier (0–3) | 0 gros œuvre · 1 second œuvre · 2 vide, finitions terminées · 3 meublé et décoré | état du lieu ; aucun personnage |
| 🎛️ Style déco (0–14) | 0 moderne · 1 contemporain · 2 scandinave · 3 mid-century · 4 industriel · 5 bohème · 6 vintage · 7 art déco · 8 campagne anglaise · 9 maison de vacances · 10 wabi-sabi · 11 kinfolk · 12 haussmannien · 13 classique contemporain · 14 minimalisme chaleureux | matériaux, couleurs, mobilier (traits d'après [artmeta.fr](https://www.artmeta.fr/quels-sont-les-differents-styles-de-decoration-interieure)) ; vide si Mobilier < 3 |
| 🎛️ Hauteur (0–2) | 0 ≈ 1 m (assis) · 1 ≈ 1,6 m (debout) · 2 ≈ 2,8 m (sous plafond) | position de la caméra ; horizon toujours au milieu |

Ne pas éditer les tables (largeur fixe, lecture par position). Pour changer un texte : modifier `build_t2hdri_INT_compare.py` puis `python build_t2hdri_INT_compare.py ../t2hdri_INT_Compare3_SDXL360_Qwen360_Klein360_v01.json` et `python validate_int_compare.py ../t2hdri_INT_Compare3_SDXL360_Qwen360_Klein360_v01.json`.

## Modèles requis

| Bloc | Type | Nom exact | Source |
|---|---|---|---|
| A | Checkpoint | `sdxl_360_diffusion.safetensors` (7,11 Go) | [ProGamerGov/sdxl-360-diffusion](https://huggingface.co/ProGamerGov/sdxl-360-diffusion) (MIT) |
| A | LoRA (option) | `View360.safetensors` | [artificialguybr/360Redmond](https://huggingface.co/artificialguybr/360Redmond) (OpenRAIL-M) |
| B | Diffusion | `qwen_image_2512_fp8_e4m3fn.safetensors` | [Comfy-Org/Qwen-Image_ComfyUI](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI) |
| B | LoRA | `Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors` | [lightx2v/Qwen-Image-Lightning](https://huggingface.co/lightx2v/Qwen-Image-Lightning) |
| B | LoRA | `qwen-360-diffusion-2512-int8-bf16-v2.safetensors` | identique au WF extérieur |
| B | Text encoder / VAE | `qwen_2.5_vl_7b_fp8_scaled.safetensors` · `qwen_image_vae.safetensors` | Comfy-Org/Qwen-Image_ComfyUI |
| C | Diffusion | `flux-2-klein-base-9b-fp8.safetensors` | [black-forest-labs/FLUX.2-klein-base-9b-fp8](https://huggingface.co/black-forest-labs/FLUX.2-klein-base-9b-fp8) |
| C | LoRA | `flux-2-klein-9b-360-panorama-lora.safetensors` (331 Mo) | [crafiq/flux-2-klein-9b-360-panorama-lora](https://huggingface.co/crafiq/flux-2-klein-9b-360-panorama-lora) |
| C | Text encoder / VAE | `qwen_3_8b_fp8mixed.safetensors` · `full_encoder_small_decoder.safetensors` | [Comfy-Org/flux2-klein-9B](https://huggingface.co/Comfy-Org/flux2-klein-9B) · [FLUX.2-small-decoder](https://huggingface.co/black-forest-labs/FLUX.2-small-decoder) |

## Nodes custom

- Aucun — 100 % natifs : `CheckpointLoaderSimple`, `LoraLoader`, `UNETLoader`, `CLIPLoader`, `Flux2Scheduler`, `CFGGuider`, `SamplerCustomAdvanced`, `ComfyMathExpression`, `StringSubstring`…
- Les checkpoints / LoRA des blocs A et C (`sdxl_360_diffusion`, `View360`, LoRA crafiq) ne sont pas des modèles Comfy Cloud de base : **à importer avant le premier run** (non vérifié).

## Réglages clés

| Paramètre | Valeur | Pourquoi |
|---|---|---|
| Résolution | 2048 × 1024 sur les 3 blocs | taille native des LoRA / checkpoints 360 ; commune pour comparer |
| A — Steps / CFG | 30 / 6.0, `dpmpp_2m` / `karras` | réglage SDXL classique (la fiche du modèle n'en donne pas) |
| B — Steps / CFG | 8 / 1.0, `euler` / `simple` | mode rapide Lightning validé sur le WF extérieur |
| C — Steps / CFG | 20 / 5.0, `euler` | valeurs du template officiel Klein 9B base |
| Seed | 360001 fixe, partagée | même point de départ pour les 3 blocs |
| LoRA View360 | OFF, force 0.8 | test optionnel (Ctrl+B) |

## Entrées attendues

- Un prompt de base en anglais (pièce, architecture, volumes, ouvertures, boîtier) et cinq entiers : Ambiance, Ensoleillement, Mobilier, Style, Hauteur.

## Prompt Set

Coller [CONTEXT_prompt-set_t2hdri_INT_Compare3_SDXL360_Qwen360_Klein360_v01.md](CONTEXT_prompt-set_t2hdri_INT_Compare3_SDXL360_Qwen360_Klein360_v01.md) dans une conversation Claude, puis donner le brief.

## Checklist de test

1. Charger le JSON dans Comfy Cloud : aucun nœud rouge (si `Math Expression` est rouge, mettre l'instance à jour).
2. Importer les modèles des blocs A et C ; vérifier que les menus des loaders résolvent les noms.
3. Un run aux valeurs par défaut : relever le temps de chaque bloc.
4. Basculer chaque barrette une fois et vérifier le texte dans les 👁️ (en particulier Mobilier 0–2 : le style doit disparaître).
5. Comparer les 3 sorties sur 3 à 4 briefs, puis changer la seed.
6. Test optionnel : Ctrl+B sur la LoRA View360 (bloc A).
7. Me renvoyer le verdict (et le log ComfyUI en cas d'erreur).

## Limites connues

- Prompt commun en texte naturel (pas de JSON FLUX.2 à ce stade) ; ~200 mots : SDXL (CLIP) ne pondère que faiblement la fin du prompt.
- Le LoRA 360 place la source lumineuse principale au centre : orienter dans Blender.
- Pas de vrai HDR dans cette étape (pas d'EXR, pas de boost des fenêtres).
- Licences : Klein 9B base et son LoRA sont sous licence FLUX non commerciale (sorties utilisables, mais vérifier le texte officiel) ; SDXL 360 Diffusion est sous MIT ; vérifier la licence Qwen.
- Lancer les 3 blocs d'un coup charge trois modèles : couper un groupe avec Ctrl+M si la VRAM ou le temps manque.
