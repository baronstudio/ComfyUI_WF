# ComfyUI_WF

Workflows ComfyUI de **Jean-Baptiste BARON** (Baron Studio) — génération d'images, de model sheets, d'environnements 360, de vidéos et d'assets 3D (Qwen-Image-Edit, Z-Image, Flux, LTX-Video, MiniMax/Hailuo, Pixal3D, Tripo).

Chaque workflow est versionné avec son **Prompt Set pour Claude** : un fichier `CONTEXT_prompt-set_*.md` à coller en début de conversation, qui transforme Claude en générateur de prompts calibré pour ce workflow précis (champ par champ, avec les contraintes du modèle et du pipeline).

---

## Arborescence

Chaque workflow a son dossier, nommé exactement comme son fichier `.json` (qui reste à la racine) :

```
<Nom_Du_WF>.json                     # le workflow ComfyUI, à la racine
<Nom_Du_WF>/
├── CONTEXT_prompt-set_<nom>.md      # le Prompt Set à donner à Claude
├── README.md                        # modèles requis, nodes custom, réglages clés
├── *.py                             # (optionnel) scripts annexes (post-traitement Blender…)
└── images/                          # images d'exemple (entrées + résultats)
    ├── in_*.png
    └── out_*.png
```

Le dossier [_TEMPLATE_WF/](_TEMPLATE_WF/) fournit les gabarits de `README.md` et de prompt set à copier dans un dossier de workflow.

> Les 25 dossiers existent ; 8 contiennent déjà leur Prompt Set et 4 leur README technique. Les autres se remplissent au fur et à mesure.

## Conventions

- **Nommage** : `[type]_[ModèlePrincipal]_[ModèleSecondaire]_[vNN]` — segment secondaire omis s'il n'y en a pas (ex. `t2i_Flux2Dev_v01`, `i2i_QwenEdit2511_MultiAngleLoRA_v01`). Types : `t2i, i2i, i2v, t2v, v2v, inpaint, upscale, relight, i2Vecto, i23d, t23D, 3D2UV, 3D2Remesh, 3D2Parts, i2pbr, t2audio, i2audio`. La version `vNN` est portée par le nom de fichier (nouveau fichier + nouveau dossier à chaque version, on ne réécrit pas l'ancienne). Les workflows antérieurs gardent leur nom historique `Domaine_Sujet_vN`.
- **Prompt Set** : toujours préfixé `CONTEXT_prompt-set_`, rédigé en anglais pour la partie prompts, en français pour les consignes de travail.
- **Images d'exemple** : PNG/JPG uniquement, préfixe `in_` (entrées) / `out_` (résultats). Les vidéos et fichiers lourds sont exclus par le [.gitignore](.gitignore) — les héberger ailleurs et pointer le lien dans le README du WF.
- **Modèles / checkpoints** : jamais versionnés. Les lister dans le README du workflow (nom exact + source).

---

## Index des workflows

### Model sheet / character & prop design
| Workflow | Prompt Set |
|---|---|
| [Full_Workflow_ModelSheet_V1.json](Full_Workflow_ModelSheet_V1.json) — pipeline complet moodboard → face master → style → 3 vues tournées | [CONTEXT](Full_Workflow_ModelSheet_V1/CONTEXT_prompt-set_ModelSheet_V1.md) |
| [qwen_modelsheet_rotation.json](qwen_modelsheet_rotation.json) — rotation seule (LoRA Multiple-Angles) | — |
| [qwen_moodboard_face_style.json](qwen_moodboard_face_style.json) — moodboard → vue de face stylisée | — |

### Image editing / intégration
| Workflow | Prompt Set |
|---|---|
| [Image_Edit_Klein_v3_CropStitch_RefSujet.json](Image_Edit_Klein_v3_CropStitch_RefSujet.json) — édition 4 props, crop & stitch, référence sujet | [CONTEXT](Image_Edit_Klein_v3_CropStitch_RefSujet/CONTEXT_prompt-set_Klein_v3_CropStitch_RefSujet.md) |
| [Image_Edit_4props_Klein_v2_CropStitch.json](Image_Edit_4props_Klein_v2_CropStitch.json) — v2 | — |
| [Image_Edit_4props_Klein.json](Image_Edit_4props_Klein.json) — v1 | — |
| [Integration_sujet_environnement_Qwen.json](Integration_sujet_environnement_Qwen.json) — intégration sujet dans un environnement | — |
| [Qwen_relight.json](Qwen_relight.json) — relighting | — |

### Environnements 360 / blockout
| Workflow | Prompt Set |
|---|---|
| [env360_pipeline_4etapes.json](env360_pipeline_4etapes.json) — pipeline 360 en 4 étapes | — |
| [qwen_INT_environnement_v2_360_first.json](qwen_INT_environnement_v2_360_first.json) — intérieur, 360 d'abord | — |
| [qwen_environnement_blockout_360.json](qwen_environnement_blockout_360.json) — depuis un blockout 3D | — |
| [qwen_environnement_4vues_360_cloud_v3.json](qwen_environnement_4vues_360_cloud_v3.json) — 4 vues + 360, exécution cloud (v3) | — |
| [qwen_environnement_4vues_360_cloud_v2.json](qwen_environnement_4vues_360_cloud_v2.json) · [cloud v1](qwen_environnement_4vues_360_cloud.json) · [local](qwen_environnement_4vues_360.json) | — |

### Vidéo (image-to-video, FX, SFX)
| Workflow | Prompt Set |
|---|---|
| [JB_LTX23_FLF_EDIT_FX_SFX_v3.json](JB_LTX23_FLF_EDIT_FX_SFX_v3.json) — LTX 2.3, first/last frame + edit + FX + SFX | [CONTEXT](JB_LTX23_FLF_EDIT_FX_SFX_v3/CONTEXT_prompt-set_LTX23_WF-v3.md) |
| [JB_LTX23_FLF_EDIT_FX_SFX_v2.json](JB_LTX23_FLF_EDIT_FX_SFX_v2.json) — v2 | — |
| [JB_LTX23_I2V_FX_SFX.json](JB_LTX23_I2V_FX_SFX.json) — LTX 2.3 image-to-video | — |
| [image_to_video_MiniMaxH3.json](image_to_video_MiniMaxH3.json) — MiniMax / Hailuo H3 | [CONTEXT](image_to_video_MiniMaxH3/CONTEXT_prompt-set_H3_ImageToVideo_local_I2V.md) |
| [H3_blocking_to_video.json](H3_blocking_to_video.json) — blocking 3D → vidéo | — |

### 3D (image-to-3D, remesh, UV, découpe en pièces)
| Workflow | Prompt Set |
|---|---|
| [3D2UV_UnwrapMesh_v01.json](3D2UV_UnwrapMesh_v01.json) — dépliage UV auto d'un GLB → GLB avec UV + layout PNG + AO, 100 % natif, Cloud | [CONTEXT](3D2UV_UnwrapMesh_v01/CONTEXT_prompt-set_3D2UV_UnwrapMesh_v01.md) |
| [3D2Remesh_NativeDC_v01.json](3D2Remesh_NativeDC_v01.json) — remesh étanche (Dual Contouring) + décimation au poly count d'un GLB → GLB triangulé, 100 % natif, Cloud | [CONTEXT](3D2Remesh_NativeDC_v01/CONTEXT_prompt-set_3D2Remesh_NativeDC_v01.md) |
| [3D2Parts_TripoSmartSegment_v01.json](3D2Parts_TripoSmartSegment_v01.json) — découpe sémantique d'un GLB en pièces nommées (nombre visé via prompt) + **Cap ON/OFF** (complétion des pièces) → GLB une pièce = un objet, nœuds Partner Tripo (crédits), Cloud | [CONTEXT](3D2Parts_TripoSmartSegment_v01/CONTEXT_prompt-set_3D2Parts_TripoSmartSegment_v01.md) |
| [i23d_Pixal3D_v02.json](i23d_Pixal3D_v02.json) — multivue (face, côté, dos) → GLB triangulé manifold **paroi simple (SDF)** sans UV, poly count cible, hauteur dans le nom + script Blender, Pixal3D natif, Cloud | [CONTEXT](i23d_Pixal3D_v02/CONTEXT_prompt-set_i23d_Pixal3D_v02.md) |

### Text-to-image
| Workflow | Prompt Set |
|---|---|
| [text_to_image_flux2dev.json](text_to_image_flux2dev.json) — Flux 2 dev | — |

---

## Utilisation

1. **Charger un workflow** : dans ComfyUI, `Workflow > Open` et sélectionner le `.json`.
2. **Installer les dépendances** : ouvrir le ComfyUI Manager → `Install Missing Custom Nodes`, puis télécharger les checkpoints/LoRA listés dans le README du workflow.
3. **Générer les prompts** : ouvrir une conversation Claude, coller le `CONTEXT_prompt-set_*.md` correspondant, puis décrire le brief et joindre les moodboards. Claude renvoie les champs prêts à coller.
