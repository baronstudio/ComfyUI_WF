#!/usr/bin/env python3
import json, sys, itertools, os
path = sys.argv[1]
wf = json.load(open(path, encoding="utf-8"))
pre = json.load(open(os.path.join(os.path.dirname(path) or ".", "presets_int.json"), encoding="utf-8"))
N = {n["id"]: n for n in wf["nodes"]}
errs = []
def E(m): errs.append(m)

assert len(N) == len(wf["nodes"]), "duplicate ids"
if wf["last_node_id"] < max(N): E("last_node_id")
if wf["last_link_id"] < max(l[0] for l in wf["links"]): E("last_link_id")

WLEN = {"KSampler":7,"PrimitiveInt":2,"PrimitiveFloat":1,"PrimitiveBoolean":1,"PrimitiveStringMultiline":1,"ComfyMathExpression":1,"StringSubstring":3,"StringTrim":2,
 "StringConcatenate":3,"PreviewAny":0,"CLIPTextEncode":1,"EmptyLatentImage":3,"EmptySD3LatentImage":3,"EmptyFlux2LatentImage":3,"VAEDecode":0,"SaveImage":1,
 "CheckpointLoaderSimple":1,"LoraLoader":3,"LoraLoaderModelOnly":2,"UNETLoader":2,"CLIPLoader":3,"VAELoader":1,"ModelSamplingAuraFlow":1,"Flux2Scheduler":3,
 "KSamplerSelect":1,"RandomNoise":2,"CFGGuider":1,"SamplerCustomAdvanced":0,"MarkdownNote":1}
CORE = set(WLEN)
for n in N.values():
    if n["type"] not in CORE: E(f"node type outside whitelist: {n['type']}")
    elif len(n["widgets_values"]) != WLEN[n["type"]]: E(f"widgets_values len {n['id']} {n['type']}: {len(n['widgets_values'])} != {WLEN[n['type']]}")

# links
lk = {l[0]: l for l in wf["links"]}
def tmatch(o, i):
    if o == i or i == "*" or o == "*": return True
    return o in i.split(",")
for lid, (_, s, ss, d, ds, t) in lk.items():
    if s not in N or d not in N: E(f"link {lid} dangling"); continue
    out = N[s]["outputs"][ss]; inp = N[d]["inputs"][ds]
    if lid not in out["links"]: E(f"link {lid} missing in output {s}")
    if inp["link"] != lid: E(f"link {lid} missing in input {d}")
    if not tmatch(out["type"], inp["type"]): E(f"type mismatch link {lid}: {out['type']} -> {inp['type']} ({N[s]['type']}->{N[d]['type']}.{inp['name']})")
    if out["type"] != t: E(f"link {lid} recorded type {t} != {out['type']}")
for n in N.values():
    for o in n["outputs"]:
        for l in o["links"]:
            if l not in lk: E(f"output link {l} unknown on {n['id']}")
    for i in n["inputs"]:
        if i["link"] is not None and i["link"] not in lk: E(f"input link unknown on {n['id']}")
        if i["link"] is None and "widget" not in i and i.get("shape") != 7 and n["mode"] != 4:
            E(f"required input unconnected: {n['id']} {n['type']}.{i['name']} ({n.get('title','')})")
# required link inputs for nodes whose inputs are not enumerated (check critical)
need = {"KSampler":["model","positive","negative","latent_image"],"VAEDecode":["samples","vae"],"SaveImage":["images"],"CFGGuider":["model","positive","negative"],
        "SamplerCustomAdvanced":["noise","guider","sampler","sigmas","latent_image"],"CLIPTextEncode":["clip"]}
for n in N.values():
    for r in need.get(n["type"], []):
        if not any(i["name"] == r and i["link"] for i in n["inputs"]): E(f"{n['id']} {n['type']} missing {r}")

# overlap
def box(n): return (n["pos"][0], n["pos"][1], n["pos"][0]+n["size"][0], n["pos"][1]+n["size"][1])
ns = [n for n in N.values() if n["type"] != "MarkdownNote"]
for a, b in itertools.combinations(ns, 2):
    A, B = box(a), box(b)
    if A[0] < B[2] and B[0] < A[2] and A[1] < B[3] and B[1] < A[3]: E(f"overlap {a['id']} {a['type']} / {b['id']} {b['type']}")
# groups: every node (except note) in exactly one group box; group boxes disjoint
gb = [(g["title"], g["bounding"]) for g in wf["groups"]]
for n in ns:
    cx_, cy_ = n["pos"][0] + 1, n["pos"][1] + 1
    inside = [t for t, (x, y, w, h) in gb if x <= n["pos"][0] and n["pos"][0]+n["size"][0] <= x+w and y <= n["pos"][1] and n["pos"][1]+n["size"][1] <= y+h]
    if len(inside) != 1: E(f"node {n['id']} {n['type']} '{n.get('title','')}' in groups {inside}")
for (t1,(x1,y1,w1,h1)),(t2,(x2,y2,w2,h2)) in itertools.combinations(gb, 2):
    if x1 < x2+w2 and x2 < x1+w1: E(f"groups overlap: {t1} / {t2}")

# preset extraction simulation
EX = pre["EXPRS"]
def idx(key, **v):
    expr, w, n = EX[key]
    return eval(expr, {"min": min, "max": max, "floor": int}, v), w
def extract(table_text, key, **v):
    i, w = idx(key, **v)
    s, e = i*(w+1), i*(w+1)+w
    return table_text[s:e].strip()
# rebuild fixed tables exactly as stored in the JSON
tabs = {}
for n in N.values():
    if n["type"] == "PrimitiveStringMultiline" and n.get("title","").startswith("🔒"):
        tabs[n["title"].split()[2]] = n["widgets_values"][0]
def tab(prefix):
    return next(v for k, v in tabs.items() if k.startswith(prefix))
tl, ts, ty, th = tab("LUMIÈRE"), tab("MOBILIER"), tab("STYLE"), tab("HAUTEUR")
cnt = 0
for a, s in itertools.product(range(4), range(4)):
    assert extract(tl, "light", a=a, b=s) == pre["LIGHT"][a*4+s]; cnt += 1
for m in range(4): assert extract(ts, "state", a=m) == pre["STATE"][m]; cnt += 1
for m, st in itertools.product(range(4), range(15)):
    got = extract(ty, "style", a=m, b=st)
    want = pre["STYLE"][st] if m >= 3 else ""
    assert got == want, (m, st, got, want); cnt += 1
for h in range(3): assert extract(th, "height", a=h) == pre["HEIGHT"][h]; cnt += 1
# out-of-range clamps
assert extract(tl, "light", a=9, b=-3) == pre["LIGHT"][3*4+0]
assert extract(ty, "style", a=3, b=99) == pre["STYLE"][14]
assert extract(ty, "style", a=2, b=5) == ""
for row in pre["LIGHT"]+pre["STATE"]+pre["STYLE"]+pre["HEIGHT"]: assert "\n" not in row

# shared params wired to each block
def find(title_part): return next(n for n in N.values() if title_part in n.get("title",""))
for t in ["Seed (commune", "Largeur (2048)", "Hauteur image"]:
    n = find(t); assert len(n["outputs"][0]["links"]) >= 3, t
# every model file named in note exists in loaders
note = next(n for n in N.values() if n["type"] == "MarkdownNote")["widgets_values"][0]
for n in N.values():
    if n["type"] in ("UNETLoader","CheckpointLoaderSimple","LoraLoader","LoraLoaderModelOnly","CLIPLoader","VAELoader"):
        f = n["widgets_values"][0]
        if f not in note: E(f"model file not documented in Mode d'emploi: {f}")

print("nodes", len(N), "links", len(lk), "presets extracted OK:", cnt, "types:", sorted({n['type'] for n in N.values()}))
print("custom packs: none" if not errs else "")
if errs:
    print("ERRORS:"); [print(" -", e) for e in errs]; sys.exit(1)
print("VALIDATION OK")
