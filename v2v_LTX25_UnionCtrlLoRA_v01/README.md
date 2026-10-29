# v2v_LTX25_UnionCtrlLoRA_v01

**En une phrase** : vidéo-à-vidéo **blocking 3D (MP4 1K) → plan rendu stylisé en 2K (2560 × 1408)** avec LTX-2.5 22B distilled, piloté par un prompt (actions + style, **repères couleur** « the RED character… ») et verrouillé sur la structure du blocking (IC-LoRA Union Control, Canny natif ou depth rendue). 100 % nœuds natifs, Comfy Cloud.

- Type : `v2v`
- Modèle principal : LTX-2.5 22B distilled (int8 convrot)
- Modèle secondaire : IC-LoRA Union Control (depth / canny / pose), `ref0.5`
- Cible : Comfy Cloud (nodes 100 % cœur ComfyUI, aucun pack custom)
- Fichier : `../v2v_LTX25_UnionCtrlLoRA_v01.json`

## Pipeline

1. **Entrées** — blocking MP4 1K (`LoadVideo`) → frames ramenées à 8n+1 (offset + max), redimensionnées à 1280×704.
2. **Contrôle structure** — Canny calculé sur le blocking (natif) **ou** vidéo depth rendue depuis la scène 3D (second `LoadVideo`, switch).
3. **Latent initial** — blocking RGB encodé par le VAE (switch) : le modèle *voit* les couleurs du blocking → le prompt peut désigner « the RED character », « the BLUE block ». Option : image de référence stylisée en première image (`LTXVImgToVideoInplace`, bypass piloté).
4. **Prompt** — prompt brut (ou amélioré par Gemma 4 E2B, OFF par défaut) + négatif → `LTXVConditioning` au fps du blocking.
5. **Étape 1 (1K)** — `LTXVAddGuide` injecte les images-guides via l'IC-LoRA, concat AV latent, `SamplerCustomAdvanced` (sigmas manuels distilled), `LTXVCropGuides`.
6. **Étape 2 (2K)** — `LTXVLatentUpsampler` ×2 + 3 pas de re-sampling (switch ON/OFF).
7. **Sortie** — décodage tuilé, audio décodé, MP4 au fps du blocking.

## Modèles

| Fichier | Dossier | Source | Licence |
|---|---|---|---|
| `ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors` | `models/diffusion_models/` | [Lightricks/LTX-2.5](https://huggingface.co/Lightricks/LTX-2.5) (gated) | LTX-2 Community (gratuit < 10 M$ CA) |
| `ltx-2.3-22b-ic-lora-union-control-ref0.5.safetensors` | `models/loras/` | [Lightricks/LTX-2.3-22b-IC-LoRA-Union-Control](https://huggingface.co/Lightricks/LTX-2.3-22b-IC-LoRA-Union-Control) | LTX-2 Community |
| `gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors` | `models/text_encoders/` | Lightricks/LTX-2.5 | LTX-2 Community |
| `gemma4_e2b_it_int8_convrot.safetensors` (optionnel) | `models/text_encoders/` | [Comfy-Org/gemma-4](https://huggingface.co/Comfy-Org/gemma-4) | Gemma |
| `ltx-2.5-video-vae-bf16.safetensors` | `models/vae/` | Lightricks/LTX-2.5 | LTX-2 Community |
| `ltx-2.5-audio-vae-bf16.safetensors` | `models/vae/` | Lightricks/LTX-2.5 | LTX-2 Community |
| `ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors` | `models/latent_upscale_models/` | Lightricks/LTX-2.5 | LTX-2 Community |

Les noms de fichiers sont ceux du template Cloud officiel `video_ltx2_5_t2v` (Comfy-Org/workflow_templates). L'IC-LoRA 2.3 est réutilisé sur 2.5 conformément au workflow officiel Lightricks `LTX-2.5_ICLoRA_Union_Control_Distilled`.

## Nodes custom

Aucun. Nodes vérifiés dans `comfyanonymous/ComfyUI` (nodes.py, comfy_extras/nodes_lt*.py, nodes_video.py, nodes_logic.py, nodes_primitive.py, nodes_math.py, nodes_canny.py, nodes_images.py).

## Réglages clés (groupe 🎛️ CONTRÔLES)

| Réglage | Défaut | Note |
|---|---|---|
| Largeur × hauteur 1K | 1280 × 704 | multiples de 32 ; ×2 → 2560 × 1408 |
| Nombre d'images max | 241 | ≈ 8 s à 30 fps ; ramené à 8n+1 |
| Sigmas étape 1 | `0.909375, 0.725, 0.421875, 0.0` | = steps + denoise du blocking RGB (voir ci-dessous) ; blocking nu → liste complète |
| Sigmas étape 2 | `0.85, 0.7250, 0.4219, 0.0` | upscale, 3 pas |
| CFG vidéo | 1.0 | distilled : négatif quasi sans effet |
| Force IC-LoRA / force du guide | 1.0 / 1.0 | blocking nu → guide **0.6** (le Canny n'a que trois arêtes) ; remonter à 0.8 si le sujet dérive |
| Canny seuils | 0.3 / 0.7 | |
| Injecter RGB en latent | ON | OFF = latent vide (structure seule) |
| Contrôle Canny / depth | ON (Canny) | OFF = vidéo depth fournie |
| Image de référence | bypass ON (ignorée) | OFF pour l'activer |
| Améliorer le prompt | OFF | réécrit le prompt, perd les repères couleur |
| Upscale ×2 | ON | OFF = test rapide 1K |

### Sigmas = steps + denoise

Les sigmas sont le planning de débruitage (niveaux de bruit, du plus fort à 0.0) ; chaque paire = un pas. Le premier chiffre est le **denoise** appliqué au latent du blocking, le nombre de valeurs le **nombre de pas**. Le modèle distilled exige ces niveaux précis : on tronque la liste officielle par le haut, on n'invente pas de valeur.

| Sigmas étape 1 | Denoise | Pas | Usage |
|---|---|---|---|
| `1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875, 0.0` | 100 % | 8 | décor à inventer depuis un blocking nu (recommandé) |
| `0.975, 0.909375, 0.725, 0.421875, 0.0` | ~97 % | 4 | compromis, couleurs du blocking comme amorce |
| `0.909375, 0.725, 0.421875, 0.0` (défaut) | ~91 % | 3 | retouche d'un rendu déjà texturé |
| `0.85, 0.725, 0.421875, 0.0` | 85 % | 3 | = étape 2 (upscale) |

Les cinq premières valeurs (1.0 → 0.975) fixent la composition : c'est là que le décor naît ou pas. Premier test (blocking « balle rebond ») : défaut 0.909 + guide 1.0 → blocking repeint en gris, décor flipper absent ; corriger par la liste complète + guide 0.6.

## Entrées attendues

- `blocking.mp4` : 1K (1920×1080 conseillé), 16:9, 30 fps, 5–10 s, éléments et acteurs en couleurs unies distinctes.
- `depth.mp4` (optionnel) : même cadrage, mêmes images, niveaux de gris.
- `reference_frame.png` (optionnel) : première image stylisée, même cadrage.

## Limites connues

- fps : LTX-2.5 est entraîné à 24/25 fps ; le WF conditionne et exporte au fps du blocking (30). Si le mouvement glisse, convertir le blocking en 25 fps.
- Longueur : > 241 images → mémoire et temps ×2 ; sur Cloud, rester ≤ 241 pour la 2K.
- Upscale ×2 uniquement (2K). 4K = v02 avec l'IC-LoRA « pixel spatial upscaler » LTX-2.5.
- Audio généré par le modèle (muet impossible côté modèle) ; couper au montage.
- EditAnything v2 (LTX-2.5) écarté : éditeur d'objets (Replace/Add/Remove/Restyle), boîte d'entraînement 704×384 / 73 images, pack BFSnodes non confirmé sur Cloud.

## Prompt Set

Coller [CONTEXT_prompt-set_v2v_LTX25_UnionCtrlLoRA_v01.md](CONTEXT_prompt-set_v2v_LTX25_UnionCtrlLoRA_v01.md) dans une conversation Claude, puis donner le brief (mapping couleur → sujet, actions, caméra, style). Claude renvoie le prompt positif, le négatif et les réglages à changer.

## Exemples

`images/in_*.png` / `images/out_*.png` — à compléter après les premiers tests.
