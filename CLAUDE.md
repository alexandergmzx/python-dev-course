# CLAUDE.md — Python for DevOps Course

This file gives Claude Code the context to help build slides, quizzes, and executables for a 12-class course.

---

## Project Overview

A 12-class course teaching **Python for DevOps / SRE engineers**. Students are expected to have a working knowledge of **C and Linux systems** — slides leverage that background by framing every Python concept against its C equivalent.

Each class produces three artifacts in `classN/`:
- `slidesN.pptx` — instructor-built lecture deck (with **runnable code in speaker notes** — this is the canonical source for quiz design)
- `quizN` / `quizN.exe` — compiled CustomTkinter app, 20 questions
- `homeworkN.ipynb` — Jupyter notebook (added when ready)

---

## Source Material

**Book**: *Python for DevOps: Learn Ruthlessly Effective Automation* (Gift, Behrman, Deza, Gheorghiu — O'Reilly, 2020, ISBN 978-1-492-05769-7).

The full PDF lives at the repo root: `python-for-devops-learn-ruthlessly-effective-automation-original-retailnbsped-149205769x-978-1492057697.pdf` (768 pages, 11 MB).

**Reading it**: use the Read tool with `pages: "X-Y"` (max 20 pages per call). Don't try to read it all at once — the harness will refuse.

---

## Course Roadmap

The book has **16 chapters in 5 sections**. They map to **12 classes** as follows. Note that **Class 6 (Pytest) is intentionally placed before Class 7 (CI/CD)** — the book's order is reference-friendly, but pedagogically you can't pipeline what you haven't tested.

| # | Class Title | Book Chapters | Theme |
|---|---|---|---|
| 1 | Python Foundations ✓ DONE | Ch 1 + parts of 2, 3 | PyObject, refcount, types, lists, dicts, exceptions, files, sys |
| 2 | Filesystem & Text Automation | Ch 2 (deep) | regex, hashing, encryption, `os.walk`, `pathlib` |
| 3 | Building CLI Tools | Ch 3 (deep) | `argparse`, `click`, `fire`, plug-ins, `subprocess` |
| 4 | Linux Power Tools with Python | Ch 4 | disk/network/CPU utilities, mixing Python with bash/zsh, `strace` |
| 5 | Packaging & Distribution | Ch 5 | versioning, native packaging, Debian/RPM, systemd units |
| 6 | Testing for DevOps | Ch 8 | `pytest`, fixtures, parametrization, `testinfra` |
| 7 | CI/CD Pipelines | Ch 6 | real-world case studies (Hugo, GCP App Engine, NFSOPS) |
| 8 | Observability — Monitoring & Logging | Ch 7 | Graphite, StatsD, Prometheus, ELK |
| 9 | Cloud & Infrastructure as Code | Ch 9 + Ch 10 | IaaS/PaaS/Serverless, Terraform, Pulumi |
| 10 | Containers — Docker & Kubernetes | Ch 11 + Ch 12 | docker-compose, kompose, minikube, GKE, Helm |
| 11 | Serverless & Data Engineering | Ch 13 + Ch 15 | AWS Lambda, OpenFaaS, YAML, big data sources |
| 12 | MLOps + Capstone (War Stories) | Ch 14 + Ch 16 | Sklearn + Flask + K8s, antipatterns, interviews |

---

## Directory Layout

See `README.md` for the full reference. In short: `class1/`–`class12/` are student-facing, `Exams/` is the instructor's quiz workspace, `Slides_Analysis/` holds the `.pptx` notes extractor, and `Homeworks/` holds the homework generator scripts and build tooling.

---

## Workflow for Building a New Class

When the user starts on Class N (with `slidesN.pptx` already drafted):

1. **Extract speaker notes** — they contain the runnable code examples that ground the quiz:
   ```bash
   cd Slides_Analysis
   .venv/bin/python extract_notes.py ../classN/slidesN.pptx --notes-only
   ```

2. **Read the relevant book chapter** for additional depth and consistent terminology. Use the Read tool: `pages: "100-115"` etc. Find the chapter's page range from the table of contents (PDF pages 1–28).

3. **Write `Exams/cN.json`** — see the schema below. Build questions from the actual code in the notes, not from invented examples.

4. **Verify in dev mode** before compiling:
   ```bash
   cd Exams
   cp cN.json questions.json
   .venv/bin/python quiz_engine.py
   rm questions.json
   ```

5. **Build the executable**:
   ```bash
   ./build_quiz.sh N      # Linux
   build_quiz.bat N       # Windows
   ```
   For Windows `.exe` files without a Windows machine, push to GitHub — `.github/workflows/build-quizzes.yml` runs the build on a Windows runner and uploads the `.exe` as a `windows-quizzes` artifact.

---

## Slide & Pedagogy Conventions

Class 1 set the pattern. Every concept slide should have:

1. **A short definition** of the Python concept
2. **A C-programmer analogy** — these students think in C. Examples: "a Python variable is a `PyObject*`", "list is a dynamic array of `PyObject*` pointers, not a linked list", "Python's `import` is `#include` + linker resolution combined"
3. **An SRE/DevOps framing** — never use toy examples. Use log files, config files, deploy scripts, daemon processes
4. **A docs.python.org link** in the slide text
5. **Runnable code in the speaker notes** — this is non-negotiable. Notes without code mean no quiz material

Closing convention: every deck ends with a slide of "Professional Technical Interview Questions" mixing the concepts taught with general SRE/DevOps questions.

---

## Quiz JSON Schema

`Exams/cN.json`:

```json
{
  "quiz_title": "Python for DevOps — Class N",
  "questions": [
    {
      "question": "What does this print?",
      "code": "x = 10\nprint(x)",
      "options": ["9", "10", "11", "Error"],
      "correct": 1,
      "explanation": "x was assigned 10, so print(x) outputs 10.",
      "labels": ["a", "b", "c", "d"]
    }
  ]
}
```

| Field | Required | Notes |
|---|---|---|
| `quiz_title` | yes | Window title bar |
| `question` | yes | Plain-text question |
| `code` | no | Optional — shown in green-on-dark monospace box |
| `options` | yes | Exactly 4 strings |
| `correct` | yes | Zero-based index of the right option |
| `explanation` | no | Shown after the student answers |
| `labels` | no | 4-char list overriding the default A/B/C/D button labels. Falls back to `["A","B","C","D"]` if absent. |

---

## Quiz Design Guidelines

- **20 questions per class** (Class 1 precedent)
- **Mix code-tracing with conceptual** questions (~70% trace, ~30% conceptual)
- **Distractors should be common bugs** — the wrong answer is what a student *would* think: mutability traps (`list.sort()` returns `None`), aliasing (`b = a` doesn't copy), `+=` on strings, file mode `"w"` truncating, etc.
- **Every question grounded in the speaker notes** — if the notes don't contain the code that would make the answer obvious, the question is unfair
- **Run every code snippet through Python before committing the JSON** — the answer key must be empirically verified, not assumed

### Easter Egg (Class 1 only — don't extend without asking)

Class 1's `labels` field is engineered so that reading the **correct** answer's label across all 20 questions in order spells `gral.ignaciozaragoza` (a reference the user supplied). Do not invent new Easter eggs for other classes; ask the user first.

---

## Homework Notebook Design

### Directory structure

```
Homeworks/
  gen_hN.py          ← source of truth for homework N content (edit this to change exercises)
  build_homework.py  ← unified build script: venv + generate + validate + patch + syntax check
  .venv/             ← pyyaml + jupyter + nbconvert (auto-created on first run)
```

The generated notebook is written to `classN/homeworkN.ipynb` (student-facing location). The generator script defines `OUT_PATH` at the top — it can point to any class directory (e.g. `gen_h1.py` writes to `class2/` because homework 1 covers classes 1 & 2 and is assigned after class 2).

### Homework numbering convention

Homework N = the Nth homework assignment, not necessarily tied to class N. `homework1` covers classes 1 & 2 and lives in `class2/`. Future homeworks follow the same pattern — number reflects assignment order, directory reflects when it's handed out.

### Notebook structure (per homework)

Each `homeworkN.ipynb` follows this layout:

```
[Markdown] Title + objective (one sentence per section listed)
[Markdown] ## Setup — pip install cell (pyyaml is the only non-stdlib dep so far)
[Code]     import cell — student runs once
[Markdown] ## Part 1 — <Class 1 topic reinforcement>
[Code]     Exercise — skeleton / broken code + assert block
... (repeat for each exercise) ...
[Markdown] ## Part N — Mini Capstone
[Code]     One pipeline exercise combining both classes
[Markdown] Stretch goals
```

### Exercise types

| Type | When to use |
|---|---|
| Fix the bug | Subtle traps: aliasing, `sort()` returns `None`, `str +=`, `re.search` returns `None` |
| Fill in the blank | When the API shape is the lesson (`re.search(r"___", line)`) |
| Write from scratch | When the scenario is the lesson |

**Rule**: every exercise uses a DevOps/SRE scenario — log files, config files, deploy scripts, metrics. No toy examples.

### Writing a new generator (`gen_hN.py`)

1. Copy `gen_h1.py` as a template
2. Update `OUT_PATH` to point to the correct `classN/` directory
3. Replace the `cells` content with the new exercises
4. Run `python3 Homeworks/build_homework.py N` — it regenerates, validates, patches, and syntax-checks in one step

### What `build_homework.py` does

1. **venv** — creates `Homeworks/.venv` with `pyyaml`, `jupyter`, `nbconvert` if missing
2. **generate** — runs `gen_hN.py`; discovers the output path from the generator's own stdout
3. **validate** — checks `nbformat == 4`, all cells non-empty, prints code/markdown counts
4. **patch** — strips stray leading `\<newline>` from code cells (artifact of raw-string generators)
5. **syntax check** — `compile()`s every code cell; exits non-zero on any `SyntaxError`
6. **summary** — prints a numbered cell index with type and first line
7. **save** — writes the patched notebook back to disk

---

## Build Commands — Cheat Sheet

```bash
# Extract speaker notes from any .pptx
Slides_Analysis/.venv/bin/python Slides_Analysis/extract_notes.py classN/slidesN.pptx --notes-only

# Test a quiz live without compiling
cd Exams && cp cN.json questions.json && .venv/bin/python quiz_engine.py && rm questions.json

# Build one quiz / several / all
Exams/build_quiz.sh N
Exams/build_quiz.sh 1 2 3
Exams/build_quiz.sh all

# Build homework notebook(s)
python3 Homeworks/build_homework.py N
python3 Homeworks/build_homework.py 1 2 3
python3 Homeworks/build_homework.py all   # finds every gen_hN.py automatically

# All venvs auto-create on first run if missing
```

---

## Lessons Learned — Don't Repeat

1. **PyInstaller `--add-data "src:dest"`**: `dest` is a **directory**, not a rename. Using `--add-data "c1.json:questions.json"` creates a folder called `questions.json/` containing `c1.json`. The fix used in `build_quiz.sh` is to copy `cN.json` → `questions.json` first, then `--add-data "questions.json:."`.

2. **`--collect-all customtkinter` is required** for the executable to bundle the theme JSON files. Without it, the GUI fails to start.

3. **PyInstaller cannot cross-compile.** Linux can only produce a Linux ELF; Windows can only produce `.exe`. For Windows builds without a Windows machine, push to GitHub — the `build-quizzes.yml` workflow runs on `windows-latest` and uploads the artifacts.

4. **Single root `.gitignore` covers all venvs.** The pattern `.venv/` (no leading slash) matches any directory named `.venv` anywhere in the tree, so `Exams/.venv/`, `Slides_Analysis/.venv/`, and `Homeworks/.venv/` are all excluded with one line.

5. **Three venvs by design — keep them isolated.**
   - `Exams/.venv` — `customtkinter` + `pyinstaller` (~99 MB). Quiz build only.
   - `Slides_Analysis/.venv` — `python-pptx` only. Notes extraction only.
   - `Homeworks/.venv` — `pyyaml` + `jupyter` + `nbconvert`. Homework generation and execution only.
   Don't cross-install packages between venvs.

6. **Always run quiz code through Python before committing.** During Class 1 review we caught one ambiguous question (Q10 — two correct answers) only by re-reading every snippet. The answer key isn't trustworthy unless every snippet has been executed.
