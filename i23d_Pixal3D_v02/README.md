# i23d_Pixal3D_v02

**En une phrase** : 3 à 4 vues d'un même sujet (face, côté, dos, + 3/4 en référence) → GLB triangulé, étanche (manifold), sans UV ni texture, ramené à un poly count cible, avec la hauteur cible encodée dans le nom du fichier. 100 % nœuds natifs ComfyUI, compatible Comfy Cloud.

## Pipeline

1. **📥 Entrées** (`LoadImage` ×4) — face (obligatoire), côté, dos, 3/4. Le 3/4 n'est **pas injecté** : Pixal3D n'a que 4 slots fixes (0° / 90° / 180° / 270°) ; il sert de référence visuelle dans le WF.
2. **✂️ Détourage** (`RemoveBackground`, BiRefNet) + **⬛ Recadrage** (`ImageCropToMask`, 1024 × 1024, pad 1,1) — accepte des images de tailles et ratios différents, sujet centré à la même échelle.
3. **🔀 Routage des vues** (2 `ComfySwitchNode` pilotés par le même booléen, entrées inversées) — la vue de côté part dans le slot `left` (ON) ou `right` (OFF) selon le flanc montré ; le dos peut être désactivé.
4. **🧭 Conditionnement** (`Pixal3DMultiViewConditioning`, DINOv3) — face = premier slot, donc la face définit l'avant du mesh.
5. **🧊 Génération Pixal3D** (Trellis.2) — ① structure (32³) → ② forme 512 → ③ détail (upsample 1536) → `VaeDecodeShapeTrellis`. Réglages CFG / shift repris du template officiel.
6. **♻️ Mesh** — `WeldVertices` → `FillHoles` (petits trous) → `RemeshMesh` **SDF paroi simple** par défaut (une seule surface fermée) — ou **UDF** de secours via switch si le SDF sort troué ou bruité — → `DecimateMesh` (QEM midpoint) → `MeshSmoothNormals` → stats. Résolution remesh auto depuis le poly count (min 128).
7. **💾 Sortie** (`StringFormat` + `SaveGLB`) — `output/i23d_Pixal3D/model_H<hauteur>cm_<tris>tris_00001_.glb`.
8. **Hors ComfyUI** — `blender_scale_to_height.py` lit la hauteur dans le nom et met le modèle à l'échelle réelle, pieds au sol.

## Modèles requis

| Type | Nom exact | Dossier | Source |
|---|---|---|---|
| Diffusion | `pixal3d_multiview_int8_convrot.safetensors` (5,2 Go) | `models/diffusion_models/` | [Comfy-Org/Pixal3D](https://huggingface.co/Comfy-Org/Pixal3D) |
| VAE forme | `trellis_2_shape_vae_bf16.safetensors` (1,0 Go) | `models/vae/` | [Comfy-Org/Pixal3D](https://huggingface.co/Comfy-Org/Pixal3D) |
| Clip vision | `dino_v3_L_naf_fp32.safetensors` (1,1 Go) | `models/clip_vision/` | [Comfy-Org/Pixal3D](https://huggingface.co/Comfy-Org/Pixal3D) |
| Détourage | `birefnet.safetensors` (0,4 Go) | `models/background_removal/` | [Comfy-Org/BiRefNet](https://huggingface.co/Comfy-Org/BiRefNet) |

Le VAE de texture Trellis.2 n'est **pas** nécessaire (pas de texture).

## Nodes custom

Aucun — 100 % natifs (`comfy-core`). Pas de nœud Partner / API. Nœuds 3D récents, ComfyUI à jour requis (Comfy Cloud l'est).

## Réglages clés

| Paramètre | Défaut | Pourquoi |
|---|---|---|
| 🎛️ Poly count cible | 20 000 tri | Plafond de triangles. Web 5–20k, jeu 20–80k, impression 100k+. |
| 🎛️ Hauteur cible (cm) | 180 | Écrite dans le nom du fichier ; appliquée par le script Blender. |
| 🎛️ Vue de côté = gauche du perso | ON | ON = on voit le flanc **gauche** du sujet. Mauvais réglage = volumes en miroir sur le côté. |
| 🎛️ Utiliser la vue de dos | ON | OFF si pas de dos (moins fiable à l'arrière). |
| 🎛️ Seed | 42 | Partagé par les 3 KSampler. |
| 🎛️ FOV des vues | 20° | 20 pour rendus / model sheets quasi orthographiques. Photos : valeur réelle de l'objectif. |
| 🎛️ Résolution détail | 1536 | 1024 rapide, 2048 plus fin (plus de VRAM). |
| 🎛️ Lissage | 2 | Taubin sur le remesh. 0 = arêtes vives. |
| KSampler ① / ② / ③ | 12 / 20 / 12 steps, CFG 7,5, euler | Valeurs du template officiel Pixal3D multivue. |
| 🎛️ Remesh SDF paroi simple | **ON (SDF)** | SDF = une seule surface fermée (paroi simple). OFF = UDF de secours si le SDF sort troué ou bruité : l'UDF crée par nature une double paroi là où le mesh brut est ouvert (manches, bas de veste), coque interne retirée seulement si elle est détachée. |
| 🩹 Boucher les trous `max_perimeter` | 0,03 | Ferme les petits trous avant le remesh (le signe SDF a besoin d'une surface fermée). |

## Entrées attendues

- `images/in_front.png`, `in_side.png`, `in_back.png`, `in_34.png` — **≥ 1024 px** sur le petit côté, même sujet, même pose (A-pose pour un perso), même échelle, cadrage complet, fond uni.
- Vues incomplètes → générer les manquantes avec **Qwen_3Ref_ModelSheet_V1**.

## Prompt Set

Pas de prompt texte dans ce WF. [CONTEXT_prompt-set_i23d_Pixal3D_v02.md](CONTEXT_prompt-set_i23d_Pixal3D_v02.md) transforme Claude en conseiller : préparation des vues, réglages à saisir, contrôles du résultat.

## Exemples

| Entrée | Résultat |
|---|---|
| ![in](images/in_exemple.png) | ![out](images/out_exemple.png) |

## Changements v02

- **Correction double paroi** : en v01, le remesh UDF (champ de distance non signé) crée par nature deux surfaces décalées autour de la paroi ; la coque intérieure n'était supprimée que si elle formait un morceau séparé, ce qui n'est pas le cas dès que le mesh Pixal3D a des trous → « épaisseur » visible en coupe. v02 ajoute un remesh **SDF** (une seule surface) et le bouchage des trous, plus `drop_enclosed_components` en UDF. **Le SDF paroi simple est désormais le défaut** (mise à jour Comfy Cloud du 05/10/2026) ; l'UDF reste disponible en secours via le switch.
- Switch côté gauche / droite sans `InvertBooleanNode` (absent de Comfy Cloud).

## Limites connues

- **Pas de mise à l'échelle native** : aucun nœud core ne scale un mesh, et le `model_3d_info` de `Save 3D (Advanced)` n'est pas appliqué au fichier exporté (vérifié dans `nodes_save_3d.py`). D'où le script Blender. Le GLB sort normalisé (≈ 1 unité, centré).
- **Triangles uniquement** (glTF), pas de quad ni de symétrie → Blender après coup.
- La vue **3/4 n'influence pas** la forme.
- Le poly count est un **maximum** ; si le remesh produit moins de faces, la décimation ne fait rien.
- **Double paroi (mode UDF de secours)** aux ouvertures du mesh brut : non résolue de façon native. Nettoyage dans Blender si besoin (sélection de la coque interne en *Select Linked*, ou Remesh Voxel).
- Manifold : le remesh + décimation QEM donnent un mesh fermé et soudé, mais à vérifier (Blender : *Select > All by Trait > Non Manifold*), surtout sur les parties très fines.
- Le `StringFormat` (entrées dynamiques) est récent : si le nom de fichier sort mal, saisir le préfixe à la main dans `SaveGLB`.
- Aperçu 3D vide (« Failed to initialize 3D Viewer ») = WebGL du navigateur ; fichier dans **Assets → Generated**.

## Sources

- Template officiel `Comfy-Org/workflow_templates/templates/3d_pixal3d_multi_views.json` (chaîne Pixal3D, CFG, steps, modèles).
- Code source `comfyanonymous/ComfyUI` : `comfy_extras/nodes_trellis2.py`, `nodes_mesh_postprocess.py`, `nodes_save_3d.py`, `nodes_images.py`, `nodes_bg_removal.py`, `nodes_logic.py`, `nodes_string.py`, `nodes_math.py`.
- [Pixal3D — docs.comfy.org](https://docs.comfy.org/tutorials/3d/pixal3d) · [Comfy Cloud supported nodes](https://comfy.org/cloud/supported-nodes/) (GeometryPack absent).
