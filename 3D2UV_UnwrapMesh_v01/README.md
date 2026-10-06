# 3D2UV_UnwrapMesh_v01

**En une phrase** : dépliage UV automatique d'un fichier 3D (GLB/GLTF) → GLB avec UV + PNG du layout UV + carte d'AO cuite dans ces UV, 100 % nœuds natifs ComfyUI, compatible Comfy Cloud, sans modèle ni crédit API.

## Pipeline

1. **📥 Fichier 3D** (`Load3DAdvanced`) — upload du GLB / GLTF via le champ `model_file` (OBJ, STL acceptés).
2. **🔧 Fichier → mesh éditable** (`Get3DComponents`) — fusionne toute la scène en un seul mesh, transforms appliqués, 1er matériau conservé.
3. **✂️ Dépliage UV** (`UnwrapMesh`) — découpe en îlots, aplatissement, packing dans [0,1].
4. **🗺️ Rendu du layout UV** (`RenderUVAtlas`) — image de contrôle, une couleur par îlot, bords en noir.
5. **🌑 Bake AO** (`BakeAmbientOcclusion`) — occlusion ambiante du mesh d'origine cuite dans les nouvelles UV.
6. **💾 Sorties** — `SaveGLB` (avec aperçu 3D intégré) + 2 × `SaveImage`, dans `output/3D2UV/`.

## Modèles requis

Aucun. Dépliage et bake algorithmiques (GPU/CPU).

## Nodes custom

Aucun — 100 % natifs (`comfy-core`). Pas de nœud Partner / API.
Nœuds 3D récents et marqués *expérimentaux* : ComfyUI à jour requis (Comfy Cloud l'est).

## Réglages clés

| Paramètre | Valeur par défaut | Pourquoi |
|---|---|---|
| 🎛️ Résolution atlas | 2048 | Pilote dépliage (densité de texel), layout et AO. Max 4096 (limite de `RenderUVAtlas`). |
| 🎛️ Marge entre îlots | 4 px | ~2 px @1024, 4 px @2048, 8 px @4096 — évite les bavures au mipmapping. |
| 🎛️ AO — rayons par texel | 64 | 128–256 pour une AO propre, au prix du temps. |
| 🎛️ AO — intensité | 1.0 | >1 assombrit, <1 éclaircit. |
| `segmenter` (Unwrap) | pec | GPU, rapide. `adaptive` = CPU, plus lent, parfois des îlots plus propres. |
| `weld_distance` (Unwrap) | 0.0002 | Monter à 0.001 si un îlot par triangle (mesh non soudé). |
| `max_distance` (AO) | 0.5 | 0.1–0.2 pour une occlusion plus locale. |
| `bias` (AO) | 0.01 | Monter si taches sombres sur surfaces planes. |

## Entrées attendues

- Un fichier **GLB / GLTF** (recommandé). OBJ et STL acceptés. **FBX / USDZ non supportés** → convertir en GLB (Blender → Export glTF 2.0).
- Mesh triangulé ou quad, idéalement **soudé** (pas de « soupe de triangles »), échelle quelconque.

## Prompt Set

Pas de prompt dans ce WF. [CONTEXT_prompt-set_3D2UV_UnwrapMesh_v01.md](CONTEXT_prompt-set_3D2UV_UnwrapMesh_v01.md) transforme Claude en conseiller de réglages : on lui décrit l'asset et sa destination, il renvoie les valeurs à saisir.

## Exemples

| Entrée | Résultat |
|---|---|
| ![in](images/in_exemple.png) | ![out](images/out_exemple.png) |

## Limites connues

- Scène fusionnée en **un seul mesh** ; seul le **1er matériau** est gardé.
- Les **UV existantes sont remplacées**.
- Vertices dupliqués sur les coutures : le compte de vertices augmente (normal).
- Dépliage automatique : pas de coutures « artistiques » ni de symétrie/empilement d'îlots. Pour un asset hero, reprendre les seams dans Blender / RizomUV.
- Pas d'aperçu du layout UV superposé au modèle : contrôle via le PNG.
- Pas besoin d'AO : sélectionner *🌑 Bake AO* + *💾 AO (PNG)* puis **Ctrl+B**.

## Historique

- v01 (correctif) : `Load3D` remplacé par `Load3DAdvanced`. L'ancien nœud plantait sur Comfy Cloud v0.38.2 (`TypeError: string indices must be integers` dans `nodes_load_3d.py`) quand l'interface n'envoyait pas la capture du viewport ; `Load3DAdvanced` lit le fichier sans dépendre de cette capture.

## Sources

- Nœuds vérifiés sur le code source `comfyanonymous/ComfyUI` (`comfy_extras/nodes_mesh_postprocess.py`, `nodes_mesh_io.py`, `nodes_load_3d.py`, `nodes_save_3d.py`) et le template officiel `Comfy-Org/workflow_templates/templates/3d_pixal3d_multi_views.json`.
- Docs : docs.comfy.org/built-in-nodes/UnwrapMesh, Get3DComponents, RenderUVAtlas, BakeAmbientOcclusion.
