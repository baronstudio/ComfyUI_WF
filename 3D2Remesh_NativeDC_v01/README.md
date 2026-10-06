# 3D2Remesh_NativeDC_v01

**En une phrase** : remesh d'un fichier 3D (GLB/GLTF) → GLB triangulé, étanche (manifold) et ramené à un poly count cible, 100 % nœuds natifs ComfyUI, compatible Comfy Cloud, sans modèle ni crédit API.

## Pipeline

1. **📥 Fichier 3D** (`Load3DAdvanced`) — upload du GLB / GLTF via `model_file` (OBJ, STL acceptés).
2. **🔧 Fichier → mesh éditable** (`Get3DComponents`) — fusionne la scène en un seul mesh, transforms appliqués.
3. **ℹ️ Stats AVANT** (`GetMeshInfo`) — vertices, faces, attributs, affichés sur le nœud.
4. **🧲 Souder les vertices** (`WeldVertices`) — indispensable sur les « soupes de triangles » (IA, scans).
5. **🧮 Résolution remesh auto** (`ComfyMathExpression`) — `res = clamp(64, 1024, ≈ √(2,7 × poly count))`, arrondi à 32 : le remesh produit ~3–4× la cible, la décimation affine ensuite.
6. **♻️ Remesh étanche** (`RemeshMesh`, mode `udf`) — champ de distance + Dual Contouring : surface propre, uniforme, fermée ; coque intérieure supprimée (`drop_inverted_components`), pôles valence 3 nettoyés (`fix_poles`).
7. **🔀 Manifold ON / OFF** (`ComfySwitchNode`, lazy) — ON = mesh remeshé ; OFF = mesh d'origine soudé (le remesh n'est pas calculé).
8. **📉 Décimation** (`DecimateMesh`, QEM `midpoint`) — au poly count cible exact (max).
9. **✨ Normales lissées** (`MeshSmoothNormals`) + **ℹ️ Stats APRÈS** (`GetMeshInfo`).
10. **💾 GLB** (`SaveGLB`) — avec aperçu 3D, dans `output/3D2Remesh/`.

## Modèles requis

Aucun. Traitement algorithmique (GPU sur Cloud).

## Nodes custom

Aucun — 100 % natifs (`comfy-core`). Pas de nœud Partner / API.
Nœuds 3D récents et marqués *expérimentaux* : ComfyUI à jour requis (Comfy Cloud l'est).

## Réglages clés

| Paramètre | Valeur par défaut | Pourquoi |
|---|---|---|
| 🎛️ Poly count cible | 20 000 tri | Plafond de triangles en sortie. Web 5–20k, jeu temps réel 20–80k, impression 100k+. |
| 🎛️ Manifold auto | ON | Mesh étanche, sans trous ni faces internes. OFF pour garder les ouvertures et la forme exacte. |
| 🎛️ Lissage | 2 | Taubin, efface l'escalier du Dual Contouring. 0 = arêtes vives, > 4 = arrondi. |
| 🎛️ Angle arêtes vives | 180° | 180 = shading lisse (organique). 30–60° = hard-surface. |
| `sign_mode` (Remesh) | udf | Robuste aux meshes sales / non manifold. `sdf` + `manifold` = arêtes plus nettes, mais exige un winding cohérent. |
| `project_back` (Remesh, avancé) | 0.0 | 0,3–0,5 recolle les vertices à la surface d'origine (plus de fidélité, moins régulier). |
| `drop_small_components` (Remesh, avancé) | 0.01 | Supprime les îlots < 1 % du plus gros morceau. 0 pour garder les petites pièces. |
| `placement_mode` (Decimate) | midpoint | Meilleure qualité, préserve les détails fins. `qem` = contrôle des arêtes vives. |
| `epsilon_rel` (Weld) | 1e-5 | 1e-3 si des vertices proches mais distincts restent séparés. |

## Entrées attendues

- Un fichier **GLB / GLTF** (recommandé). OBJ et STL acceptés. **FBX / USDZ non supportés** → Blender → Export glTF 2.0.
- **Manifold ON : modèle normalisé** — dimension max ≈ 1 unité, centré sur l'origine (cas natif des sorties Trellis / Hunyuan3D). Le remesh travaille dans un cube fixe [-0,5 ; 0,5] : au-delà, la géométrie est coupée.

## Prompt Set

Pas de prompt dans ce WF. [CONTEXT_prompt-set_3D2Remesh_NativeDC_v01.md](CONTEXT_prompt-set_3D2Remesh_NativeDC_v01.md) transforme Claude en conseiller de réglages : on lui décrit l'asset et sa destination, il renvoie les valeurs à saisir.

## Exemples

| Entrée | Résultat |
|---|---|
| ![in](images/in_exemple.png) | ![out](images/out_exemple.png) |

## Limites connues

- **Triangles uniquement** : le format glTF/GLB ne stocke pas de quads, et aucun nœud natif ne fait de quad remesh (Quadriflow, Instant Meshes) ni de **symétrie**. Pour du quad : Blender (*Remesh Quad* / QuadriFlow, ou *Tris to Quads*) après ce WF.
- Pas de quad remesh via API sur Cloud non plus sans crédits : Tripo (`Tripo: Import Model` → `Tripo: Convert model`, quad + symétrie, sortie FBX). Meshy n'a pas de nœud Remesh dans ComfyUI.
- **Échelle** : en Manifold ON, un modèle > 1 unité ou décentré est tronqué (voir *Entrées attendues*). Manifold OFF n'a pas cette limite.
- **UV et textures perdues** (couleurs de sommets conservées). Enchaîner avec `3D2UV_UnwrapMesh_v01` pour re-déplier.
- Scène fusionnée en **un seul mesh**.
- Le poly count est un **maximum** : si le remesh produit moins de faces que la cible, la décimation ne fait rien → monter la cible ou la résolution.
- Aperçu 3D vide (« Failed to initialize 3D Viewer ») = WebGL du navigateur, pas le WF ; fichier dispo dans **Assets → Generated**.

## Sources

- Nœuds vérifiés sur le code source `comfyanonymous/ComfyUI` (`comfy_extras/nodes_mesh_postprocess.py` — `RemeshMesh`, `DecimateMesh`, `WeldVertices`, `MeshSmoothNormals` ; `nodes_mesh_io.py`, `nodes_load_3d.py`, `nodes_save_3d.py`, `nodes_math.py`, `nodes_logic.py`), et le template officiel `Comfy-Org/workflow_templates/templates/3d_pixal3d_trellis2_image_to_model.json` (sérialisation de `RemeshMesh` / `DecimateMesh`).
- Partner nodes vérifiés : `comfy_api_nodes/nodes_meshy.py` (pas de remesh), `nodes_tripo.py` (`TripoImportModelNode`, `TripoConversionNode`).
- Liste des packs Comfy Cloud : comfy.org/cloud/supported-nodes (GeometryPack et Trellis2 absents).
