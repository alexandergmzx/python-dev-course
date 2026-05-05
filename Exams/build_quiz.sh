#!/usr/bin/env bash
# Usage: ./build_quiz.sh 1        → builds quiz1 from c1.json
#        ./build_quiz.sh 1 2 3    → builds quiz1, quiz2, quiz3
#        ./build_quiz.sh all      → builds quiz1 through quiz12

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"
PYINSTALLER="$VENV/bin/pyinstaller"

# ── Ensure venv + deps ────────────────────────────────────────────────────
if [ ! -f "$PYINSTALLER" ]; then
    echo "[setup] Creating virtual environment..."
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install --quiet customtkinter pyinstaller
    echo "[setup] Done."
fi

# ── Resolve quiz numbers ──────────────────────────────────────────────────
if [ "$1" = "all" ]; then
    NUMS=$(seq 1 12)
else
    NUMS="$@"
fi

if [ -z "$NUMS" ]; then
    echo "Usage: $0 <number> [number ...]   or   $0 all"
    exit 1
fi

# ── Build each quiz ───────────────────────────────────────────────────────
for N in $NUMS; do
    SOURCE="$SCRIPT_DIR/c${N}.json"

    if [ ! -f "$SOURCE" ]; then
        echo "[skip] c${N}.json not found — skipping quiz${N}"
        continue
    fi

    echo ""
    echo "━━━ Building quiz${N} from c${N}.json ━━━"

    # Copy source file to questions.json so --add-data bundles it by that name
    cp "$SOURCE" "$SCRIPT_DIR/questions.json"

    "$PYINSTALLER" \
        --onefile \
        --windowed \
        --name "quiz${N}" \
        --collect-all customtkinter \
        --add-data "questions.json:." \
        "$SCRIPT_DIR/quiz_engine.py" \
        --distpath "$SCRIPT_DIR/dist" \
        --workpath "$SCRIPT_DIR/build" \
        --specpath "$SCRIPT_DIR" \
        --noconfirm \
        --log-level WARN

    rm -f "$SCRIPT_DIR/questions.json"
    echo "[done] dist/quiz${N}  ($(du -sh "$SCRIPT_DIR/dist/quiz${N}" | cut -f1))"
done

echo ""
echo "All done. Executables are in: $SCRIPT_DIR/dist/"
