# 3D2Parts_TripoSmartSegment_v01

**En une phrase** : découpe un fichier 3D (GLB) en pièces séparées et nommées → un GLB (une pièce = un objet), avec option **Cap** qui complète et ferme chaque pièce. Compatible Comfy Cloud, nœuds Partner Tripo (crédits).

## Pipeline

1. **📥 Fichier 3D** (`Load3DAdvanced`) : upload du GLB via `model_file` (FBX, OBJ, STL acceptés).
2. **☁️ Import Tripo** (`TripoImportModelNode`) : envoie le fichier chez Tripo, renvoie un `model task_id`. Gratuit, 150 Mo max.
3. **🧮 Prompt Tripo** (`StringFormat`) : assemble le nombre d'éléments visé et la description des pièces dans le champ `hint`.
4. **✂️ Découpe sémantique** (`TripoSmartSegmentNode`, source `model`) : pièces séparées et nommées, guidées par le `hint` et la `granularity`. Sorties : GLB segmenté, noms des pièces, analyse Tripo, masque couleur.
5. **🧩 CAP** (`TripoMeshCompleteNode`) : complète et ferme chaque pièce (zones cachées reconstruites). ON par défaut, **Ctrl+B = OFF** (aucun crédit consommé).
6. **🔀 Switch** (`ComfySoftSwitchNode`) : prend le GLB complété si le Cap est actif, sinon le GLB brut. Bascule automatique, rien à régler.
7. **💾 GLB** (`SaveGLB`) avec aperçu 3D, dans `output/3D2Parts/`.

## Modèles requis

Aucun téléchargement : Tripo tourne côté API (Partner nodes Comfy.org).

| Type | Nom | Source |
|---|---|---|
| API Partner | Tripo v3 — Smart Segment, Complete Mesh Parts, Import Model | Comfy.org (crédits du compte Comfy) |

## Nodes custom

Aucun : 100 % `comfy-core`. **Nœuds Partner / API utilisés** (choix validé : modèle utilisable sur Cloud, hors Hunyuan3D).

## Coût indicatif (badges de prix des nœuds)

| Nœud | Prix |
|---|---|
| Import Model | gratuit |
| Smart Segment (source model) | ≈ 0,55 $ |
| Complete Mesh Parts (Cap) | ≈ 0,50 $ |
| **Total Cap ON / Cap OFF** | **≈ 1,05 $ / ≈ 0,55 $** |

## Réglages clés

| Paramètre | Valeur par défaut | Pourquoi |
|---|---|---|
| 🎛️ Nombre d'éléments visé | 6 | Injecté dans le prompt (« about N separate parts »). **Indicatif** : l'API n'a pas de paramètre « N pièces exact ». |
| ✏️ Description des pièces | prompt EN | Nature de l'objet + liste des pièces. Levier principal sur le découpage et les noms. |
| `granularity` (✂️) | medium | coarse ≤ 4 pièces, medium 5–10, fine 10+. À accorder au nombre visé. |
| 🧩 CAP | ON | Pièces fermées, prêtes à animer / imprimer / éclater. OFF pour une découpe brute fidèle à la surface d'origine. |
| `part_names` (🧩) | vide | Vide = toutes les pièces complétées. Sinon, liste séparée par des virgules (noms lus dans 📋). |

## Entrées attendues

- Un fichier **GLB** unique (textures embarquées), 150 Mo max. FBX, OBJ, STL acceptés ; **GLTF multi-fichiers refusé**.
- Fonctionne mieux sur des objets aux pièces lisibles (personnage, véhicule, mobilier, prop mécanique). Les sorties IA (Trellis, Pixal3D) et les scans passent.

## Prompt Set

Coller [CONTEXT_prompt-set_3D2Parts_TripoSmartSegment_v01.md](CONTEXT_prompt-set_3D2Parts_TripoSmartSegment_v01.md) dans une conversation Claude, décrire l'objet et l'usage visé. Claude renvoie le nombre d'éléments, la description des pièces (EN), la granularity et le choix Cap ON/OFF.

## Exemples

| Entrée | Résultat |
|---|---|
| ![in](images/in_exemple.png) | ![out](images/out_exemple.png) |

## Limites connues

- **Nombre de pièces non garanti** : Tripo décide ; le nombre et la granularity orientent seulement.
- **Cap = géométrie reconstruite** : les pièces complétées peuvent s'écarter légèrement de l'original ; UV et textures d'origine pas garanties sur les zones reconstruites.
- **Crédits** à chaque run (voir tableau). Passer le Cap en OFF pour itérer sur le prompt, puis ON pour la version finale.
- Le Cap se règle par **bypass du nœud 🧩** (Ctrl+B) et non par un booléen : un nœud Partner actif s'exécute toujours, même derrière un switch. Le bypass est le seul moyen de ne pas payer.
- Données envoyées aux serveurs Tripo via Comfy.org : à vérifier pour un asset client sous NDA.
- Aperçu 3D vide (« Failed to initialize 3D Viewer ») = WebGL du navigateur, pas le WF ; fichier dispo dans **Assets → Generated**.

## Sources

- Schémas vérifiés dans `comfyanonymous/ComfyUI` : `comfy_api_nodes/nodes_tripo.py` (`TripoImportModelNode`, `TripoSmartSegmentNode`, `TripoMeshCompleteNode`), `comfy_extras/nodes_load_3d.py`, `nodes_save_3d.py`, `nodes_logic.py` (`ComfySoftSwitchNode`), `nodes_string.py` (`StringFormat`), `nodes_preview_any.py`.
- Sérialisation des DynamicCombo et de `StringFormat` : templates officiels `Comfy-Org/workflow_templates` (`api_tripo_p1_image_to_model.json`, `image_ming_image_01_design_image_edit.json`).
- Doc : docs.comfy.org/built-in-nodes/TripoSmartSegmentNode, TripoSegmentNode.
