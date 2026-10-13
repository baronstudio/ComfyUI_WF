# i2i_QwenImage21_v03

**En une phrase** : changement de matière sur un objet d'un rendu 3D (3ds Max, Blender…), sélectionné à la pipette sur une **passe Object ID**, à partir d'un échantillon de matière (albedo, spéculaire, normale). L'IA choisit l'échelle et l'orientation de la texture, et le résultat est recomposé **à la résolution d'origine**, pixel-perfect hors de l'objet. 100 % nœuds natifs, compatible Comfy Cloud, sans nœud Partner / API.

## Pipeline

1. **📥 Entrées** — rendu beauty (format libre) + passe Object ID de même taille (`LoadImage` ×2).
2. **🆔 Masque Object ID** — deux modes (`ComfySwitchNode`) :
   - *pipette* : `ColorToRGBInt` (widget couleur + pipette du navigateur, ou code hex) → `ImageColorToMask`, correspondance RGB **exacte** ;
   - *Mask Editor* : outil **Color Select** (tolérance 0) sur la passe ID → sortie MASK du `LoadImage`.
   Puis `ResizeImageMaskNode` *match size* en *nearest-exact* (calage sur le rendu) → `GrowMask` → `ImageBlur` → masque de composite pleine taille. Aperçu du masque.
3. **🧱 Matière** — albedo, spéculaire, normale (`LoadImage` ×3), ramenées à 1024 px (`ResizeImageMaskNode` *scale longer dimension*) pour limiter le coût de l'encodeur.
4. **📐 Préparation sans recadrage** — mise à l'échelle uniforme (2.0 MP, option) → `GetImageSize` → `ComfyMathExpression` `(32 - a % 32) % 32` → `ImagePadForOutpaint` à droite / en bas (feathering 0). Même padding appliqué au masque de référence.
5. **Encodage Qwen 2.1** (`TextEncodeQwenImage21`, resolution 0) — `image_1` rendu, `image_2` masque (blanc = objet), `image_3` albedo, `image_4` spéculaire, `image_5` normale.
6. **Génération** — switch édition / img2img + denoise, `KSampler` euler / simple, `QwenImage21Cache`, `VAEDecode`.
7. **🧩 Recomposition** — `ImageCrop` (retrait du padding, taille de travail exacte) → `ResizeImageMaskNode` *match size* sur le rendu original → `ImageCompositeMasked` : IA dans le masque, pixels natifs du rendu ailleurs.
8. **💾 Sortie** — rendu modifié à la taille d'origine + `ImageCompare` (original / modifié) + résultat IA brut pour contrôle.

## Pourquoi c'est pixel-perfect

- Le masque vient de valeurs RGB exactes de la passe ID, à la taille du rendu : aucune estimation (contrairement à SAM).
- Aucun recadrage : le padding ajouté pour le multiple de 32 est retiré à l'identique.
- Hors masque, l'image de sortie **est** le rendu original, pixel pour pixel, à sa résolution native.

## Préparer la passe Object ID

| Logiciel | Réglage |
|---|---|
| Blender | Passe *Object Index* (ou *Cryptomatte* convertie en couleurs plates dans le compositor), **filtre / anti-aliasing désactivé**, view transform **Standard** à l'export, PNG 8 bits RGB. |
| 3ds Max | Render Element *Object ID* (couleurs aléatoires ou par objet), **filtrage OFF**, PNG 8 bits. |
| Tous | Même cadrage et même taille que le beauty. Jamais de JPEG (compression = couleurs fausses). |

## Modèles requis

| Type | Nom exact | Dossier | Source |
|---|---|---|---|
| Diffusion | `qwen_image_2.1_bf16.safetensors` | `models/diffusion_models/` | [Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) |
| Text encoder | `qwen3vl_8b_bf16.safetensors` | `models/text_encoders/` | idem |
| VAE | `qwen_image_2.1_vae_bf16.safetensors` | `models/vae/` | idem |

## Nodes custom

Aucun — 100 % natifs (`comfy-core`). ComfyUI ≥ 0.37.0. `ImageCrop` (*Crop Image*) est marqué *deprecated* mais reste enregistré ; `ComfySwitchNode` et `QwenImage21Cache` sont *expérimentaux*.

## Réglages clés

| Paramètre | Valeur | Pourquoi |
|---|---|---|
| 🎛️ Masque | OFF (pipette) | ON = Mask Editor / Color Select : plusieurs objets d'un coup, lecture des vraies valeurs. |
| 🎨 Couleur de l'objet | #ff0000 | À piper sur la passe ID. Correspondance exacte : vérifier l'aperçu du masque. |
| 🎛️ Marge du masque | 1 px | Couvre la frange anti-aliasée du beauty au bord de l'objet. 0 = coupe franche sur l'ID. |
| 🎛️ Adoucissement | 1 | 1 ≈ bord net. Monter à 2–3 seulement si une frange reste visible. |
| 🎛️ Mode img2img | OFF | OFF = vrai changement de matière. ON + denoise 0.7–0.85 = conserve mieux éclairage et ombres. |
| 🎛️ Taille de travail | 2.0 MP | Natif jusqu'à ~4 MP. Le résultat est ensuite agrandi à la taille du rendu. |
| 🎛️ Steps / CFG | 28 / 1 | 30–40 si la texture manque de finesse. |
| Encodage → resolution | **0** | Ne pas toucher. |

## Entrées attendues

- Rendu beauty : PNG / JPG / EXR 8 bits converti, n'importe quel ratio.
- Passe Object ID : **même taille**, couleurs plates, sans AA, PNG 8 bits.
- Matière : 3 images carrées (2048 px conseillé), albedo sans éclairage cuit de préférence.

## Prompt Set

Coller [CONTEXT_prompt-set_i2i_QwenImage21_v03.md](CONTEXT_prompt-set_i2i_QwenImage21_v03.md) dans une conversation Claude, joindre le rendu, la passe ID et les trois cartes de matière, puis donner le brief.

## Exemples

| Entrée | Résultat |
|---|---|
| ![in](images/in_exemple.png) | ![out](images/out_exemple.png) |

## Limites connues

- Licence **Qwen Research License** : vérifier avant usage commercial.
- Le modèle lit spéculaire et normale comme des images de référence, pas comme des cartes PBR : l'effet sur la brillance et le relief est indicatif. Si elles perturbent, bypasser **🧱 Normale** seule ou **Spéculaire + Normale** (pas Spéculaire seule : les numéros `<imageN>` se décaleraient).
- Une couleur par passe en mode pipette (plusieurs objets : mode Mask Editor).
- Dans le masque, la texture est générée à la taille de travail puis agrandie : moins nette que le rendu natif pour un original 4K et plus.
- Le padding gris (≤ 31 px) à droite / en bas est vu par le modèle puis retiré : sans effet sur le résultat.

## Historique

- v03 : passe Object ID (pipette exacte ou Color Select), références matière ×3, préparation par padding sans recadrage, recomposition à la taille d'origine.
- v02 : composite masqué (dérive 1–2 px des arêtes fines constatée en v01).
- v01 : préparation multiple de 32, encodeur `resolution` 0, switch édition / img2img.

## Sources

- Nœuds vérifiés sur le code source `comfyanonymous/ComfyUI` (`comfy_extras/nodes_qwen.py`, `nodes_mask.py`, `nodes_color.py`, `nodes_math.py`, `nodes_images.py`, `nodes_post_processing.py`, `nodes_logic.py`, `nodes.py`) et sur les templates officiels `Comfy-Org/workflow_templates` (sérialisation de `ComfyMathExpression`, `ColorToRGBInt`, `ImagePadForOutpaint`, `ResizeImageMaskNode` *match size*).
- Docs : docs.comfy.org/tutorials/image/qwen/qwen-image-2-1.
