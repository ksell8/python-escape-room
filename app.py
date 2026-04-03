"""
app.py — All tkinter UI code for the Python Escape Room.
Imports Room definitions and run_room() from rooms.py.
To debug puzzle logic, edit rooms.py.
To debug UI, edit this file.
"""

import tkinter as tk
from tkinter import font as tkfont
import threading
import time

from rooms import ROOMS, Room, RunResult, run_room


# ── Palette ───────────────────────────────────────────────────────────────────

BG      = "#0a0a0a"
BG2     = "#111111"
BG3     = "#0d0d0d"
BORDER  = "#222222"
GREEN   = "#00ff41"
RED     = "#ff3333"
YELLOW  = "#ffcc00"
ORANGE  = "#ff8800"
DIM     = "#444444"
FG      = "#cccccc"
FG2     = "#888888"
WHITE   = "#ffffff"


# ── Main window ───────────────────────────────────────────────────────────────

class EscapeRoomApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Escape Room")
        self.configure(bg=BG)
        self.geometry("900x740")
        self.resizable(True, True)
        self.minsize(700, 600)

        self.room_index = 0
        self.hint_level = 0
        self.running = False
        self._start_time = None
        self._tick_id = None

        self._build_fonts()
        self._build_ui()
        self._load_room()

    # ── Fonts ──────────────────────────────────────────────────────────────────

    def _build_fonts(self):
        self.font_mono    = tkfont.Font(family="Courier New", size=12)
        self.font_mono_sm = tkfont.Font(family="Courier New", size=11)
        self.font_title   = tkfont.Font(family="Courier New", size=17, weight="bold")
        self.font_label   = tkfont.Font(family="Courier New", size=10)
        self.font_timer   = tkfont.Font(family="Courier New", size=30, weight="bold")
        self.font_btn     = tkfont.Font(family="Courier New", size=11, weight="bold")

    # ── Layout ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Top bar
        top = tk.Frame(self, bg=BG, padx=20, pady=14)
        top.pack(fill="x")

        tk.Label(top, text="PYTHON ESCAPE ROOM", fg=DIM, bg=BG,
                 font=self.font_label).pack(anchor="w")

        self.lbl_title = tk.Label(top, text="", fg=WHITE, bg=BG, font=self.font_title)
        self.lbl_title.pack(anchor="w")

        self.lbl_rooms = tk.Label(top, text="", fg=DIM, bg=BG, font=self.font_label)
        self.lbl_rooms.pack(anchor="w", pady=(2, 0))

        # Flavor text
        flavor_outer = tk.Frame(self, bg=BG2)
        flavor_outer.pack(fill="x", padx=20, pady=(0, 8))
        tk.Frame(flavor_outer, bg=RED, width=3).pack(side="left", fill="y")
        self.lbl_flavor = tk.Label(
            flavor_outer, text="", fg=FG2, bg=BG2,
            font=self.font_label, justify="left",
            wraplength=820, padx=14, pady=10,
        )
        self.lbl_flavor.pack(side="left", fill="x", expand=True)

        # Metric row (time or memory display)
        metric_row = tk.Frame(self, bg=BG, padx=20)
        metric_row.pack(fill="x", pady=(0, 6))

        self.lbl_metric = tk.Label(metric_row, text="--", fg=DIM, bg=BG,
                                    font=self.font_timer)
        self.lbl_metric.pack(side="left")

        self.lbl_threshold = tk.Label(metric_row, text="", fg=DIM, bg=BG,
                                       font=self.font_label)
        self.lbl_threshold.pack(side="left", padx=16)

        self.lbl_status = tk.Label(metric_row, text="", fg=GREEN, bg=BG,
                                    font=self.font_btn)
        self.lbl_status.pack(side="left", padx=8)

        # ── Bottom section (packed before editor so it isn't squeezed out) ───────

        # Hint display
        hint_frame = tk.Frame(self, bg=BG, padx=20, pady=4, height=48)
        hint_frame.pack(side="bottom", fill="x")
        hint_frame.pack_propagate(False)

        self.hint_var = tk.StringVar()
        self.lbl_hint = tk.Label(
            hint_frame, textvariable=self.hint_var,
            fg=YELLOW, bg=BG, font=self.font_label,
            justify="left", anchor="w",
            wraplength=860,
        )
        self.lbl_hint.pack(fill="both", expand=True)

        # Button row
        btn_row = tk.Frame(self, bg=BG, padx=20, pady=10)
        btn_row.pack(side="bottom", fill="x")

        self.btn_run = tk.Button(
            btn_row, text="▶  RUN", fg=BG, bg=WHITE,
            font=self.font_btn, relief="flat",
            padx=18, pady=7, cursor="hand2",
            command=self.run_code,
        )
        self.btn_run.pack(side="left")

        tk.Button(
            btn_row, text="RESET", fg=FG2, bg=BG2,
            font=self.font_btn, relief="flat",
            padx=12, pady=7, cursor="hand2",
            command=self.reset_code,
        ).pack(side="left", padx=(8, 0))

        self.btn_hint = tk.Button(
            btn_row, text="HINT", fg=FG2, bg=BG2,
            font=self.font_btn, relief="flat",
            padx=12, pady=7, cursor="hand2",
            command=self.show_hint,
        )
        self.btn_hint.pack(side="left", padx=(8, 0))

        self.btn_next = tk.Button(
            btn_row, text="NEXT ROOM →", fg=BG, bg=GREEN,
            font=self.font_btn, relief="flat",
            padx=18, pady=7, cursor="hand2",
            command=self.next_room,
        )
        # btn_next hidden until room is passed

        # Output console
        console_outer = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        console_outer.pack(side="bottom", fill="x", padx=20, pady=(2, 8))

        self.console = tk.Text(
            console_outer,
            bg="#050505", fg=GREEN,
            font=self.font_mono_sm,
            relief="flat",
            height=5, padx=10, pady=8,
            wrap="word",
            state="disabled",
        )
        self.console.pack(fill="x")

        tk.Label(self, text="OUTPUT", fg=DIM, bg=BG,
                 font=self.font_label, padx=20).pack(side="bottom", anchor="w")

        # ── Code editor (fills remaining space) ──────────────────────────────────

        editor_outer = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        editor_outer.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        editor_inner = tk.Frame(editor_outer, bg=BG3)
        editor_inner.pack(fill="both", expand=True)

        self.editor = tk.Text(
            editor_inner,
            bg=BG3, fg=FG,
            insertbackground=GREEN,
            font=self.font_mono,
            relief="flat",
            padx=12, pady=10,
            wrap="none",
            selectbackground="#1a3a1a",
            selectforeground=WHITE,
            undo=True,
            tabs=("2c",),
        )
        self.editor.tag_configure("sel", background="#1a3a1a")

        # Convert Tab keypress to 4 spaces so exec() never sees mixed indentation
        def _insert_spaces(event):
            self.editor.insert("insert", "    ")
            return "break"  # prevent default tab insertion
        self.editor.bind("<Tab>", _insert_spaces)

        scroll_y = tk.Scrollbar(editor_inner, command=self.editor.yview,
                                 bg=BG2, troughcolor=BG3)
        scroll_x = tk.Scrollbar(editor_inner, orient="horizontal",
                                 command=self.editor.xview,
                                 bg=BG2, troughcolor=BG3)
        self.editor.configure(
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
        )
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.editor.pack(fill="both", expand=True)

    # ── Room management ────────────────────────────────────────────────────────

    def _load_room(self):
        room: Room = ROOMS[self.room_index]
        self.hint_level = 0
        self.hint_var.set("")
        self.btn_hint.config(text="HINT", fg=FG2, state="normal")
        self.lbl_status.config(text="")
        self.lbl_title.config(text=room.title, fg=WHITE)
        self.lbl_flavor.config(text=room.flavor)
        self.lbl_threshold.config(
            text=f"baseline: {room.broken_label}   goal: {room.fixed_label}",
            fg=DIM,
        )
        self._set_metric("--", DIM)

        pips = " ".join(
            "■" if i < self.room_index else "▶" if i == self.room_index else "□"
            for i in range(len(ROOMS))
        )
        self.lbl_rooms.config(text=pips)

        self.editor.config(state="normal")
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", room.code)
        self._clear_console()
        self.btn_next.pack_forget()
        self.btn_run.config(state="normal", text="▶  RUN", bg=WHITE, fg=BG)

    def reset_code(self):
        room: Room = ROOMS[self.room_index]
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", room.code)
        self._set_metric("--", DIM)
        self.lbl_status.config(text="")
        self.hint_var.set("")
        self.hint_level = 0
        self.btn_hint.config(text="HINT", fg=FG2, state="normal")
        self._clear_console()
        self.btn_next.pack_forget()

    def next_room(self):
        if self.room_index < len(ROOMS) - 1:
            self.room_index += 1
            self._load_room()
        else:
            self._show_escaped()

    def show_hint(self):
        room: Room = ROOMS[self.room_index]
        self.hint_level += 1
        if self.hint_level == 1:
            self.hint_var.set(f"💡 {room.hint1}")
            self.btn_hint.config(text="I GIVE UP", fg=ORANGE)
        elif self.hint_level == 2:
            self.hint_var.set(f"🔓 {room.hint2}")
            self.btn_hint.config(state="disabled", fg=DIM)

    # ── Timer tick (runs on main thread via after, independent of exec thread) ──

    def _start_tick(self):
        self._start_time = time.perf_counter()
        self._tick()

    def _tick(self):
        if not self.running or self._start_time is None:
            return
        elapsed = time.perf_counter() - self._start_time
        self._set_metric(f"{elapsed:.1f}s", DIM)
        self._tick_id = self.after(100, self._tick)

    def _stop_tick(self):
        if self._tick_id is not None:
            self.after_cancel(self._tick_id)
            self._tick_id = None
        self._start_time = None

    # ── Code execution ─────────────────────────────────────────────────────────

    def run_code(self):
        if self.running:
            return
        self.running = True
        self.btn_run.config(state="disabled", text="RUNNING...", bg=DIM, fg=BG)
        self.lbl_status.config(text="")
        self._clear_console()

        room: Room = ROOMS[self.room_index]
        code = self.editor.get("1.0", "end")

        # Start the live timer before spawning the thread
        self._start_tick()

        thread = threading.Thread(
            target=self._exec_thread,
            args=(room, code),
            daemon=True,
        )
        thread.start()

    def _exec_thread(self, room: Room, code: str):
        result: RunResult = run_room(room, code)
        self.after(0, self._on_done, room, result)

    def _on_done(self, room: Room, result: RunResult):
        self._stop_tick()
        self.running = False
        self.btn_run.config(state="normal", text="▶  RUN", bg=WHITE, fg=BG)

        # Format the final metric
        if room.measure == "time":
            metric_text = f"{result.elapsed:.2f}s"
        else:
            metric_text = f"{result.peak_memory_mb:.1f} MB"

        if result.error:
            self._set_metric(metric_text, RED)
            self.lbl_status.config(text="✗ ERROR", fg=RED)
            self._write_console(result.error, color=RED)
            if result.tamper_warning:
                self._show_tamper(result.tamper_warning)
            return

        if result.tamper_warning and not result.passed:
            self._show_tamper(result.tamper_warning)

        if result.output:
            self._write_console(result.output, color=GREEN)

        if result.passed:
            self._set_metric(metric_text, GREEN)
            self.lbl_status.config(text="✓ DOOR UNLOCKED", fg=GREEN)
            label = "ESCAPE →" if self.room_index == len(ROOMS) - 1 else "NEXT ROOM →"
            self.btn_next.config(text=label)
            self.btn_next.pack(side="right")
        else:
            self._set_metric(metric_text, RED)
            reason = result.failure_reason or f"goal: {room.fixed_label}"
            self.lbl_status.config(text=f"✗ {reason}", fg=RED)

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _show_tamper(self, message: str):
        """Flash a big obnoxious warning when locked functions are tampered with."""
        self.hint_var.set(message)
        self.lbl_hint.config(fg="#ff0000")
        # Flash it red/orange three times
        def flash(n=0):
            if n >= 6:
                self.lbl_hint.config(fg=ORANGE)
                return
            color = "#ff0000" if n % 2 == 0 else ORANGE
            self.lbl_hint.config(fg=color)
            self.after(150, flash, n + 1)
        flash()

    def _set_metric(self, text: str, color: str):
        self.lbl_metric.config(text=text, fg=color)

    def _clear_console(self):
        self.console.config(state="normal")
        self.console.delete("1.0", "end")
        self.console.config(state="disabled")

    def _write_console(self, text: str, color: str = GREEN):
        self.console.config(state="normal")
        tag = f"color_{color.replace('#', '')}"
        self.console.tag_configure(tag, foreground=color)
        self.console.insert("end", text.strip(), tag)
        self.console.config(state="disabled")

    # ── Escaped screen ─────────────────────────────────────────────────────────

    def _show_escaped(self):
        for w in self.winfo_children():
            w.destroy()

        frame = tk.Frame(self, bg=BG)
        frame.pack(expand=True)

        tk.Label(frame, text="🚪", font=tkfont.Font(size=52), bg=BG).pack(pady=(0, 10))
        tk.Label(
            frame, text="YOU ESCAPED", fg=GREEN, bg=BG,
            font=tkfont.Font(family="Courier New", size=28, weight="bold"),
        ).pack()
        tk.Label(
            frame,
            text=(
                "You understand:\n"
                "subclassing  •  ABC  •  asyncio  •  yield  •  async generators\n\n"
                "The door was always open.\n"
                "You just needed to know how to open it."
            ),
            fg=FG2, bg=BG,
            font=tkfont.Font(family="Courier New", size=12),
            justify="center",
        ).pack(pady=20)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = EscapeRoomApp()
    app.mainloop()
