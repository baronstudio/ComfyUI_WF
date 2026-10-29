#!/usr/bin/env python3
"""Builder for t2hdri_INT_Compare3_SDXL360_Qwen360_Klein360_v01 (ComfyUI UI-format JSON).
Étape 1 : banc d'essai qualité — 3 blocs (SDXL 360 Diffusion / Qwen-Image-2512 + qwen-360 / Flux.2 Klein 9B base + LoRA crafiq)
alimentés par le même prompt, les mêmes barrettes, la même seed et la même résolution. Génération 2048x1024 seule (pas de raccord/upscale/EXR)."""
import json, sys, os

WF = "t2hdri_INT_Compare3_SDXL360_Qwen360_Klein360_v01"
OUT = sys.argv[1] if len(sys.argv) > 1 else f"{WF}.json"

nodes, links = [], []
_nid, _lid = [0], [0]
GROUPS = {}          # group key -> list of node ids
_cur = [None]

def grp(key):
    _cur[0] = key
    GROUPS.setdefault(key, [])

def add(type_, title, pos, size, widgets=None, inputs=(), outputs=(), color=None, mode=0):
    _nid[0] += 1
    n = {"id": _nid[0], "type": type_, "pos": list(pos), "size": list(size), "flags": {}, "order": 0,
         "mode": mode, "inputs": [], "outputs": [], "properties": {"Node name for S&R": type_},
         "widgets_values": widgets if widgets is not None else []}
    for name, t, kind in inputs:
        e = {"localized_name": name, "name": name, "type": t, "link": None}
        if kind == "widget": e["widget"] = {"name": name}
        if kind == "opt": e["shape"] = 7
        if kind == "autogrow": e["label"] = name.split(".")[-1]
        if kind == "autogrow_opt": e["label"] = name.split(".")[-1]; e["shape"] = 7
        n["inputs"].append(e)
    for name, t in outputs:
        n["outputs"].append({"localized_name": name, "name": name, "type": t, "links": []})
    if title: n["title"] = title
    if color: n["color"], n["bgcolor"] = color
    nodes.append(n)
    if _cur[0]: GROUPS[_cur[0]].append(n["id"])
    return n["id"]

def node(i): return nodes[i - 1]

def link(src, src_slot, dst, dst_name):
    _lid[0] += 1
    s, d = node(src), node(dst)
    out = s["outputs"][src_slot]
    inp = next(x for x in d["inputs"] if x["name"] == dst_name)
    assert inp["link"] is None, (dst, dst_name)
    out["links"].append(_lid[0]); inp["link"] = _lid[0]
    links.append([_lid[0], src, src_slot, dst, d["inputs"].index(inp), out["type"]])
    return _lid[0]

C_CTRL = ("#223", "#335"); C_MOD = ("#323", "#535"); C_PRE = ("#233", "#355"); C_PRO = ("#332", "#553")
C_A = ("#322", "#533"); C_B = ("#232", "#353"); C_C = ("#223", "#335")

# ------------------------------------------------------------------ LOCKED TABLES (EN)
# Ambiance (0 morning, 1 day, 2 evening, 3 night) x Sunlight (0..3) -> index = ambiance*4 + sunlight
LIGHT = [
 # morning
 "early morning, overcast pale grey daylight entering softly through the windows, flat cool diffuse light without direct sun, interior lamps providing most of the illumination with a warm glow against the cool window light",
 "early morning, low soft sun entering through the windows, pale warm light and gentle long soft-edged shadows on the floor, cool blue-white shadows, a few lamps lit",
 "early morning, low sun rays entering through the windows as sharp warm beams across the floor and lower walls, long defined shadows of the window frames, dust floating in the light, lamps unnecessary",
 "early morning, bright low sun directly facing the camera through the windows, blinding glare and glowing haze around the window openings, the room interior underexposed and silhouetted, soft rim light on edges, interior lamps barely visible",
 # day
 "midday, white overcast sky, flat soft diffuse daylight through the windows, no cast shadows, even neutral light, interior lamps lit and dominating the dim corners",
 "midday, soft sun through a light haze, gentle daylight entering the windows, soft shadows with blurred edges, neutral white light, interior lamps secondary",
 "midday, strong direct sun rays entering through the windows, bright sharp-edged light patches on the floor and walls, crisp shadows, high contrast, neutral white light, lamps unnecessary",
 "midday, dazzling high sun directly facing the camera through the windows, overexposed glowing window openings, strong glare and bloom, the room underexposed and dark, interior lamps lost in the glare",
 # evening
 "evening, dusk under a grey overcast sky, dim blue-grey light from the windows, warm interior lamps lit and dominating, pools of warm lamplight in the room",
 "evening, low soft sun glow through the windows, warm amber light, soft long shadows, some warm lamps lit",
 "evening, low golden sun rays entering through the windows as sharp orange beams crossing the room, long shadows, deep golden light on the walls, lamps unnecessary",
 "evening, blinding low sun facing the camera through the windows at sunset, orange glare and bloom around the window openings, silhouetted room interior underexposed, faint warm rim light, lamps barely visible",
 # night
 "night, windows dark blue-black, interior lamps lit as the only light, warm pools of artificial light with deep shadows in the corners",
 "night, soft cold moonlight through the windows, pale blue patches on the floor, a few warm lamps lit",
 "night, strong moonlight and bright street light rays entering through the windows, sharp pale-blue beams and long shadows on the floor, lamps very dim",
 "night, a bright street lamp or full moon directly facing the camera through the windows, glowing glare and bloom at the openings, the room underexposed and very dark, lamps off",
]
LIGHT_LABELS_A = ["0 matin", "1 jour", "2 soir", "3 nuit"]
LIGHT_LABELS_S = ["0 aucun soleil direct", "1 soleil doux", "2 rayons marqués", "3 contre-jour éblouissant"]

STATE = [
 "an unfinished bare shell with raw concrete walls and floor, exposed cinder blocks, hanging electrical cables and an exposed concrete ceiling slab, completely empty",
 "a building site at second-fix stage, rough plastered walls partly painted, protective plastic sheets and tarpaulins, tools, paint buckets and ladders, an unfinished dusty floor, bare temporary work lights",
 "a finished empty room, completed finishes, clean painted walls, finished floor, skirting boards and ceiling mouldings, completely empty of furniture and decoration",
 "a fully furnished and decorated room, with sofas, tables, rugs, lamps, shelves, curtains and decorative objects",
]
STATE_LABELS = ["0 gros œuvre", "1 second œuvre", "2 vide, finitions terminées", "3 meublé et décoré"]

STYLE = [
 ". Decor style: modern, concrete, glass and steel materials, geometric shapes, straight lines, open space, limited decoration",
 ". Decor style: contemporary, natural materials and textures, light and deep tones in balance, curved forms, curated decoration, clean lines, a minimalist dining table in a noble material as centrepiece",
 ". Decor style: Scandinavian, light wood, textiles and rugs, light airy palette, simple forms, light proportions, well-placed lighting, only useful objects",
 ". Decor style: mid-century modern, dark wood, tapered legs, organic lines, comfortable seating, a few bold colours and graphic patterns",
 ". Decor style: industrial, steel, wood, brick, concrete and glass, raw materials, deep mineral tones, sturdy functional furniture",
 ". Decor style: bohemian, mixed materials and textiles, varied colours and patterns, accumulated objects, souvenirs and mismatched pieces",
 ". Decor style: vintage, wood, Formica, metal and textured fabrics, deep colours, furniture and objects from the 1950s to the 1970s with patina and wear",
 ". Decor style: Art Deco, wood, glass, brass and velvet, geometric compositions, symmetry, worked lines",
 ". Decor style: English country, painted panelling, wallpaper, floral or checked fabrics, muted coherent palette, aged antique furniture and patinated objects",
 ". Decor style: holiday house, wood, stone, linen and natural fibres, soft tones, light and calm atmosphere, subtle sea references",
 ". Decor style: wabi-sabi, raw wood, stone, ceramics and linen, irregular surfaces, handmade objects, visible signs of age",
 ". Decor style: Kinfolk, wood, linen and ceramics, muted low-contrast tones, fresh or dried plants, books, old jars and terracotta vases, a solid wood table",
 ". Decor style: Haussmann, herringbone parquet, marble fireplaces, mouldings, high ceilings, large windows, contemporary furniture scaled to the space",
 ". Decor style: contemporary classic, precious period elements mixed with contemporary pieces, clean-lined modern furniture against traditional architecture",
 ". Decor style: warm minimalism, textured relief-rich materials such as travertine, light wood and bouclé, soft neutral beige tones, simple lines, arches and rounded forms",
 "",   # 15 = no style (Mobilier < 3)
]
STYLE_LABELS = ["0 moderne", "1 contemporain", "2 scandinave", "3 mid-century", "4 industriel", "5 bohème", "6 vintage", "7 art déco",
                "8 campagne anglaise", "9 maison de vacances", "10 wabi-sabi", "11 kinfolk", "12 haussmannien", "13 classique contemporain", "14 minimalisme chaleureux"]

HEIGHT = [
 "captured from a seated viewpoint about 1 metre above the floor, table height, the floor close and prominent in the lower half, objects seen from low, the ceiling high above, horizon exactly at mid-height",
 "captured from a standing viewpoint about 1.6 metres above the floor, natural human eye level, horizon exactly at mid-height",
 "captured from about 2.8 metres above the floor, just below the ceiling, looking slightly down on the room, floor and objects seen from above, the ceiling close above, horizon exactly at mid-height",
]
HEIGHT_LABELS = ["0 ≈ 1 m (assis)", "1 ≈ 1,6 m (debout)", "2 ≈ 2,8 m (sous plafond)"]

def fixed_table(lines):
    w = max(len(l) for l in lines)
    return "\n".join(l.ljust(w) for l in lines), w
LIGHT_TXT, W_L = fixed_table(LIGHT)
STATE_TXT, W_M = fixed_table(STATE)
STYLE_TXT, W_Y = fixed_table(STYLE)
HEIGHT_TXT, W_H = fixed_table(HEIGHT)

BASE_PROMPT = ("a large rectangular living room with a high ceiling, three tall arched windows on one long wall and a wide glazed opening on the opposite wall, "
               "a door in one short wall and a chimney breast in the other, shot on a full-frame mirrorless camera with a 14 mm lens, sharp realistic photograph")
RULES360 = ("Full spherical interior view from inside the room, a single coherent room, continuous floor at the bottom, continuous ceiling at the top, "
            "walls that connect all around, seamless left and right edges, straight horizon in the exact middle, the same lighting, colours and time of day everywhere. "
            "Sharp photographic detail, natural textures, real camera photograph, not an illustration, not a 3D render. An unoccupied room, no text, no frame.")
TRIG_SDXL = "equirectangular 360 view, 360 panorama, photograph of"
TRIG_QWEN = "equirectangular 360 degree panorama with equirectangular projection, photograph of"
TRIG_KLEIN = "Equirectangular 360 panorama, photograph of"
NEG_SDXL = ("illustration, cartoon, drawing, painting, anime, 3d render, cgi, video game, people, person, human, text, watermark, logo, frame, "
            "blurry, lowres, deformed, bad perspective, duplicated furniture, mirrored duplicate, visible seam")
NEG_QWEN = ("illustration, cartoon, drawing, painting, anime, 3d render, cgi, people, text, watermark, frame, blurry")

MANUAL = f"""# {WF} — Mode d'emploi

**Banc d'essai (étape 1)** : trois solutions de génération d'**environment map INTÉRIEURE 360°** (équirectangulaire 2:1, **2048 × 1024**) alimentées par **le même prompt, les mêmes barrettes, la même seed et la même résolution**, pour comparer la qualité de rendu. Rien d'autre : pas de raccord, pas d'upscale, pas d'EXR (étape 3, sur la solution retenue).

| Bloc | Modèle | LoRA / checkpoint 360 | Licence (à vérifier) |
|---|---|---|---|
| **A** | SDXL | checkpoint `sdxl_360_diffusion` (+ LoRA `View360` / 360Redmond, OFF par défaut) | MIT / OpenRAIL |
| **B** | Qwen-Image-2512 | LoRA `qwen-360-diffusion` v2 + Lightning (mode rapide validé) | à vérifier |
| **C** | Flux.2 Klein 9B **base** | LoRA `flux-2-klein-9b-360-panorama-lora` (crafiq) | Klein 9B = FLUX Non-Commercial |

## Entrées (groupe 🎛️ CONTRÔLES)
1. **✏️ Prompt de base (EN)** : type de pièce, architecture, volumes, ouvertures, boîtier photo. Rien sur la lumière, le mobilier, le style ni la hauteur. Éviter les finitions précises (parquet, marbre…) qui contrediraient *Mobilier* 0–1.
2. **🎛️ Ambiance (0–3)** : 0 matin · 1 jour · 2 soir · 3 nuit.
3. **🎛️ Ensoleillement (0–3)** : 0 aucun soleil direct · 1 soleil doux · 2 rayons marqués · 3 contre-jour éblouissant (intérieur sous-exposé). Table 4 × 4 = 16 lignes, pondérée par l'ambiance.
4. **🎛️ Mobilier (0–3)** : 0 gros œuvre · 1 second œuvre · 2 vide, finitions terminées · 3 meublé et décoré. Aucun personnage.
5. **🎛️ Style déco (0–14)** : actif seulement si Mobilier = 3 (sinon fragment vide). 0 moderne · 1 contemporain · 2 scandinave · 3 mid-century · 4 industriel · 5 bohème · 6 vintage · 7 art déco · 8 campagne anglaise · 9 maison de vacances · 10 wabi-sabi · 11 kinfolk · 12 haussmannien · 13 classique contemporain · 14 minimalisme chaleureux.
6. **🎛️ Hauteur (0–2)** : 0 ≈ 1 m · 1 ≈ 1,6 m · 2 ≈ 2,8 m.
7. **Seed / Largeur / Hauteur** partagés. Réglages par modèle (steps, CFG, force LoRA) dans le même groupe.

Les textes des barrettes sont **verrouillés** (tables à largeur fixe lues par position) : ne pas les éditer à la main, régénérer le WF.

## Protocole de test
1. Garder les valeurs par défaut, lancer, noter le temps de chaque bloc.
2. Comparer les 3 sorties (géométrie des lignes, raccord gauche/droite, plafond / sol, fenêtres, cohérence de la pièce, respect des barrettes).
3. Refaire avec 3 à 4 combinaisons : (Ambiance 1, Soleil 2, Mobilier 3, Style 12) · (Ambiance 3, Soleil 0, Mobilier 2) · (Ambiance 2, Soleil 3, Mobilier 0) · même chose en changeant la seed.
4. **Ctrl+M** sur un groupe = couper ce bloc (économise du temps et de la VRAM). Un bloc coupé ne sera pas exécuté.
5. Test optionnel : bloc A avec la LoRA View360 activée (Ctrl+B sur le nœud ➕).

## Modèles (à déposer dans Comfy Cloud / ComfyUI)
- A : `checkpoints/sdxl_360_diffusion.safetensors` (ProGamerGov/sdxl-360-diffusion, 7,11 Go) · `loras/View360.safetensors` (artificialguybr/360Redmond)
- B : `diffusion_models/qwen_image_2512_fp8_e4m3fn.safetensors` · `loras/Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors` · `loras/qwen-360-diffusion-2512-int8-bf16-v2.safetensors` · `text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors` · `vae/qwen_image_vae.safetensors`
- C : `diffusion_models/flux-2-klein-base-9b-fp8.safetensors` · `loras/flux-2-klein-9b-360-panorama-lora.safetensors` (crafiq) · `text_encoders/qwen_3_8b_fp8mixed.safetensors` · `vae/full_encoder_small_decoder.safetensors`

## Limites
- Le LoRA 360 place la source lumineuse principale au centre : l'orientation se fait dans Blender.
- Même prompt en texte naturel sur les 3 blocs (pas de JSON FLUX.2 à ce stade) : chaque bloc ajoute seulement son *trigger*.
- Prompt négatif : actif seulement sur A (SDXL) ; B est à CFG 1 (sans effet) ; C n'en utilise pas.
- Les fichiers A et C ne sont pas des modèles Comfy Cloud standard : à importer avant le premier run.
"""

# ================================================================== NODES
grp(None)
add("MarkdownNote", "📖 Mode d'emploi", (40, 40), (520, 1900), [MANUAL])

# ---- 🎛️ CONTRÔLES
grp("ctrl"); cx, y = 620, 60
def ctrl(type_, title, widgets, h):
    global y
    i = add(type_, title, (cx, y), (320, h), widgets, outputs=[(type_.replace("Primitive", "").upper(), type_.replace("Primitive", "").upper())], color=C_CTRL)
    y += h + 24
    return i
N_BASE = add("PrimitiveStringMultiline", "✏️ Prompt de base (EN) : pièce, architecture, volumes, ouvertures, boîtier", (cx, y), (320, 260), [BASE_PROMPT], outputs=[("STRING", "STRING")], color=C_PRO)
y += 260 + 24
N_AMB  = ctrl("PrimitiveInt", "🎛️ Ambiance lumineuse (0–3) : matin · jour · soir · nuit", [1, "fixed"], 82)
N_SUN  = ctrl("PrimitiveInt", "🎛️ Ensoleillement (0–3) : aucun · doux · rayons · contre-jour", [2, "fixed"], 82)
N_MOB  = ctrl("PrimitiveInt", "🎛️ Mobilier (0–3) : gros œuvre · second œuvre · vide · meublé", [3, "fixed"], 82)
N_STY  = ctrl("PrimitiveInt", "🎛️ Style déco (0–14), actif si Mobilier = 3", [12, "fixed"], 82)
N_HGT  = ctrl("PrimitiveInt", "🎛️ Hauteur de prise de vue (0–2) : 1 m · 1,6 m · 2,8 m", [1, "fixed"], 82)
N_SEED = ctrl("PrimitiveInt", "🎛️ Seed (commune aux 3 blocs)", [360001, "fixed"], 82)
N_W    = ctrl("PrimitiveInt", "🎛️ Largeur (2048)", [2048, "fixed"], 82)
N_H    = ctrl("PrimitiveInt", "🎛️ Hauteur image (1024)", [1024, "fixed"], 82)
N_A_ST = ctrl("PrimitiveInt", "A SDXL — Steps (25–40)", [30, "fixed"], 82)
N_A_CF = ctrl("PrimitiveFloat", "A SDXL — CFG (5–8)", [6.0], 58)
N_A_LS = ctrl("PrimitiveFloat", "A SDXL — Force LoRA View360 (si activée)", [0.8], 58)
N_B_ST = ctrl("PrimitiveInt", "B Qwen — Steps (8, Lightning)", [8, "fixed"], 82)
N_B_CF = ctrl("PrimitiveFloat", "B Qwen — CFG (1.0 avec Lightning)", [1.0], 58)
N_C_ST = ctrl("PrimitiveInt", "C Klein 9B base — Steps (20–30)", [20, "fixed"], 82)
N_C_CF = ctrl("PrimitiveFloat", "C Klein 9B base — CFG (3–5)", [5.0], 58)
N_C_LS = ctrl("PrimitiveFloat", "C Klein — Force LoRA 360", [1.0], 58)

# ---- PRESETS
grp("pre"); px_tab, px_math, px_sub = 1040, 1480, 1820
def table(title, pos, h, text):
    return add("PrimitiveStringMultiline", title, pos, (400, h), [text], outputs=[("STRING", "STRING")], color=C_PRE)
def math(title, pos, expr, n):
    """n = number of used sources; like the reference WF: n+1 autogrow inputs, the last one optional."""
    inputs = []
    for k, nm in enumerate("abcd"[:n + 1]):
        inputs.append((f"values.{nm}", "FLOAT,INT,BOOLEAN", "autogrow_opt" if k == n else "autogrow"))
    return add("ComfyMathExpression", title, pos, (320, 120), [expr], inputs=inputs,
               outputs=[("FLOAT", "FLOAT"), ("INT", "INT"), ("BOOL", "BOOLEAN")], color=C_PRE)
def substr(title, pos):
    return add("StringSubstring", title, pos, (300, 150), ["", 0, 0],
               inputs=[("string", "STRING", "widget"), ("start", "INT", "widget"), ("end", "INT", "widget")], outputs=[("STRING", "STRING")], color=C_PRE)
def trim(title, pos):
    return add("StringTrim", title, pos, (300, 80), ["", "Both"], inputs=[("string", "STRING", "widget")], outputs=[("STRING", "STRING")], color=C_PRE)

EXPRS = {}   # for the validator
def preset_block(key, y0, h_tab, title, text, w, srcs, idx_expr):
    t = table(title, (px_tab, y0), h_tab, text)
    es = f"({idx_expr})*{w+1}"
    ee = f"({idx_expr})*{w+1}+{w}"
    EXPRS[key] = (idx_expr, w, len(srcs))
    ms = math(f"Début = index borné × {w+1}", (px_math, y0), es, len(srcs))
    me = math(f"Fin = début + {w}", (px_math, y0 + 170), ee, len(srcs))
    for m in (ms, me):
        for k, s in enumerate(srcs):
            link(s, 0, m, "values." + "abcd"[k])
    sb = substr("Ligne de la table (position)", (px_sub, y0))
    tr = trim("Texte du preset (sans remplissage)", (px_sub, y0 + 190))
    link(t, 0, sb, "string"); link(ms, 1, sb, "start"); link(me, 1, sb, "end"); link(sb, 0, tr, "string")
    return tr

T_LIGHT = preset_block("light", 60, 420, "🔒 Table LUMIÈRE = Ambiance × Ensoleillement (16 lignes, largeur fixe — ne pas éditer)", LIGHT_TXT, W_L, [N_AMB, N_SUN], "min(max(a,0),3)*4+min(max(b,0),3)")
T_STATE = preset_block("state", 540, 270, "🔒 Table MOBILIER (4 lignes, largeur fixe — ne pas éditer)", STATE_TXT, W_M, [N_MOB], "min(max(a,0),3)")
T_STYLE = preset_block("style", 870, 420, "🔒 Table STYLE DÉCO (15 + 1 ligne vide, actif si Mobilier = 3 — ne pas éditer)", STYLE_TXT, W_Y, [N_MOB, N_STY], "(a>=3)*min(max(b,0),14)+(a<3)*15")
T_HGT = preset_block("height", 1350, 270, "🔒 Table HAUTEUR DE PRISE DE VUE (3 lignes, largeur fixe — ne pas éditer)", HEIGHT_TXT, W_H, [N_HGT], "min(max(a,0),2)")

# ---- PROMPT
grp("pro"); qx1, qx2, qx3 = 2240, 2640, 3040
def concat(title, pos, delim, a="", b="", mode=0, color=C_PRO):
    return add("StringConcatenate", title, pos, (340, 150), [a, b, delim],
               inputs=[("string_a", "STRING", "widget"), ("string_b", "STRING", "widget")], outputs=[("STRING", "STRING")], color=color, mode=mode)
N_C1 = concat("Base + lumière (barrette)", (qx1, 60), ". Lighting: ")
N_C2 = concat("+ État du lieu / mobilier (barrette)", (qx1, 240), ". Room state: ")
N_C3 = concat("+ Style déco (barrette, vide si Mobilier < 3)", (qx1, 420), "")
N_C4 = concat("+ Hauteur de prise de vue (barrette)", (qx1, 600), ". Camera height: ")
N_C5 = concat("+ Consignes 360 intérieures (fixes)", (qx1, 780), "\n\n", b=RULES360)
N_BODY_PREV = add("PreviewAny", "👁️ Corps de prompt commun (3 blocs)", (qx1, 970), (340, 320), [], inputs=[("source", "*", "link")], color=C_PRO)
link(N_BASE, 0, N_C1, "string_a"); link(T_LIGHT, 0, N_C1, "string_b")
link(N_C1, 0, N_C2, "string_a"); link(T_STATE, 0, N_C2, "string_b")
link(N_C2, 0, N_C3, "string_a"); link(T_STYLE, 0, N_C3, "string_b")
link(N_C3, 0, N_C4, "string_a"); link(T_HGT, 0, N_C4, "string_b")
link(N_C4, 0, N_C5, "string_a")      # string_b = fixed rules (widget)
link(N_C5, 0, N_BODY_PREV, "source")
N_TA = concat("A · trigger SDXL 360 + corps", (qx2, 60), " ", a=TRIG_SDXL)
N_TB = concat("B · trigger Qwen 360 + corps", (qx2, 240), " ", a=TRIG_QWEN)
N_TC = concat("C · trigger Klein 360 + corps", (qx2, 420), " ", a=TRIG_KLEIN)
for t in (N_TA, N_TB, N_TC): link(N_C5, 0, t, "string_b")
N_PA = add("PreviewAny", "👁️ Prompt A (SDXL)", (qx3, 60), (340, 220), [], inputs=[("source", "*", "link")], color=C_PRO)
N_PB = add("PreviewAny", "👁️ Prompt B (Qwen)", (qx3, 310), (340, 220), [], inputs=[("source", "*", "link")], color=C_PRO)
N_PC = add("PreviewAny", "👁️ Prompt C (Klein)", (qx3, 560), (340, 220), [], inputs=[("source", "*", "link")], color=C_PRO)
link(N_TA, 0, N_PA, "source"); link(N_TB, 0, N_PB, "source"); link(N_TC, 0, N_PC, "source")

# ---- BLOCK helpers
def clipenc(title, pos, text, h=130, color=None):
    return add("CLIPTextEncode", title, pos, (400, h), [text], inputs=[("clip", "CLIP", "link"), ("text", "STRING", "widget")], outputs=[("CONDITIONING", "CONDITIONING")], color=color)
def ksampler(title, pos, sampler, sched, color):
    return add("KSampler", title, pos, (400, 262), [360001, "fixed", 20, 1.0, sampler, sched, 1.0],
               inputs=[("model", "MODEL", "link"), ("positive", "CONDITIONING", "link"), ("negative", "CONDITIONING", "link"), ("latent_image", "LATENT", "link"),
                       ("seed", "INT", "widget"), ("steps", "INT", "widget"), ("cfg", "FLOAT", "widget")], outputs=[("LATENT", "LATENT")], color=color)
def decode(pos, color):
    return add("VAEDecode", "", pos, (400, 46), [], inputs=[("samples", "LATENT", "link"), ("vae", "VAE", "link")], outputs=[("IMAGE", "IMAGE")], color=color)
def save(title, pos, prefix, color):
    return add("SaveImage", title, pos, (400, 300), [prefix], inputs=[("images", "IMAGE", "link")], color=color)

# ================= BLOCK A — SDXL 360 Diffusion
grp("A"); ax = 3500; ay = 60
N_A_CK = add("CheckpointLoaderSimple", "A · SDXL 360 Diffusion (checkpoint)", (ax, ay), (400, 110), ["sdxl_360_diffusion.safetensors"], outputs=[("MODEL", "MODEL"), ("CLIP", "CLIP"), ("VAE", "VAE")], color=C_A); ay += 134
N_A_LR = add("LoraLoader", "➕ LoRA View360 / 360Redmond (OFF — Ctrl+B pour activer)", (ax, ay), (400, 160), ["View360.safetensors", 0.8, 0.8],
             inputs=[("model", "MODEL", "link"), ("clip", "CLIP", "link"), ("strength_model", "FLOAT", "widget"), ("strength_clip", "FLOAT", "widget")],
             outputs=[("MODEL", "MODEL"), ("CLIP", "CLIP")], color=C_A, mode=4); ay += 184
N_A_POS = clipenc("A · PROMPT (positif)", (ax, ay), "", 130, C_A); ay += 154
N_A_NEG = clipenc("A · Négatif SDXL (CFG > 1)", (ax, ay), NEG_SDXL, 180, C_A); ay += 204
N_A_LAT = add("EmptyLatentImage", "A · Latent vide 2048 × 1024", (ax, ay), (400, 130), [2048, 1024, 1],
              inputs=[("width", "INT", "widget"), ("height", "INT", "widget")], outputs=[("LATENT", "LATENT")], color=C_A); ay += 154
N_A_KS = ksampler("A · KSampler SDXL (dpmpp_2m / karras)", (ax, ay), "dpmpp_2m", "karras", C_A); ay += 286
N_A_DEC = decode((ax, ay), C_A); ay += 70
N_A_SAVE = save("💾 A · SDXL 360 — sortie", (ax, ay), f"{WF}/A_SDXL360", C_A)
link(N_A_CK, 0, N_A_LR, "model"); link(N_A_CK, 1, N_A_LR, "clip"); link(N_A_LR, 1, N_A_POS, "clip"); link(N_A_LR, 1, N_A_NEG, "clip")
link(N_A_LS, 0, N_A_LR, "strength_model"); link(N_A_LS, 0, N_A_LR, "strength_clip")
link(N_TA, 0, N_A_POS, "text"); link(N_W, 0, N_A_LAT, "width"); link(N_H, 0, N_A_LAT, "height")
link(N_A_LR, 0, N_A_KS, "model"); link(N_A_POS, 0, N_A_KS, "positive"); link(N_A_NEG, 0, N_A_KS, "negative"); link(N_A_LAT, 0, N_A_KS, "latent_image")
link(N_SEED, 0, N_A_KS, "seed"); link(N_A_ST, 0, N_A_KS, "steps"); link(N_A_CF, 0, N_A_KS, "cfg")
link(N_A_KS, 0, N_A_DEC, "samples"); link(N_A_CK, 2, N_A_DEC, "vae"); link(N_A_DEC, 0, N_A_SAVE, "images")

# ================= BLOCK B — Qwen-Image-2512 + qwen-360-diffusion
grp("B"); bx = 4000; by = 60
N_B_UN = add("UNETLoader", "B · Qwen-Image-2512 (diffusion)", (bx, by), (400, 82), ["qwen_image_2512_fp8_e4m3fn.safetensors", "default"], outputs=[("MODEL", "MODEL")], color=C_B); by += 106
N_B_L1 = add("LoraLoaderModelOnly", "B · LoRA Lightning 2512 — 4 steps", (bx, by), (400, 82), ["Qwen-Image-2512-Lightning-4steps-V1.0-fp32.safetensors", 1.0], inputs=[("model", "MODEL", "link")], outputs=[("MODEL", "MODEL")], color=C_B); by += 106
N_B_L2 = add("LoraLoaderModelOnly", "B · LoRA qwen-360-diffusion 2512 v2", (bx, by), (400, 82), ["qwen-360-diffusion-2512-int8-bf16-v2.safetensors", 1.0], inputs=[("model", "MODEL", "link")], outputs=[("MODEL", "MODEL")], color=C_B); by += 106
N_B_AU = add("ModelSamplingAuraFlow", "B · AuraFlow 3.1", (bx, by), (400, 58), [3.1], inputs=[("model", "MODEL", "link")], outputs=[("MODEL", "MODEL")], color=C_B); by += 82
N_B_CL = add("CLIPLoader", "B · Text encoder Qwen2.5-VL 7B", (bx, by), (400, 106), ["qwen_2.5_vl_7b_fp8_scaled.safetensors", "qwen_image", "default"], outputs=[("CLIP", "CLIP")], color=C_B); by += 130
N_B_VA = add("VAELoader", "B · VAE Qwen Image", (bx, by), (400, 58), ["qwen_image_vae.safetensors"], outputs=[("VAE", "VAE")], color=C_B); by += 82
N_B_POS = clipenc("B · PROMPT (positif)", (bx, by), "", 130, C_B); by += 154
N_B_NEG = clipenc("B · Négatif (sans effet à CFG 1)", (bx, by), NEG_QWEN, 130, C_B); by += 154
N_B_LAT = add("EmptySD3LatentImage", "B · Latent vide 2048 × 1024", (bx, by), (400, 130), [2048, 1024, 1], inputs=[("width", "INT", "widget"), ("height", "INT", "widget")], outputs=[("LATENT", "LATENT")], color=C_B); by += 154
N_B_KS = ksampler("B · KSampler Qwen (euler / simple)", (bx, by), "euler", "simple", C_B); by += 286
N_B_DEC = decode((bx, by), C_B); by += 70
N_B_SAVE = save("💾 B · Qwen 360 — sortie", (bx, by), f"{WF}/B_Qwen360", C_B)
link(N_B_UN, 0, N_B_L1, "model"); link(N_B_L1, 0, N_B_L2, "model"); link(N_B_L2, 0, N_B_AU, "model")
link(N_B_CL, 0, N_B_POS, "clip"); link(N_B_CL, 0, N_B_NEG, "clip"); link(N_TB, 0, N_B_POS, "text")
link(N_W, 0, N_B_LAT, "width"); link(N_H, 0, N_B_LAT, "height")
link(N_B_AU, 0, N_B_KS, "model"); link(N_B_POS, 0, N_B_KS, "positive"); link(N_B_NEG, 0, N_B_KS, "negative"); link(N_B_LAT, 0, N_B_KS, "latent_image")
link(N_SEED, 0, N_B_KS, "seed"); link(N_B_ST, 0, N_B_KS, "steps"); link(N_B_CF, 0, N_B_KS, "cfg")
link(N_B_KS, 0, N_B_DEC, "samples"); link(N_B_VA, 0, N_B_DEC, "vae"); link(N_B_DEC, 0, N_B_SAVE, "images")

# ================= BLOCK C — Flux.2 Klein 9B base + LoRA 360
grp("C"); kx = 4500; ky = 60
N_C_UN = add("UNETLoader", "C · Flux.2 Klein 9B base (fp8)", (kx, ky), (400, 82), ["flux-2-klein-base-9b-fp8.safetensors", "default"], outputs=[("MODEL", "MODEL")], color=C_C); ky += 106
N_C_LR = add("LoraLoaderModelOnly", "C · LoRA 360 panorama (crafiq)", (kx, ky), (400, 82), ["flux-2-klein-9b-360-panorama-lora.safetensors", 1.0], inputs=[("model", "MODEL", "link"), ("strength_model", "FLOAT", "widget")], outputs=[("MODEL", "MODEL")], color=C_C); ky += 106
N_C_CL = add("CLIPLoader", "C · Text encoder Qwen3 8B", (kx, ky), (400, 106), ["qwen_3_8b_fp8mixed.safetensors", "flux2", "default"], outputs=[("CLIP", "CLIP")], color=C_C); ky += 130
N_C_VA = add("VAELoader", "C · VAE Flux.2 (small decoder)", (kx, ky), (400, 58), ["full_encoder_small_decoder.safetensors"], outputs=[("VAE", "VAE")], color=C_C); ky += 82
N_C_POS = clipenc("C · PROMPT (positif)", (kx, ky), "", 130, C_C); ky += 154
N_C_NEG = clipenc("C · Négatif (vide : Flux.2 n'en utilise pas)", (kx, ky), "", 100, C_C); ky += 124
N_C_LAT = add("EmptyFlux2LatentImage", "C · Latent vide 2048 × 1024", (kx, ky), (400, 130), [2048, 1024, 1], inputs=[("width", "INT", "widget"), ("height", "INT", "widget")], outputs=[("LATENT", "LATENT")], color=C_C); ky += 154
N_C_SCH = add("Flux2Scheduler", "C · Scheduler Flux.2", (kx, ky), (400, 130), [20, 2048, 1024], inputs=[("steps", "INT", "widget"), ("width", "INT", "widget"), ("height", "INT", "widget")], outputs=[("SIGMAS", "SIGMAS")], color=C_C); ky += 154
N_C_SEL = add("KSamplerSelect", "C · Sampler (euler)", (kx, ky), (400, 58), ["euler"], outputs=[("SAMPLER", "SAMPLER")], color=C_C); ky += 82
N_C_NOI = add("RandomNoise", "C · Bruit (seed fixe)", (kx, ky), (400, 82), [360001, "fixed"], inputs=[("noise_seed", "INT", "widget")], outputs=[("NOISE", "NOISE")], color=C_C); ky += 106
N_C_GD = add("CFGGuider", "C · CFG Guider", (kx, ky), (400, 98), [5.0], inputs=[("model", "MODEL", "link"), ("positive", "CONDITIONING", "link"), ("negative", "CONDITIONING", "link"), ("cfg", "FLOAT", "widget")], outputs=[("GUIDER", "GUIDER")], color=C_C); ky += 122
N_C_SCA = add("SamplerCustomAdvanced", "C · Échantillonnage 360", (kx, ky), (400, 106),
              inputs=[("noise", "NOISE", "link"), ("guider", "GUIDER", "link"), ("sampler", "SAMPLER", "link"), ("sigmas", "SIGMAS", "link"), ("latent_image", "LATENT", "link")],
              outputs=[("output", "LATENT"), ("denoised_output", "LATENT")], color=C_C); ky += 130
N_C_DEC = decode((kx, ky), C_C); ky += 70
N_C_SAVE = save("💾 C · Klein 360 — sortie", (kx, ky), f"{WF}/C_Klein360", C_C)
link(N_C_UN, 0, N_C_LR, "model"); link(N_C_LS, 0, N_C_LR, "strength_model")
link(N_C_CL, 0, N_C_POS, "clip"); link(N_C_CL, 0, N_C_NEG, "clip"); link(N_TC, 0, N_C_POS, "text")
link(N_W, 0, N_C_LAT, "width"); link(N_H, 0, N_C_LAT, "height")
link(N_C_ST, 0, N_C_SCH, "steps"); link(N_W, 0, N_C_SCH, "width"); link(N_H, 0, N_C_SCH, "height")
link(N_SEED, 0, N_C_NOI, "noise_seed")
link(N_C_LR, 0, N_C_GD, "model"); link(N_C_POS, 0, N_C_GD, "positive"); link(N_C_NEG, 0, N_C_GD, "negative"); link(N_C_CF, 0, N_C_GD, "cfg")
link(N_C_NOI, 0, N_C_SCA, "noise"); link(N_C_GD, 0, N_C_SCA, "guider"); link(N_C_SEL, 0, N_C_SCA, "sampler"); link(N_C_SCH, 0, N_C_SCA, "sigmas"); link(N_C_LAT, 0, N_C_SCA, "latent_image")
link(N_C_SCA, 0, N_C_DEC, "samples"); link(N_C_VA, 0, N_C_DEC, "vae"); link(N_C_DEC, 0, N_C_SAVE, "images")

# ================================================================== GROUPS (bounding from members)
TITLES = {
 "ctrl": ("🎛️ CONTRÔLES", "#335"),
 "pre": ("PRESETS VERROUILLÉS — lumière (ambiance × soleil) / mobilier / style / hauteur", "#355"),
 "pro": ("PROMPT — corps commun + trigger propre à chaque modèle", "#553"),
 "A": ("BLOC A — SDXL 360 Diffusion (+ LoRA View360 optionnelle)", "#533"),
 "B": ("BLOC B — Qwen-Image-2512 + qwen-360-diffusion v2", "#353"),
 "C": ("BLOC C — Flux.2 Klein 9B base + LoRA 360 (crafiq)", "#335"),
}
groups = []
for gid, key in enumerate(["ctrl", "pre", "pro", "A", "B", "C"], 1):
    ids = GROUPS[key]
    x0 = min(node(i)["pos"][0] for i in ids) - 20; y0 = 0
    x1 = max(node(i)["pos"][0] + node(i)["size"][0] for i in ids) + 20
    y1 = max(node(i)["pos"][1] + node(i)["size"][1] for i in ids) + 20
    groups.append({"id": gid, "title": TITLES[key][0], "bounding": [x0, y0, x1 - x0, y1 - y0], "color": TITLES[key][1], "font_size": 24, "flags": {}})

# ================================================================== ORDER
deps = {n["id"]: set() for n in nodes}
for l in links: deps[l[3]].add(l[1])
order, seen = [], set()
def visit(i):
    if i in seen: return
    seen.add(i)
    for d in sorted(deps[i]): visit(d)
    order.append(i)
for n in nodes: visit(n["id"])
for k, i in enumerate(order): node(i)["order"] = k

wf = {"id": "t2hdri-int-compare3-sdxl360-qwen360-klein360-v01", "revision": 0, "last_node_id": _nid[0], "last_link_id": _lid[0],
      "nodes": nodes, "links": links, "groups": groups, "config": {}, "extra": {"ds": {"scale": 0.3, "offset": [0, 80]}, "workflow_name": WF}, "version": 0.4}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=1)
print("written", OUT, "nodes", len(nodes), "links", len(links), "widths L/M/Y/H", W_L, W_M, W_Y, W_H)
json.dump({"EXPRS": EXPRS, "LIGHT": LIGHT, "STATE": STATE, "STYLE": STYLE, "HEIGHT": HEIGHT,
           "LIGHT_LABELS_A": LIGHT_LABELS_A, "LIGHT_LABELS_S": LIGHT_LABELS_S, "STATE_LABELS": STATE_LABELS, "STYLE_LABELS": STYLE_LABELS, "HEIGHT_LABELS": HEIGHT_LABELS},
          open(os.path.join(os.path.dirname(OUT) or ".", "presets_int.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
