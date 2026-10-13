# i2i_QwenImage21_v02

**En une phrase** : image → image avec Qwen Image 2.1 (édition par instruction ou img2img à denoise réglable), **sans décalage de pixels** entre la source préparée et le résultat, **+ composite masqué** qui garantit des pixels strictement identiques hors de la zone éditée. 100 % nœuds natifs, compatible Comfy Cloud, sans nœud Partner / API.

## Pipeline

1. **📥 Image source** (`LoadImage`).
2. **🎛️ Taille de travail** (`ResizeImageMaskNode` → *scale total pixels*, 2.0 MP) — mise à l'échelle **uniforme**, activable via *🎛️ Redimensionner la source* (`ComfySwitchNode`).
3. **📐 Recadrage multiple de 32** (`ResizeImageMaskNode` → *scale to multiple*, 32) — mise à l'échelle uniforme minime + recadrage centré, jamais d'étirement. Sauvegardée en **💾 Source préparée**.
4. **Encodage Qwen 2.1** (`TextEncodeQwenImage21`, `resolution` = 0) — l'image étant déjà multiple de 32, l'encodeur ne la redimensionne pas ; il fournit conditioning + latent vide à la taille exacte de image_1.
5. **Latent** (`ComfySwitchNode`) — *Mode img2img* OFF : latent vide de l'encodeur (édition officielle, denoise 1.0 forcé) ; ON : `VAEEncode` de la source préparée + *🎛️ Denoise img2img*.
6. **KSampler** (euler / simple, CFG 1, 25 steps) + `QwenImage21Cache` → `VAEDecode`.
7. **🧩 Composite** (option, *🎛️ Composite masqué*) : masque peint sur l'image source (`LoadImage` → Mask Editor) → `ResizeImageMaskNode` *match size* (même cadrage que la source préparée) → `GrowMask` (marge) → `MaskToImage` → `ImageBlur` (bord adouci) → `ImageToMask` → `ImageCompositeMasked` (résultat dans le masque, source préparée ailleurs). Aperçu du masque.
8. **💾 Résultat** + **🔍 Comparer** (curseur avant/après).

## Pourquoi il n'y a pas de décalage

Le pixel shift des modèles d'édition Qwen vient d'une incohérence de taille entre la référence vue par le modèle et le latent échantillonné (redimensionnement non uniforme, arrondis différents, latent vide à une autre taille). Ici, une seule image préparée sert à tout : encodeur (sans redimensionnement), latent (taille dérivée de cette image) et comparaison. Le tooltip officiel du nœud le confirme : toute autre taille de latent décale l'édition.

## Pourquoi un composite (v02)

v01 garantit la taille et le cadrage, mais le modèle **régénère** toute l'image par patchs latents de 16×16 px : les arêtes fines (moulures, chambranles, joints) sont redessinées, avec une dérive de 1 à 2 px et un léger lissage. Ce n'est pas réglable par l'échantillonnage. Le composite masqué ne garde du résultat que la zone voulue : partout ailleurs, pixels de la source préparée à l'identique.

**Usage** : clic droit sur *📥 Image source* → *Open in Mask Editor* → peindre la zone avec le **pinceau de masque** (pas le *Paint Pen*, qui peint dans l'image RGB) → Save → *🎛️ Composite masqué* ON.

## Modèles requis

| Type | Nom exact | Dossier | Source |
|---|---|---|---|
| Diffusion | `qwen_image_2.1_bf16.safetensors` (13,3 Go) | `models/diffusion_models/` | [Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) |
| Text encoder | `qwen3vl_8b_bf16.safetensors` (16,3 Go) | `models/text_encoders/` | idem |
| VAE | `qwen_image_2.1_vae_bf16.safetensors` (644 Mo) | `models/vae/` | idem |

Variante légère (templates officiels) : `qwen_image_2.1_int8_convrot.safetensors` + `qwen3vl_8b_int8_convrot.safetensors`.

## Nodes custom

Aucun — 100 % natifs (`comfy-core`). ComfyUI ≥ 0.37.0 requis (nœuds Qwen 2.1). `ComfySwitchNode` et `QwenImage21Cache` sont marqués *expérimentaux*.

## Réglages clés

| Paramètre | Valeur | Pourquoi |
|---|---|---|
| 🎛️ Mode img2img | OFF | OFF = édition officielle (latent vide). ON = garde la composition via le latent source. |
| 🎛️ Denoise img2img | 0.6 | 0.3 retouche légère · 0.6 restyle · 0.85–0.95 ≈ édition. Ignoré en mode édition. |
| 🎛️ Taille de travail | 2.0 MP | Natif jusqu'à ~4 MP (2048²). Au-delà, perte d'adhérence au prompt. |
| 🎛️ Steps | 25 | 4–8 pour une petite retouche locale ; 30–40 pour mains et détails fins. |
| 🎛️ CFG | 1 | Chemin publié ; négatif ignoré. 2 pour les textes denses. Jamais > 3. |
| Encodage → resolution | **0** | Ne pas toucher : c'est ce qui évite un second redimensionnement. |
| 🎛️ Composite masqué | OFF | ON dès qu'un masque est peint : pixel-perfect hors masque. ON sans masque = source inchangée. |
| 🎛️ Marge du masque | 8 px | Couvre les bords de la zone éditée (ombres, reflets, jointures). 16–24 pour un objet qui change de forme. |
| 🎛️ Adoucissement du bord | 8 | Rayon du flou de la jointure (1–31). 1–3 pour un raccord net sur une arête droite. |

## Entrées attendues

- Une image (PNG/JPG), n'importe quel ratio. Le recadrage enlève au plus 31 px par axe (après mise à l'échelle).
- Pour superposer le résultat dans un logiciel : utiliser **💾 Source préparée**, pas l'originale.

## Prompt Set

Coller [CONTEXT_prompt-set_i2i_QwenImage21_v02.md](CONTEXT_prompt-set_i2i_QwenImage21_v02.md) dans une conversation Claude, puis donner le brief et joindre l'image source. Claude renvoie le prompt et les réglages.

## Exemples

| Entrée | Résultat |
|---|---|
| ![in](images/in_exemple.png) | ![out](images/out_exemple.png) |

## Limites connues

- Licence **Qwen Research License** : vérifier les conditions avant un usage commercial.
- Une seule image (pas de références supplémentaires dans cette version).
- Dans la zone masquée, la dérive de 1–2 px reste possible : c'est du contenu régénéré. Faire passer le bord du masque sur une surface unie plutôt que sur une arête.
- Composite à la taille de la source préparée, pas de l'image originale.
- L'alignement est garanti en taille et en cadrage ; une édition « globale » (changement de point de vue, recadrage demandé dans le prompt) déplace évidemment le contenu.
- En mode img2img avec denoise faible, le prompt a peu d'effet : c'est normal.

## Historique

- v02 : ajout du composite masqué natif (dérive de 1–2 px des arêtes fines constatée en v01).
- v01 : préparation multiple de 32, encodeur `resolution` 0, switch édition / img2img.

## Sources

- Nœuds vérifiés sur le code source `comfyanonymous/ComfyUI` (`comfy_extras/nodes_qwen.py`, `nodes_post_processing.py`, `nodes_logic.py`, `nodes_primitive.py`, `nodes_image_compare.py`, `nodes_mask.py`, `nodes.py`) et le template officiel `Comfy-Org/workflow_templates/templates/image_qwen_image_2_1_image_edit.json`.
- Docs : docs.comfy.org/tutorials/image/qwen/qwen-image-2-1.
