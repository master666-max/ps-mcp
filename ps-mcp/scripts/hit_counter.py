# hit_counter.py - ps-mcp craft-library hit accounting assistant (D14 #12)
# Reads a hit list (CL-IDs referenced by a finished task) + the craft-library file,
# prints SUGGESTED count updates and promotion alerts. Does NOT edit files —
# the agent applies changes via its editor (append-only discipline, human gate).
# Usage:
#   py hit_counter.py --hits "CL-A-08,CL-X-08" --outcome pass --library ../references/craft-library.md
import argparse
import re


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hits", required=True, help="comma-separated CL-IDs")
    ap.add_argument("--outcome", choices=["pass", "fail"], default="pass")
    ap.add_argument("--library", required=True)
    a = ap.parse_args()

    lib = open(a.library, encoding="utf-8").read()
    # layer detection: rows before "## 2." are 清单项层; after are 候选层
    layer_boundary = lib.find("## 2.")
    ids = [x.strip() for x in a.hits.split(",") if x.strip()]
    alerts = []
    for cid in ids:
        # locate the row mentioning this ID in a table cell
        row = None
        row_pos = -1
        for m2 in re.finditer(r"^\|.*" + re.escape(cid) + r".*$", lib, re.M):
            row, row_pos = m2.group(0), m2.start()
            break
        if not row:
            print(f"{cid}: NOT FOUND in library (check ID)")
            continue
        layer = "清单项层" if 0 <= row_pos < layer_boundary else "候选层"
        m = re.search(r"实战\s*(\d+)\s*次", row)
        if a.outcome == "pass":
            if m:
                n = int(m.group(1)) + 1
                print(f"{cid}（{layer}）: hit recorded -> 实战 {n} 次")
                if layer == "清单项层":
                    print(f"{cid}: 已是清单项（计数更新，无需晋升）")
                elif n >= 2:
                    alerts.append(f"{cid}: 达到晋升线（实战 {n} 次）——人工确认后可升清单项")
                else:
                    print(f"{cid}: 未达晋升线（需 ≥2 次）")
            else:
                print(f"{cid}: 行内无'实战 N 次'计数（可能是 L2 行或规格行），人工核对")
        else:
            print(f"{cid}: outcome=fail —— 不计数；建议把失败模式记入条目或台账（append-only）")
    if alerts:
        print("== 晋升提示 ==")
        for x in alerts:
            print("  " + x)
    print("NOTE: 本工具只输出建议；落账由 agent 用编辑工具执行（append-only，禁 heredoc）。")


if __name__ == "__main__":
    main()
