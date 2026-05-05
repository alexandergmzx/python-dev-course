@echo off
REM Usage: build_quiz.bat 1          → builds quiz1.exe from c1.json
REM        build_quiz.bat 1 2 3      → builds quiz1.exe, quiz2.exe, quiz3.exe
REM        build_quiz.bat all        → builds quiz1.exe through quiz12.exe

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "VENV=%SCRIPT_DIR%.venv"
set "PYINSTALLER=%VENV%\Scripts\pyinstaller.exe"

REM ── Ensure venv + deps ────────────────────────────────────────────────
if not exist "%PYINSTALLER%" (
    echo [setup] Creating virtual environment...
    python -m venv "%VENV%"
    "%VENV%\Scripts\pip.exe" install --quiet customtkinter pyinstaller
    echo [setup] Done.
)

REM ── Resolve quiz numbers ──────────────────────────────────────────────
set "NUMS=%*"
if "%~1"=="all" set "NUMS=1 2 3 4 5 6 7 8 9 10 11 12"

if "%NUMS%"=="" (
    echo Usage: %~nx0 ^<number^> [number ...]   or   %~nx0 all
    exit /b 1
)

REM ── Build each quiz ───────────────────────────────────────────────────
for %%N in (%NUMS%) do (
    set "SOURCE=%SCRIPT_DIR%c%%N.json"

    if not exist "!SOURCE!" (
        echo [skip] c%%N.json not found — skipping quiz%%N
    ) else (
        echo.
        echo === Building quiz%%N from c%%N.json ===

        copy /Y "!SOURCE!" "%SCRIPT_DIR%questions.json" >nul

        "%PYINSTALLER%" ^
            --onefile ^
            --windowed ^
            --name "quiz%%N" ^
            --collect-all customtkinter ^
            --add-data "questions.json;." ^
            "%SCRIPT_DIR%quiz_engine.py" ^
            --distpath "%SCRIPT_DIR%dist" ^
            --workpath "%SCRIPT_DIR%build" ^
            --specpath "%SCRIPT_DIR%" ^
            --noconfirm ^
            --log-level WARN

        del "%SCRIPT_DIR%questions.json"
        echo [done] dist\quiz%%N.exe
    )
)

echo.
echo All done. Executables are in: %SCRIPT_DIR%dist\
endlocal
