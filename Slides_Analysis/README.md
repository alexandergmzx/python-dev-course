# Slides Analysis

Tooling to extract slide text and speaker notes from `.pptx` files. Used to generate quiz questions grounded in the actual class content.

## Setup (first time only)

```bash
cd Slides_Analysis
python3 -m venv .venv
.venv/bin/pip install python-pptx
```

## Usage

```bash
# Print everything (slide text + speaker notes) to stdout
.venv/bin/python extract_notes.py ../class1/slides1.pptx

# Speaker notes only
.venv/bin/python extract_notes.py ../class1/slides1.pptx --notes-only

# Write to a file
.venv/bin/python extract_notes.py ../class1/slides1.pptx -o class1_notes.txt
```

## Workflow for a new class

1. Drop `slidesN.pptx` into `classN/`
2. Run `extract_notes.py ../classN/slidesN.pptx -o classN_notes.txt`
3. Read the notes and design quiz questions for `Exams/cN.json`
4. Build with `Exams/build_quiz.sh N`
