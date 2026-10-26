# 破面溯源：3mf 作者原始网格 vs 我们手里 STL 的开放边对照
import zipfile, struct, os
import xml.etree.ElementTree as ET
from collections import Counter

TMF = r"d:\work_dir\小鸭\microduck-replica-cad\打印\microduck-飞特版-BambuStudio2026-10-20.3mf"
PLA = r"d:\work_dir\小鸭\microduck-replica-cad\打印\导出\PLA单"
OUT = r"d:\work_dir\小鸭\_破面溯源.txt"

import sys, io
sys.stdout = io.TextIOWrapper(open(OUT, "wb"), encoding="utf-8")

TARGETS = ["top_head_shell", "power_support", "foot_left", "bottom_head_shell", "trunk_base", "neck_颈部"]

def boundary_edges(tris):
    """tris: list of 3 vertex-tuples(welded ids) -> 只出现一次的边数"""
    cnt = Counter()
    for a, b, c in tris:
        for e in ((a, b), (b, c), (c, a)):
            cnt[tuple(sorted(e))] += 1
    return sum(1 for v in cnt.values() if v == 1)

# ---- 3mf 原始网格（遍历所有 object_*.model）----
z = zipfile.ZipFile(TMF)
model_names = [n for n in z.namelist() if n.endswith(".model")]
print("3mf 内网格文件数:", len(model_names))

# ---- 名字表：config 里 object id -> 真名 ----
cfg = ET.fromstring(z.read("Metadata/model_settings.config"))
names = {}
for o in cfg.iter("object"):
    oid = o.get("id")
    nm = None
    for m in o.findall("metadata"):
        if m.get("key") == "name":
            nm = m.get("value")
    p = o.find("part")
    if p is not None and nm in (None, "1"):
        for m in p.findall("metadata"):
            if m.get("key") == "source_file":
                nm = m.get("value")
    if oid and nm and nm != "1":
        names[oid] = nm

# object 文件：三角数 -> 开放边（面数指纹对接 config）
cnt_map = {}
for mn in model_names:
    root = ET.fromstring(z.read(mn))
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"
    for o in root.iter(ns + "object"):
        mesh = o.find(ns + "mesh")
        if mesh is None or mesh.find(ns + "triangles") is None:
            continue
        tris = [tuple(int(t.get(k)) for k in ("v1", "v2", "v3"))
                for t in mesh.find(ns + "triangles").iter(ns + "triangle")]
        if tris:
            cnt_map[len(tris)] = boundary_edges(tris)

# config：真名 + mesh_stat 面数 → 对接开放边
open3mf = {}
for o in cfg.iter("object"):
    nm = names.get(o.get("id"))
    if not nm:
        continue
    key = next((t for t in TARGETS if nm.startswith(t)), None)
    if key is None or key in open3mf:
        continue
    p = o.find("part")
    if p is None:
        continue
    ms = p.find("mesh_stat")
    if ms is None:
        continue
    fc = int(ms.get("face_count"))
    if fc in cnt_map:
        open3mf[key] = (fc, cnt_map[fc])

# ---- 我们手里的 STL ----
def stl_tris(path):
    with open(path, "rb") as f:
        f.seek(80)
        n = struct.unpack("<I", f.read(4))[0]
        tris = []
        weld = {}
        out = []
        for _ in range(n):
            d = f.read(50)
            v = struct.unpack("<12f", d[:48])
            tri = []
            for k in range(3):
                p = (round(v[3 + k * 3], 4), round(v[4 + k * 3], 4), round(v[5 + k * 3], 4))
                tri.append(weld.setdefault(p, len(weld)))
            out.append(tuple(tri))
    return out

def base_name(fn):
    s = fn[:-4]
    if s.endswith(")") and "(" in s:
        s = s[: s.rfind("(")]
    while s.endswith(".stl"):
        s = s[:-4]
    return s

print(f"\n{'零件':<20}{'3mf三角':>9}{'3mf开放边':>10}{'STL三角':>9}{'STL开放边':>10}  结论")
for fn in sorted(os.listdir(PLA)):
    key = next((t for t in TARGETS if base_name(fn).startswith(t)), None)
    if key is None or key not in open3mf:
        continue
    tris = stl_tris(os.path.join(PLA, fn))
    ob = boundary_edges(tris)
    tn, on = open3mf[key]
    same = "✅ 破面出生即在(与脚本无关)" if (tn, on) == (len(tris), ob) else "❌ 数字不符,需深查"
    print(f"{key:<20}{tn:>9}{on:>10}{len(tris):>9}{ob:>10}  {same}  [{fn}]")
