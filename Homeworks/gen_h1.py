#!/usr/bin/env python3
"""
Generate class2/homework1.ipynb — the first homework for the Python for DevOps course.

Covers:
  - Part 1: Python Foundations (Class 1)
  - Part 2: Filesystem & Text Automation (Class 2)
  - Part 3: Mini Capstone (combines both)

Run from the repo root:
    python3 Homeworks/gen_h1.py

Output: class2/homework1.ipynb
"""
import json, uuid, textwrap, pathlib

REPO_ROOT = pathlib.Path(__file__).parent.parent
OUT_PATH  = REPO_ROOT / "class2" / "homework1.ipynb"


def _mid():
    return str(uuid.uuid4())[:8]

def md(text):
    lines = textwrap.dedent(text).strip().splitlines(keepends=True)
    return {"cell_type": "markdown", "id": _mid(), "metadata": {}, "source": lines}

def code(text):
    src = textwrap.dedent(text).strip()
    # Raw-string cells may start with a literal backslash-newline — strip it.
    if src.startswith("\\\n"):
        src = src[2:]
    lines = src.splitlines(keepends=True)
    return {
        "cell_type": "code", "id": _mid(),
        "execution_count": None, "metadata": {}, "outputs": [],
        "source": lines,
    }


cells = []

# ── Title ──────────────────────────────────────────────────────────────────
cells.append(md("""\
    # Homework 1 — Python for DevOps: Classes 1 & 2

    **Assigned after Class 2.** This notebook reinforces the concepts from:
    - **Class 1** — Python Foundations (types, mutability, comprehensions, exceptions, file modes)
    - **Class 2** — Filesystem & Text Automation (pathlib, csv, regex, hashlib, yaml, os.environ)

    **Rules**
    - Run cells top-to-bottom; each `assert` block at the bottom of an exercise verifies your answer.
    - Every exercise uses a real DevOps/SRE scenario — no toy problems.
    - The last exercise combines both classes into a small pipeline.

    > **Tip**: if an assert fires with a cryptic message, add `print(your_variable)` before it.
    """))

# ── Setup ──────────────────────────────────────────────────────────────────
cells.append(md("## Setup"))
cells.append(code("""\
    # Run once. pyyaml is the only non-stdlib dependency.
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "pyyaml"])
    """))
cells.append(code("""\
    import csv, hashlib, io, json, os, pathlib, re, sys, tempfile, yaml
    print("Imports OK")
    """))

# ══════════════════════════════════════════════════════════════════════════
# PART 1 — Python Foundations
# ══════════════════════════════════════════════════════════════════════════
cells.append(md("""\
    ---
    ## Part 1 — Python Foundations

    Exercises that target the silent bugs most commonly introduced by engineers
    coming from C or statically-typed languages.
    """))

# 1.1 list.sort() returns None ─────────────────────────────────────────────
cells.append(md("""\
    ### Exercise 1.1 — `list.sort()` returns `None`

    The deployment script below silently prints `None` instead of a sorted list.
    **Fix it** so `deploy_order` holds the correctly sorted list.
    (Hint: there are two valid fixes — pick one.)
    """))
cells.append(code("""\
    servers = ["web03", "web01", "db01", "web02", "cache01"]

    # BROKEN — result is None
    deploy_order = servers.sort()

    # --- fix deploy_order above, then run the assertion ---

    assert deploy_order is not None, "deploy_order is still None — sort() returns None in-place"
    assert deploy_order == ["cache01", "db01", "web01", "web02", "web03"], f"Got: {deploy_order}"
    print("✓ 1.1 passed")
    """))

# 1.2 list aliasing ────────────────────────────────────────────────────────
cells.append(md("""\
    ### Exercise 1.2 — List aliasing (`b = a` is not a copy)

    The config merger below mutates `base_config` — any later service that reads
    base_config will see the prod values. **Fix the assignment on the marked line**
    so `base_config` is unchanged after the merge.
    """))
cells.append(code("""\
    base_config = {"timeout": 30, "retries": 3, "log_level": "INFO"}

    prod_config = base_config        # BUG: this is an alias, not a copy
    prod_config["log_level"] = "WARNING"
    prod_config["timeout"] = 60

    assert base_config == {"timeout": 30, "retries": 3, "log_level": "INFO"}, \\
        f"base_config was mutated: {base_config}"
    assert prod_config == {"timeout": 60, "retries": 3, "log_level": "WARNING"}, \\
        f"prod_config wrong: {prod_config}"
    print("✓ 1.2 passed")
    """))

# 1.3 string += in loop ────────────────────────────────────────────────────
cells.append(md("""\
    ### Exercise 1.3 — `str +=` in a loop is O(N²)

    The log formatter below copies the entire string on every iteration.
    **Rewrite it** using `str.join()` so it produces identical output in O(N).
    """))
cells.append(code("""\
    log_entries = [
        "[INFO]  Server started",
        "[WARN]  High memory usage: 87%",
        "[ERROR] Disk full on /var",
        "[INFO]  Backup completed",
    ]

    # BROKEN — O(N²): creates a new string object on every +=
    report = ""
    for entry in log_entries:
        report += entry + "\\n"

    # Rewrite: produce the same string in one line using join()
    # report_fast = YOUR CODE HERE

    assert report_fast == report, "Output differs from the original"
    assert report_fast.count("\\n") == 4
    print("✓ 1.3 passed")
    """))

# 1.4 list comprehension ───────────────────────────────────────────────────
cells.append(md("""\
    ### Exercise 1.4 — List comprehension: filter + transform

    Write a **one-line list comprehension** that returns only the CPU readings
    above `threshold`, rounded to the nearest integer.
    """))
cells.append(code("""\
    cpu_readings = [12.5, 87.3, 45.0, 91.2, 3.8, 78.6, 55.5, 95.1]
    threshold = 75.0

    high_cpu = None  # YOUR CODE HERE — one-line comprehension

    assert high_cpu == [87, 91, 79, 95], f"Got: {high_cpu}"
    print("✓ 1.4 passed")
    """))

# 1.5 dict dispatch table ──────────────────────────────────────────────────
cells.append(md("""\
    ### Exercise 1.5 — Dict dispatch table

    Replace the `if/elif` chain in `run_command` with a **dict dispatch table**
    so adding a new command only requires one dict entry, not a new branch.
    """))
cells.append(code("""\
    def start(service):   return f"Starting {service}"
    def stop(service):    return f"Stopping {service}"
    def restart(service): return f"Restarting {service}"

    def run_command(cmd, service):
        # BROKEN — replace this if/elif chain with a dispatch table
        if cmd == "start":
            return start(service)
        elif cmd == "stop":
            return stop(service)
        elif cmd == "restart":
            return restart(service)
        else:
            raise ValueError(f"Unknown command: {cmd}")

    assert run_command("restart", "nginx") == "Restarting nginx"
    assert run_command("stop", "redis")    == "Stopping redis"
    assert run_command("start", "db")      == "Starting db"
    try:
        run_command("explode", "db")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    print("✓ 1.5 passed")
    """))

# 1.6 try/except/else/finally ──────────────────────────────────────────────
cells.append(md("""\
    ### Exercise 1.6 — `try / except / else / finally`

    Implement `safe_read_config(path)`:
    - Returns the parsed JSON dict if the file exists and is valid JSON
    - Returns `{}` if the file is missing (`FileNotFoundError`) or malformed (`json.JSONDecodeError`)
    - **Always** prints `"Config read attempted: <path>"` — whether it succeeded or failed

    Use `try / except / else / finally` (all four clauses).
    """))
cells.append(code("""\
    def safe_read_config(path):
        # YOUR CODE HERE
        pass

    # Test 1: missing file
    result = safe_read_config("/nonexistent/config.json")
    assert result == {}, f"Expected {{}}, got {result}"

    # Test 2: valid JSON
    tmp = pathlib.Path(tempfile.mktemp(suffix=".json"))
    tmp.write_text('{"env": "prod", "replicas": 3}')
    result = safe_read_config(str(tmp))
    assert result == {"env": "prod", "replicas": 3}, f"Got: {result}"
    tmp.unlink()

    # Test 3: malformed JSON
    tmp2 = pathlib.Path(tempfile.mktemp(suffix=".json"))
    tmp2.write_text("{not valid json")
    result = safe_read_config(str(tmp2))
    assert result == {}, f"Expected {{}}, got {result}"
    tmp2.unlink()

    print("✓ 1.6 passed")
    """))

# ══════════════════════════════════════════════════════════════════════════
# PART 2 — Filesystem & Text Automation
# ══════════════════════════════════════════════════════════════════════════
cells.append(md("""\
    ---
    ## Part 2 — Filesystem & Text Automation

    These exercises target the silent data-loss and crash bugs that show up when
    automating config files, log parsers, and deployment scripts.
    """))

# 2.1 pathlib.write_text overwrites ────────────────────────────────────────
cells.append(md("""\
    ### Exercise 2.1 — `pathlib.write_text()` silently overwrites

    The version bumper below replaces the entire config file with just the new
    version field — `app`, `replicas`, and every other key disappear silently.

    **Fix `bump_version`** so it updates only `version` and leaves all other keys intact.
    """))
cells.append(code("""\
    def bump_version(config_path, new_version):
        # BROKEN: builds a new dict with only "version" and overwrites the file
        config_path.write_text(json.dumps({"version": new_version}))

    # Setup: write a multi-key config
    cfg_path = pathlib.Path(tempfile.mktemp(suffix=".json"))
    cfg_path.write_text(json.dumps({"app": "deploy-bot", "version": "1.0.0", "replicas": 2}))

    bump_version(cfg_path, "1.0.1")

    result = json.loads(cfg_path.read_text())
    cfg_path.unlink()

    assert "app" in result,      f"'app' key was lost: {result}"
    assert "replicas" in result, f"'replicas' key was lost: {result}"
    assert result["version"] == "1.0.1", f"version not updated: {result}"
    print("✓ 2.1 passed")
    """))

# 2.2 csv yields strings ───────────────────────────────────────────────────
cells.append(md("""\
    ### Exercise 2.2 — `csv.reader` yields strings, not numbers

    The metrics aggregator below crashes with `TypeError` because it tries to add
    a string to an integer. **Fix `total_memory`** so it returns the correct integer sum.
    """))
cells.append(code("""\
    CSV_DATA = "server,cpu_pct,mem_mb\\nweb01,45,2048\\nweb02,82,4096\\ndb01,23,8192\\n"

    def total_memory(csv_text):
        reader = csv.reader(io.StringIO(csv_text))
        next(reader)  # skip header
        total = 0
        for row in reader:
            total = total + row[2]  # BUG: row[2] is str
        return total

    assert total_memory(CSV_DATA) == 14336, f"Got: {total_memory(CSV_DATA)}"
    print("✓ 2.2 passed")
    """))

# 2.3 re.search returns None ───────────────────────────────────────────────
cells.append(md("""\
    ### Exercise 2.3 — `re.search()` returns `None` on no match

    The log parser below crashes with `AttributeError: 'NoneType' object has no
    attribute 'group'` on lines that contain no IP address.

    **Fix `extract_ips`** so it silently skips non-matching lines.
    """))
cells.append(code(r"""
    LOG_LINES = [
        "192.168.1.10 - GET /api/health 200",
        "CRON job started at 03:00",
        "10.0.0.5 - POST /deploy 201",
        "Backup completed successfully",
    ]

    def extract_ips(lines):
        ips = []
        for line in lines:
            m = re.search(r"\d+\.\d+\.\d+\.\d+", line)
            ips.append(m.group())  # BUG: crashes when m is None
        return ips

    assert extract_ips(LOG_LINES) == ["192.168.1.10", "10.0.0.5"]
    print("✓ 2.3 passed")
    """))

# 2.4 hashlib requires bytes ───────────────────────────────────────────────
cells.append(md("""\
    ### Exercise 2.4 — `hashlib` requires `bytes`, not `str`

    The file integrity checker below passes the file's text content (a `str`)
    to `h.update()`, which raises `TypeError`. **Fix `file_checksum`** so it
    reads the file in binary mode and returns the correct SHA-256 hex digest.
    """))
cells.append(code("""\
    def file_checksum(filepath):
        h = hashlib.sha256()
        with open(filepath, "r") as f:   # BUG: text mode
            content = f.read()
        h.update(content)                # BUG: str instead of bytes
        return h.hexdigest()

    tmp = pathlib.Path(tempfile.mktemp())
    tmp.write_bytes(b"deploy v1.2.3\\n")
    digest = file_checksum(str(tmp))
    tmp.unlink()

    assert len(digest) == 64, f"Expected 64-char hex, got {len(digest)}"
    assert all(c in "0123456789abcdef" for c in digest), f"Not hex: {digest}"
    print("✓ 2.4 passed")
    """))

# 2.5 yaml.load unsafe ─────────────────────────────────────────────────────
cells.append(md("""\
    ### Exercise 2.5 — `yaml.load()` can execute arbitrary code

    The deployment loader uses `yaml.Loader`, which can deserialize custom Python
    objects — a path to remote code execution if the YAML comes from an untrusted
    source (CI artifact, user-supplied config file).

    **Fix `load_deployment`**: replace the unsafe loader with `yaml.safe_load()`.
    Add a one-line comment above the fixed call explaining the security risk.
    """))
cells.append(code("""\
    DEPLOY_YAML = \"\"\"
    service: api-gateway
    replicas: 3
    image: myapp:latest
    \"\"\"

    def load_deployment(yaml_text):
        # BROKEN: yaml.Loader can construct arbitrary Python objects (RCE risk)
        return yaml.load(yaml_text, Loader=yaml.Loader)

    config = load_deployment(DEPLOY_YAML)
    assert config["replicas"] == 3
    assert config["service"] == "api-gateway"
    print("✓ 2.5 passed")
    """))

# 2.6 os.environ.get with defaults ─────────────────────────────────────────
cells.append(md("""\
    ### Exercise 2.6 — `os.environ.get()` with defaults

    Write `load_db_config()` that reads three environment variables with sensible
    defaults for local development:

    | Variable | Default |
    |---|---|
    | `DB_HOST` | `"localhost"` |
    | `DB_PORT` | `5432` (int) |
    | `DB_NAME` | `"appdb"` |

    Return a dict `{"host": ..., "port": ..., "name": ...}`.
    `port` must be an `int` even when read from the environment (env vars are always strings).
    """))
cells.append(code("""\
    def load_db_config():
        # YOUR CODE HERE
        pass

    # Test 1: no env vars — should use all defaults
    for k in ("DB_HOST", "DB_PORT", "DB_NAME"):
        os.environ.pop(k, None)

    cfg = load_db_config()
    assert cfg == {"host": "localhost", "port": 5432, "name": "appdb"}, f"Got: {cfg}"

    # Test 2: env vars set
    os.environ["DB_HOST"] = "db.prod.internal"
    os.environ["DB_PORT"] = "5433"
    os.environ["DB_NAME"] = "production"
    cfg = load_db_config()
    assert cfg == {"host": "db.prod.internal", "port": 5433, "name": "production"}, f"Got: {cfg}"
    assert isinstance(cfg["port"], int), "port must be int"

    # Cleanup
    for k in ("DB_HOST", "DB_PORT", "DB_NAME"):
        os.environ.pop(k, None)

    print("✓ 2.6 passed")
    """))

# 2.7 named regex groups ───────────────────────────────────────────────────
cells.append(md("""\
    ### Exercise 2.7 — Named regex groups (`?P<name>`)

    Write `parse_apache_log(line)` using **named capture groups** to extract
    the six fields from a simplified Apache combined log line:

    ```
    192.168.1.1 - jdoe [13/Nov/2019:14:43:30] "GET /api/status HTTP/1.1" 200 512
    ```

    Return a dict with keys: `ip`, `user`, `method`, `path`, `status`, `bytes_sent`.
    (`user` is `"-"` when the request is unauthenticated.)
    """))
cells.append(code(r"""
    APACHE_LINES = [
        '192.168.1.1 - jdoe [13/Nov/2019:14:43:30] "GET /api/status HTTP/1.1" 200 512',
        '10.0.0.2 - - [13/Nov/2019:14:44:01] "POST /deploy HTTP/1.1" 201 0',
    ]

    def parse_apache_log(line):
        # YOUR CODE HERE — use re.search() with named groups (?P<name>...)
        pass

    r1 = parse_apache_log(APACHE_LINES[0])
    assert r1["ip"]         == "192.168.1.1"
    assert r1["user"]       == "jdoe"
    assert r1["method"]     == "GET"
    assert r1["path"]       == "/api/status"
    assert r1["status"]     == "200"
    assert r1["bytes_sent"] == "512"

    r2 = parse_apache_log(APACHE_LINES[1])
    assert r2["user"]   == "-"
    assert r2["method"] == "POST"

    print("✓ 2.7 passed")
    """))

# ══════════════════════════════════════════════════════════════════════════
# PART 3 — Mini Capstone
# ══════════════════════════════════════════════════════════════════════════
cells.append(md("""\
    ---
    ## Part 3 — Mini Capstone

    One exercise that strings together concepts from both classes into a small
    end-to-end automation pipeline.
    """))

cells.append(md("""\
    ### Exercise 3.1 — Server overload report

    Write `find_overloaded_servers(csv_text, cpu_threshold, output_path)` that:

    1. Reads a CSV with columns `server, cpu_pct, mem_mb, disk_gb`
    2. Skips the header row
    3. Converts `cpu_pct` to `float`, `mem_mb` and `disk_gb` to `int`
    4. Filters rows where `cpu_pct > cpu_threshold`
    5. Writes a JSON report to `output_path` in this shape:

    ```json
    {
        "threshold": 80.0,
        "overloaded": [
            {"server": "web02", "cpu_pct": 87.5, "mem_mb": 4096, "disk_gb": 120}
        ]
    }
    ```

    Combine: `csv`, list comprehension, type conversion, `json.dump`, `pathlib`.
    """))
cells.append(code("""\
    METRICS_CSV = \"\"\"server,cpu_pct,mem_mb,disk_gb
    web01,45.2,2048,50
    web02,87.5,4096,120
    db01,23.1,8192,500
    cache01,91.3,1024,20
    worker01,78.9,2048,80
    \"\"\"

    def find_overloaded_servers(csv_text, cpu_threshold, output_path):
        # YOUR CODE HERE
        pass

    out = pathlib.Path(tempfile.mktemp(suffix=".json"))
    find_overloaded_servers(METRICS_CSV, cpu_threshold=80.0, output_path=out)

    report = json.loads(out.read_text())
    out.unlink()

    assert report["threshold"] == 80.0, f"threshold wrong: {report['threshold']}"
    names = sorted(s["server"] for s in report["overloaded"])
    assert names == ["cache01", "web02"], f"Got: {names}"
    assert all(isinstance(s["cpu_pct"], float) for s in report["overloaded"]), "cpu_pct must be float"
    assert all(isinstance(s["mem_mb"], int)   for s in report["overloaded"]), "mem_mb must be int"
    print("✓ 3.1 passed — pipeline complete!")
    """))

# ── Done ───────────────────────────────────────────────────────────────────
cells.append(md("""\
    ---
    ## All done!

    If every cell printed `✓ ... passed`, you have completed Homework 1.

    **Stretch goals** (not graded):
    - Extend Exercise 2.4: make `file_checksum` stream the file in 4 KB chunks
      so it works on multi-GB log archives without loading them into RAM.
    - Extend Exercise 3.1: sort the `overloaded` list by `cpu_pct` descending
      and add a `"generated_at"` timestamp using `datetime.datetime.utcnow().isoformat()`.
    """))

# ── Write notebook ─────────────────────────────────────────────────────────
notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.10.0",
        },
    },
    "cells": cells,
}

OUT_PATH.write_text(json.dumps(notebook, indent=1, ensure_ascii=False))
print(f"Written: {OUT_PATH}  ({OUT_PATH.stat().st_size:,} bytes,  {len(cells)} cells)")
