# 发布前四查 runner（ps-mcp evals）——定义见同目录 regression-checks.md
# 复用自达芬奇同族 runner（语义逐项一致，docs/decisions D7）
# 用法: py run-regression-checks.py [--self-test] [包根目录(默认=本脚本上级)]
# exit: 0 全绿 | 1 指纹 | 2 版本 | 3 台账缺口(④a) | 4 台账结构/版本(④b) | 10 自测失败
import re
import shutil
import sys
import tempfile
from pathlib import Path

MUTATED = "[[PSCP_MUTATED]]"


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# ---------------- ① 指纹回归 ----------------
def parse_fingerprints(root: Path):
    rows = []
    for line in read(root / "evals" / "fingerprint-table.md").splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 4 or not re.fullmatch(r"\d+", cells[0]):
            continue
        rows.append({"id": int(cells[0]), "fp": cells[1], "file": cells[2]})
    return rows


def check_fingerprints(root: Path):
    bad = []
    for row in parse_fingerprints(root):
        path = root / row["file"]
        if not path.exists():
            bad.append((row["id"], f"锚文件不存在: {row['file']}"))
            continue
        content = read(path)
        n = content.count(row["fp"])
        if n == 0:
            bad.append((row["id"], f"指纹缺失(语义本体可能已丢失): {row['fp'][:36]}…"))
        elif n > 1:
            bad.append((row["id"], f"指纹在锚文件内出现 {n} 次(要求唯一): {row['fp'][:36]}…"))
    return bad


# ---------------- ② 版本三处同步 ----------------
def get_versions(root: Path):
    m = re.search(r"^\s*version:\s*[\"']([^\"']+)[\"']", read(root / "SKILL.md"), re.M)
    v_skill = m.group(1) if m else None
    first_line = (read(root / "INSTALL.md").splitlines() or [""])[0]
    m2 = re.search(r"v(\d[\w.\-]*)", first_line)
    v_install = m2.group(1) if m2 else None
    m3 = re.search(r"^## (\d[\w.\-]*)", read(root / "CHANGELOG.md"), re.M)
    v_changelog = m3.group(1) if m3 else None
    return v_skill, v_install, v_changelog


def check_versions(root: Path):
    v_skill, v_install, v_changelog = get_versions(root)
    bad = []
    if not (v_skill == v_install == v_changelog):
        bad.append(f"三处不同步: frontmatter={v_skill} INSTALL={v_install} CHANGELOG={v_changelog}")
    return bad


# ---------------- ③ 部署逐根哈希断言 ----------------
def check_deploy(root: Path):
    if not (root / "deploy-roots.txt").exists():
        return None  # 显式 N/A（不是静默跳过）
    import hashlib
    bad = []
    for line in (root / "deploy-roots.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        target = Path(line)
        if not target.exists():
            bad.append(f"部署根缺失: {line}")
            continue
        for src in root.rglob("*"):
            if src.is_file() and "_probe" not in src.parts and "__pycache__" not in src.parts:
                rel = src.relative_to(root)
                dst = target / rel
                if not dst.exists() or hashlib.sha256(src.read_bytes()).hexdigest() != \
                   hashlib.sha256(dst.read_bytes()).hexdigest():
                    bad.append(f"根 {line} 与源不一致: {rel}")
    return bad


# ---------------- ④a 台账覆盖 / ④b 台账结构 ----------------
def changelog_latest_section(text: str) -> str:
    m = re.search(r"^## .*$", text, re.M)
    if not m:
        return ""
    nxt = text.find("\n## ", m.end())
    return text[m.start(): nxt if nxt != -1 else len(text)]


def fkey(fid: str):
    n, suf = re.match(r"F-(\d+)([ab]?)", fid).groups()
    return (int(n), suf)


def check_ledger_coverage(root: Path):  # ④a
    referenced = set(re.findall(r"F-\d+[ab]?", changelog_latest_section(read(root / "CHANGELOG.md"))))
    # 已登记=台账表首列有独立行（列作用域）；散文/处置栏里提到 F-NN 不算登记
    # （首跑 --self-test P3 抓出的缺陷：全文扫描会把交叉引用误判为已登记）
    ledger_text = read(root / "evals" / "ledger.md")
    registered = set(re.findall(r"^\|\s*(F-\d+[ab]?)\s*\|", ledger_text, re.M))
    missing = sorted(referenced - registered, key=fkey)
    return missing


def check_ledger_structure(root: Path):  # ④b
    ledger = read(root / "evals" / "ledger.md")
    ids = re.findall(r"^\|\s*(F-\d+[ab]?)\s*\|", ledger, re.M)
    problems, seen, prev = [], set(), None
    for fid in ids:
        if fid in seen:
            problems.append(f"台账编号重复: {fid}")
        seen.add(fid)
        if prev and fkey(fid) < fkey(prev):
            problems.append(f"台账编号乱序: {prev} → {fid}")
        prev = fid
    v_skill, _, v_changelog = get_versions(root)
    if v_skill != v_changelog:
        problems.append(f"④b 版本断言: frontmatter {v_skill} != CHANGELOG 最新条目 {v_changelog}")
    return problems


# ---------------- 主流程 ----------------
def run_all(root: Path):
    results = []
    fp_bad = check_fingerprints(root)
    results.append(("①指纹", 1, fp_bad if fp_bad else []))
    ver_bad = check_versions(root)
    results.append(("②版本三处同步", 2, ver_bad))
    dep_bad = check_deploy(root)
    results.append(("③部署断言", 1, dep_bad if dep_bad is not None else "N/A(无 deploy-roots.txt,留痕)"))
    la = check_ledger_coverage(root)
    results.append(("④a台账覆盖", 3, la))
    lb = check_ledger_structure(root)
    results.append(("④b台账结构", 4, lb))

    exit_code = 0
    for name, code, bad in results:
        if bad == []:
            print(f"[PASS] {name}")
        elif bad == "N/A(无 deploy-roots.txt,留痕)" or (isinstance(bad, str) and bad.startswith("N/A")):
            print(f"[N/A ] {name}: {bad}")
        else:
            print(f"[FAIL] {name} (exit {code})")
            for item in bad:
                print(f"       - {item}")
            exit_code = min(exit_code or code, code) if exit_code else code
    print(f"run_all: exit={exit_code}")
    return exit_code


# ---------------- --self-test 反向实测 ----------------
def self_test(root: Path):
    tmp = Path(tempfile.mkdtemp(prefix="pscp_eval_"))
    troot = tmp / "pkg"
    shutil.copytree(root, troot, ignore=shutil.ignore_patterns("__pycache__", "_probe"))
    failures = []
    try:
        # P1: 逐指纹单点删除——探针对象=被保护语义本体(删除其在锚文件中的唯一出现)
        for row in parse_fingerprints(troot):
            path = troot / row["file"]
            content = read(path)
            if content.count(row["fp"]) != 1:
                failures.append(f"P1 #{row['id']}: 指纹在锚文件出现 {content.count(row['fp'])} 次,无法做单点删除探针")
                continue
            path.write_text(content.replace(row["fp"], MUTATED), encoding="utf-8")
            detected = any(bid == row["id"] for bid, _ in check_fingerprints(troot))
            if not detected:
                failures.append(f"P1 #{row['id']}: 单点删除未被检出——指纹无效")
            path.write_text(content, encoding="utf-8")
        # P2: 版本漂移（动态锚：随 frontmatter 当前版本走——硬编码版本号会在升版后静默失效）
        skill = troot / "SKILL.md"
        original = read(skill)
        mutated = re.sub(r'(version:\s*)"[^"]+"', r'\1"9.9.9"', original, count=1)
        if mutated == original:
            failures.append("P2: version 锚未找到,无法构造漂移")
        else:
            skill.write_text(mutated, encoding="utf-8")
            if not check_versions(troot):
                failures.append("P2: 版本漂移未被 ② 检出")
            skill.write_text(original, encoding="utf-8")
        # P3: 台账缺口（动态锚：删除最新 CHANGELOG 条目实际引用的第一个 F-NN——
        # 硬编码 F-1 在升版后引用面变化会静默失效）
        ref_ids = sorted(set(re.findall(r"F-\d+[ab]?",
                          changelog_latest_section(read(troot / "CHANGELOG.md")))), key=fkey)
        if not ref_ids:
            failures.append("P3: 最新 CHANGELOG 条目未引用任何 F-NN,无缺口探针对象")
        else:
            target = ref_ids[0]
            ledger = troot / "evals" / "ledger.md"
            loriginal = read(ledger)
            ledger.write_text("\n".join(l for l in loriginal.splitlines()
                              if not l.strip().startswith("| %s |" % target)),
                              encoding="utf-8")
            if not check_ledger_coverage(troot):
                failures.append(f"P3: 删除台账 {target} 未被 ④a 检出")
            ledger.write_text(loriginal, encoding="utf-8")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        print(f"[FAIL] --self-test (exit 10)")
        for f in failures:
            print(f"       - {f}")
        return 10
    n = len(parse_fingerprints(root))
    print(f"[PASS] --self-test: P1 逐指纹单点删除探针 x{n} 全检出; P2 版本漂移检出; P3 台账缺口检出")
    return 0


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = Path(args[0]).resolve() if args else Path(__file__).resolve().parent.parent
    print(f"ps-mcp evals runner | 包根: {root}")
    code = self_test(root) if "--self-test" in sys.argv else run_all(root)
    sys.exit(code)


if __name__ == "__main__":
    main()
