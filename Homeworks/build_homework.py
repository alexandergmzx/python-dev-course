#!/usr/bin/env python3
"""
Usage
-----
  python3 Homeworks/build_homework.py 1        # build homework 1
  python3 Homeworks/build_homework.py 1 2 3    # build several
  python3 Homeworks/build_homework.py all      # build every gen_hN.py found

Steps (per N)
-------------
  1. Ensure Homeworks/.venv exists; install pyyaml + jupyter if missing
  2. Run Homeworks/gen_hN.py  →  classN/homeworkN.ipynb
  3. Validate notebook JSON   (format version, non-empty cells)
  4. Patch code cells         (strip stray leading backslash-newline)
  5. Syntax-check every code cell via compile()
  6. Print cell inspection summary
  7. Save patched notebook back to disk
"""

import json, pathlib, subprocess, sys, textwrap

REPO   = pathlib.Path(__file__).parent.parent   # project root
HW_DIR = pathlib.Path(__file__).parent          # Homeworks/
VENV   = HW_DIR / ".venv"
VENV_PY = VENV / "bin" / "python"

# ── Colours ────────────────────────────────────────────────────────────────
GREEN  = "\033[32m"
RED    = "\033[31m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
RESET  = "\033[0m"

def ok(msg):    print(f"  {GREEN}✓{RESET}  {msg}")
def fail(msg):  print(f"  {RED}✗{RESET}  {msg}"); sys.exit(1)
def warn(msg):  print(f"  {YELLOW}!{RESET}  {msg}")
def info(msg):  print(f"  {CYAN}·{RESET}  {msg}")
def header(msg): print(f"\n{CYAN}{'─'*60}{RESET}\n  {msg}\n{CYAN}{'─'*60}{RESET}")


# ── Step 1: venv ───────────────────────────────────────────────────────────

def ensure_venv():
    """Create .venv and install packages if not already present."""
    if not VENV_PY.exists():
        info("Creating Homeworks/.venv …")
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
        ok("venv created")

    # Check which packages are missing
    needed = {"pyyaml": "yaml", "jupyter": "jupyter_core", "nbconvert": "nbconvert"}
    missing = []
    for pkg, import_name in needed.items():
        r = subprocess.run(
            [str(VENV_PY), "-c", f"import {import_name}"],
            capture_output=True,
        )
        if r.returncode != 0:
            missing.append(pkg)

    if missing:
        info(f"Installing: {', '.join(missing)} …")
        subprocess.run(
            [str(VENV_PY), "-m", "pip", "install", "--quiet", *missing],
            check=True,
        )
        ok(f"Installed: {', '.join(missing)}")
    else:
        ok("venv packages up to date")


# ── Step 2: generate ───────────────────────────────────────────────────────

def generate(n: int) -> pathlib.Path:
    gen = HW_DIR / f"gen_h{n}.py"
    if not gen.exists():
        fail(f"Generator not found: {gen}")

    result = subprocess.run(
        [sys.executable, str(gen)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(result.stderr)
        fail(f"gen_h{n}.py exited with code {result.returncode}")

    # Generator prints "Written: /abs/path/to/notebook.ipynb  (N bytes, …)"
    # Extract the path from the first token after "Written:"
    nb_path = None
    for line in result.stdout.strip().splitlines():
        if line.startswith("Written:"):
            raw = line.split("Written:", 1)[1].strip().split()[0]
            nb_path = pathlib.Path(raw)
            break

    if nb_path is None or not nb_path.exists():
        fail(f"gen_h{n}.py ran but output notebook not found.\nStdout: {result.stdout}")

    info(result.stdout.strip().split("\n")[-1])
    ok(f"Generated: {nb_path.relative_to(REPO)}")
    return nb_path


# ── Step 3: validate ───────────────────────────────────────────────────────

def validate(nb: dict, nb_path: pathlib.Path):
    if nb.get("nbformat") != 4:
        fail(f"Unexpected nbformat: {nb.get('nbformat')}")

    cells = nb["cells"]
    if not cells:
        fail("Notebook has no cells")

    empty = [i for i, c in enumerate(cells) if not c.get("source")]
    if empty:
        warn(f"Empty cells at indices: {empty}")
    else:
        ok(f"All {len(cells)} cells have content")

    code_count = sum(1 for c in cells if c["cell_type"] == "code")
    md_count   = sum(1 for c in cells if c["cell_type"] == "markdown")
    ok(f"Cell types: {code_count} code, {md_count} markdown")


# ── Step 4: patch ──────────────────────────────────────────────────────────

def patch(nb: dict) -> int:
    """Strip stray leading backslash-newline from code cells. Returns patch count."""
    patched = 0
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell["source"])
        if src.startswith("\\\n"):
            fixed = src[2:]                          # drop the \<newline>
            cell["source"] = fixed.splitlines(keepends=True)
            patched += 1
    return patched


# ── Step 5: syntax check ───────────────────────────────────────────────────

def syntax_check(nb: dict):
    errors = []
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell["source"])
        try:
            compile(src, f"<cell {i}>", "exec")
        except SyntaxError as e:
            errors.append(f"cell {i}: {e}")

    if errors:
        for e in errors:
            warn(f"Syntax error — {e}")
        fail(f"{len(errors)} cell(s) have syntax errors")
    else:
        ok("All code cells pass syntax check")


# ── Step 6: summary ────────────────────────────────────────────────────────

def print_summary(nb: dict):
    print(f"\n  {'IDX':>3}  {'TYPE':^4}  FIRST LINE")
    print(f"  {'─'*3}  {'─'*4}  {'─'*55}")
    for i, cell in enumerate(nb["cells"]):
        src  = "".join(cell["source"]).strip()
        kind = cell["cell_type"][:4].upper()
        first = src.split("\n")[0][:60]
        print(f"  {i:>3}  {kind:^4}  {first}")


# ── Main ───────────────────────────────────────────────────────────────────

def build_one(n: int):
    header(f"Homework {n}")

    # 1. venv
    ensure_venv()

    # 2. generate
    nb_path = generate(n)

    # 3–6. validate, patch, syntax, summary
    raw = nb_path.read_text(encoding="utf-8")
    nb  = json.loads(raw)

    validate(nb, nb_path)

    patched = patch(nb)
    if patched:
        warn(f"Patched {patched} cell(s) (stray leading backslash-newline)")
    else:
        ok("No patching needed")

    syntax_check(nb)
    print_summary(nb)

    # 7. save
    nb_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    ok(f"Saved: {nb_path.relative_to(REPO)}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    args = sys.argv[1:]

    if args == ["all"]:
        nums = sorted(
            int(p.stem[len("gen_h"):])
            for p in HW_DIR.glob("gen_h*.py")
            if p.stem[len("gen_h"):].isdigit()
        )
        if not nums:
            fail("No gen_hN.py files found in Homeworks/")
    else:
        nums = []
        for a in args:
            if not a.isdigit():
                fail(f"Expected an integer or 'all', got: {a!r}")
            nums.append(int(a))

    for n in nums:
        build_one(n)

    print(f"\n{GREEN}All done.{RESET}\n")


if __name__ == "__main__":
    main()
