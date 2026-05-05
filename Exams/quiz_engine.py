import customtkinter as ctk
import json
import sys
import os


def get_resource_path(filename: str) -> str:
    """Resolve path to a bundled file. Works in both dev and PyInstaller modes."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def load_questions() -> dict:
    path = get_resource_path("questions.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Palette ────────────────────────────────────────────────────────────────
BG_DARK      = "#0f0f1a"
CARD_BG      = "#1a1a2e"
CODE_BG      = "#12121f"
CODE_FG      = "#00e5a0"
BTN_NORMAL   = "#1e1e3f"
BTN_HOVER    = "#2d2d5e"
BTN_CORRECT  = "#14532d"
BTN_WRONG    = "#7f1d1d"
ACCENT_BLUE  = "#3b82f6"
GREEN        = "#22c55e"
RED          = "#ef4444"
ORANGE       = "#f97316"


class QuizApp(ctk.CTk):
    def __init__(self, data: dict):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(data.get("quiz_title", "Python Quiz"))
        self.geometry("820x660")
        self.minsize(700, 580)
        self.configure(fg_color=BG_DARK)

        self.questions: list = data["questions"]
        self.current_q: int = 0
        self.score: int = 0

        self._build_ui()
        self._show_question()

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=28, pady=24)

        # ── Header row ──
        header = ctk.CTkFrame(outer, fg_color="transparent")
        header.pack(fill="x", pady=(0, 6))

        self.title_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=ACCENT_BLUE,
        )
        self.title_label.pack(side="left")

        self.progress_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#6b7280",
        )
        self.progress_label.pack(side="right")

        # ── Progress bar ──
        self.progress_bar = ctk.CTkProgressBar(outer, height=4, fg_color="#1f2937", progress_color=ACCENT_BLUE)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=(0, 16))

        # ── Question text ──
        self.question_label = ctk.CTkLabel(
            outer,
            text="",
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=740,
            justify="left",
            anchor="w",
        )
        self.question_label.pack(fill="x", pady=(0, 10))

        # ── Code box (shown only when question has a snippet) ──
        self.code_box = ctk.CTkTextbox(
            outer,
            font=ctk.CTkFont(family="Courier New", size=13),
            height=140,
            state="disabled",
            fg_color=CODE_BG,
            text_color=CODE_FG,
            border_color="#2d2d5e",
            border_width=1,
            corner_radius=8,
        )

        # ── Option buttons ──
        self.options_frame = ctk.CTkFrame(outer, fg_color="transparent")
        self.options_frame.pack(fill="x", pady=(4, 0))

        self.option_buttons: list[ctk.CTkButton] = []
        for i in range(4):
            btn = ctk.CTkButton(
                self.options_frame,
                text="",
                font=ctk.CTkFont(size=14),
                height=48,
                anchor="w",
                corner_radius=8,
                fg_color=BTN_NORMAL,
                hover_color=BTN_HOVER,
                border_width=0,
                command=lambda idx=i: self._check_answer(idx),
            )
            btn.pack(fill="x", pady=4)
            self.option_buttons.append(btn)

        # ── Feedback card ──
        self.feedback_frame = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=10)

        self.feedback_result = ctk.CTkLabel(
            self.feedback_frame,
            text="",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        )
        self.feedback_result.pack(fill="x", padx=16, pady=(14, 4))

        self.feedback_explanation = ctk.CTkLabel(
            self.feedback_frame,
            text="",
            font=ctk.CTkFont(size=13),
            wraplength=700,
            justify="left",
            text_color="#9ca3af",
            anchor="w",
        )
        self.feedback_explanation.pack(fill="x", padx=16, pady=(0, 14))

        # ── Next / Finish button ──
        self.next_button = ctk.CTkButton(
            outer,
            text="Next Question →",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=46,
            corner_radius=8,
            command=self._next_question,
        )

    # ── Question display ───────────────────────────────────────────────────

    def _show_question(self):
        q = self.questions[self.current_q]
        total = len(self.questions)
        idx = self.current_q

        self.title_label.configure(text=f"Quiz — Question {idx + 1}")
        self.progress_label.configure(text=f"{idx + 1} / {total}")
        self.progress_bar.set((idx + 1) / total)

        self.question_label.configure(text=q["question"])

        # Code snippet
        code = q.get("code", "").strip()
        if code:
            self.code_box.pack(fill="x", pady=(0, 12), before=self.options_frame)
            self.code_box.configure(state="normal")
            self.code_box.delete("1.0", "end")
            self.code_box.insert("1.0", code)
            self.code_box.configure(state="disabled")
        else:
            self.code_box.pack_forget()

        # Options
        labels = q.get("labels", ["A", "B", "C", "D"])
        for i, btn in enumerate(self.option_buttons):
            btn.configure(
                text=f"  {labels[i]}.   {q['options'][i]}",
                fg_color=BTN_NORMAL,
                hover_color=BTN_HOVER,
                state="normal",
            )

        self.feedback_frame.pack_forget()
        self.next_button.pack_forget()
        self.options_frame.pack(fill="x", pady=(4, 0))

    # ── Answer logic ───────────────────────────────────────────────────────

    def _check_answer(self, selected: int):
        q = self.questions[self.current_q]
        correct = q["correct"]

        for btn in self.option_buttons:
            btn.configure(state="disabled")

        for i, btn in enumerate(self.option_buttons):
            if i == correct:
                btn.configure(fg_color=BTN_CORRECT, hover_color=BTN_CORRECT)
            elif i == selected:
                btn.configure(fg_color=BTN_WRONG, hover_color=BTN_WRONG)

        if selected == correct:
            self.score += 1
            self.feedback_result.configure(text="✓  Correct!", text_color=GREEN)
        else:
            label = ["A", "B", "C", "D"][correct]
            self.feedback_result.configure(
                text=f"✗  Incorrect — the correct answer was {label}.",
                text_color=RED,
            )

        self.feedback_explanation.configure(text=q.get("explanation", ""))
        self.feedback_frame.pack(fill="x", pady=12)

        is_last = self.current_q + 1 >= len(self.questions)
        self.next_button.configure(text="See Results →" if is_last else "Next Question →")
        self.next_button.pack(fill="x", pady=(0, 4))

    def _next_question(self):
        self.current_q += 1
        if self.current_q < len(self.questions):
            self._show_question()
        else:
            self._show_results()

    # ── Results screen ─────────────────────────────────────────────────────

    def _show_results(self):
        for w in self.winfo_children():
            w.destroy()

        total = len(self.questions)
        pct = round(self.score / total * 100)
        color = GREEN if pct >= 75 else ORANGE if pct >= 50 else RED
        msg = (
            "Outstanding work!" if pct >= 90
            else "Great job!" if pct >= 75
            else "Good effort — review the material and try again." if pct >= 50
            else "Keep studying — you've got this!"
        )

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="Quiz Complete", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=(0, 8))
        ctk.CTkLabel(
            frame,
            text=f"{self.score} / {total}",
            font=ctk.CTkFont(size=64, weight="bold"),
            text_color=color,
        ).pack()
        ctk.CTkLabel(
            frame,
            text=f"{pct}%  •  {msg}",
            font=ctk.CTkFont(size=16),
            text_color="#9ca3af",
        ).pack(pady=12)
        ctk.CTkButton(
            frame,
            text="Restart Quiz",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=46,
            width=220,
            command=self._restart,
        ).pack(pady=(20, 0))

    def _restart(self):
        for w in self.winfo_children():
            w.destroy()
        self.current_q = 0
        self.score = 0
        self._build_ui()
        self._show_question()


# ── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    data = load_questions()
    app = QuizApp(data)
    app.mainloop()
