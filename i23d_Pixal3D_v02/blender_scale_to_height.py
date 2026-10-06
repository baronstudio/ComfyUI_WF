# blender_scale_to_height.py — i23d_Pixal3D_v02
# Met le GLB sorti de ComfyUI à la hauteur cible, pieds au sol, centré sur l'origine.
# Usage : Blender > onglet Scripting > ouvrir ce fichier > renseigner GLB_PATH > Run Script.
#   - La hauteur est lue dans le nom du fichier (..._H180cm_...). Sinon, HEIGHT_CM est utilisé.
#   - GLB_PATH vide : le script s'applique aux objets mesh sélectionnés.
#   - EXPORT = True : réexporte à côté de l'original en "<nom>_scaled.glb".

import bpy, re, os
from mathutils import Vector

GLB_PATH = r""        # ex. r"C:\Users\JB\Downloads\model_H180cm_20000tris_00001_.glb"
HEIGHT_CM = 180.0     # utilisé si le nom du fichier ne contient pas _H<valeur>cm
EXPORT = True

def height_from_name(path):
    m = re.search(r"_H(\d+(?:\.\d+)?)cm", os.path.basename(path))
    return float(m.group(1)) if m else None

if GLB_PATH:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=GLB_PATH)
    objs = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    h = height_from_name(GLB_PATH) or HEIGHT_CM
else:
    objs = [o for o in bpy.context.selected_objects if o.type == "MESH"]
    h = HEIGHT_CM
if not objs:
    raise RuntimeError("Aucun mesh trouvé (GLB_PATH vide et rien de sélectionné).")

# Appliquer les transforms d'import (glTF Y-up -> Blender Z-up) avant de mesurer
bpy.ops.object.select_all(action="DESELECT")
for o in objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = objs[0]
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

pts = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
zmin = min(p.z for p in pts); zmax = max(p.z for p in pts)
cx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2
cy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
s = (h / 100.0) / (zmax - zmin)          # Blender : 1 unité = 1 m

for o in objs:
    for v in o.data.vertices:
        p = o.matrix_world @ v.co
        v.co = o.matrix_world.inverted() @ Vector(((p.x - cx) * s, (p.y - cy) * s, (p.z - zmin) * s))
    o.data.update()
for o in objs:
    o.select_set(True)
bpy.context.scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

print(f"[i23d] {len(objs)} mesh(s) -> hauteur {h:.1f} cm (facteur {s:.4f}), pieds en Z=0")

if EXPORT and GLB_PATH:
    out = os.path.splitext(GLB_PATH)[0] + "_scaled.glb"
    bpy.ops.export_scene.gltf(filepath=out, use_selection=True, export_format="GLB",
                              export_texcoords=False, export_materials="NONE")
    print("[i23d] exporté :", out)
