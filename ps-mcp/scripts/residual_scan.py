# residual_scan.py - ps-mcp residual scanner + inspection plan generator (D14 #9/#10)
# Generalizes the grid-acceptance machine check: scan treated regions of an image,
# rank anomalous segments, emit an inspection plan (1:1 tiles, priority-ordered).
# Usage:
#   py residual_scan.py --image <png> --regions regions.json --out plan.json
# regions.json: {"regions": [
#   {"id": "v744", "type": "line", "axis": 0, "pos": 744, "halfw": 4},
#   {"id": "r1",   "type": "rect", "rect": [l, t, r, b]}, ...]}
# Output plan.json: per-region stats + worst segments + tiles[{id, crop, zoom, priority}]
import argparse
import json
import numpy as np
from PIL import Image


def line_signal(T, c, w=4, off=10):
    center = T[:, c, :].mean(axis=1)
    neigh = (T[:, c - off, :].mean(axis=1) + T[:, c + off, :].mean(axis=1)) / 2
    e = center - neigh
    return e


def scan_line(arr, axis, c, halfw, win=160):
    T = arr if axis == 0 else np.transpose(arr, (1, 0, 2))
    L = T.shape[0]
    e = line_signal(T, c)
    sums = np.convolve(e, np.ones(win), "valid") / win
    order = np.argsort(np.abs(sums))[::-1]
    segs = []
    taken = []
    for i in order:
        s = int(i)
        if any(not (s + win <= a or s >= b) for a, b in taken):
            continue
        taken.append((s, s + win))
        segs.append({"start": s, "end": s + win, "severity": round(float(abs(sums[i])), 2)})
        if len(segs) >= 3:
            break
    segs.sort(key=lambda x: x["start"])
    m, q = float(np.mean(e)), float(np.percentile(e, 25))
    return {"mean": round(m, 2), "p25": round(q, 2), "worst_segments": segs}


def scan_rect(arr, rect, win=160):
    l, t, r, b = rect
    ring = np.concatenate([
        arr[max(0, t - 12):t, l:r, :].reshape(-1, 3),
        arr[b:b + 12, l:r, :].reshape(-1, 3),
        arr[t:b, max(0, l - 12):l, :].reshape(-1, 3),
        arr[t:b, r:r + 12, :].reshape(-1, 3)])
    inner = arr[t:b, l:r, :].astype(float)
    border_mean = ring.mean(axis=0) if len(ring) else np.zeros(3)
    diff = np.abs(inner - border_mean).mean(axis=2)          # per-pixel deviation from ring
    Ht, Wt = diff.shape
    worst = []
    step_y = max(1, Ht // 3)
    step_x = max(1, Wt // 3)
    for gy in range(0, Ht, step_y):
        for gx in range(0, Wt, step_x):
            cell = diff[gy:gy + step_y, gx:gx + step_x]
            worst.append((float(cell.mean()), t + gy, l + gx))
    worst.sort(reverse=True)
    segs = [{"start": int(y), "end": int(x), "severity": round(s, 2)} for s, y, x in worst[:3]]
    return {"mean": round(float(diff.mean()), 2), "p25": round(float(np.percentile(diff, 25)), 2),
            "worst_segments": segs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--regions", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tile", type=int, default=200, help="half-size of 1:1 tile around line/point")
    a = ap.parse_args()
    arr = np.asarray(Image.open(a.image).convert("RGB")).astype(float)
    H, W, _ = arr.shape
    regions = json.load(open(a.regions, encoding="utf-8"))["regions"]
    plan = {"image": a.image, "regions": [], "tiles": []}
    for rg in regions:
        rid = rg["id"]
        if rg["type"] == "line":
            st = scan_line(arr, rg["axis"], rg["pos"], rg.get("halfw", 4))
            st.update({"id": rid, "type": "line", "axis": rg["axis"], "pos": rg["pos"]})
            for k, seg in enumerate(st["worst_segments"]):
                if rg["axis"] == 0:
                    crop = [max(0, rg["pos"] - a.tile), seg["start"],
                            min(W, rg["pos"] + a.tile), seg["end"]]
                else:
                    crop = [seg["start"], max(0, rg["pos"] - a.tile),
                            seg["end"], min(H, rg["pos"] + a.tile)]
                plan["tiles"].append({"id": f"{rid}_seg{k}", "crop": crop,
                                      "zoom": "1:1", "priority": k + 1, "region": rid})
        else:
            st = scan_rect(arr, rg["rect"])
            st.update({"id": rid, "type": "rect", "rect": rg["rect"]})
            l, t, r, b = rg["rect"]
            plan["tiles"].append({"id": f"{rid}_hot", "crop": [l, t, r, b],
                                  "zoom": "1:1", "priority": 1, "region": rid})
        plan["regions"].append(st)
    plan["tiles"].sort(key=lambda t: t["priority"])
    json.dump(plan, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"regions": len(plan["regions"]), "tiles": len(plan["tiles"]),
                      "out": a.out}, ensure_ascii=False))


if __name__ == "__main__":
    main()
