"""Tkinter front end for the existing backtracking + MRV Sudoku solver.

Run with `python gui.py` from the sudoku folder.  GUI rendering and input
handling are intentionally separate from the search implementation in solver.py.
"""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from solver import (
    Board, PuzzleConflictError, PuzzleFormatError, SearchStats,
    is_valid_solution, read_puzzle, solve, validate_initial_board,
)

CELL_FONT = ("Helvetica", 20)
CLUE_FONT = ("Helvetica", 20, "bold")
SOLVED_COLOUR = "#0b7790"
CLUE_COLOUR = "#18283a"
EDIT_COLOUR = "#354459"


def parse_cell_text(values: list[list[str]]) -> Board:
    """Convert a 9x9 grid of GUI strings into a board, with 0 for blank."""
    if len(values) != 9 or any(len(row) != 9 for row in values):
        raise PuzzleFormatError("The grid must have exactly 9 rows and columns.")
    board: Board = []
    for row_index, row in enumerate(values, 1):
        digits: list[int] = []
        for column_index, text in enumerate(row, 1):
            value = text.strip()
            if value in {"", "0"}:
                digits.append(0)
            elif len(value) == 1 and value in "123456789":
                digits.append(int(value))
            else:
                raise PuzzleFormatError(
                    f"Cell ({row_index}, {column_index}) must be blank or a digit 1-9."
                )
        board.append(digits)
    validate_initial_board(board)
    return board


class SudokuGUI:
    """Simple editor and visualisation; all CSP logic lives in solver.py."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Sudoku Solver  |  Backtracking + MRV")
        self.root.configure(bg="#f3f6fb")
        self.root.minsize(630, 730)

        self.loaded_board: Board = [[0] * 9 for _ in range(9)]
        self.inputs: list[list[tk.Entry]] = []
        self.buttons: list[ttk.Button] = []
        self.status_var = tk.StringVar(value="Ready. Open a puzzle, or enter one manually.")
        self.filename_var = tk.StringVar(value="No file selected")
        self.stats_var = tk.StringVar(value="No search has been run.")
        self._busy = False
        self._result_queue: queue.Queue[tuple[Board | None, SearchStats] | Exception] = queue.Queue()
        self._build_layout()

        # Load a sample if the bundled puzzle exists; a fresh empty GUI also works.
        example = Path(__file__).resolve().parent / "puzzles" / "euler_01.txt"
        if example.exists():
            self._load_board(read_puzzle(example), example.name)

        self.root.bind("<Control-o>", self._shortcut_open)
        self.root.bind("<Command-o>", self._shortcut_open)
        self.root.bind("<Control-Return>", self._shortcut_solve)
        self.root.bind("<Command-Return>", self._shortcut_solve)

    def _build_layout(self) -> None:
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Action.TButton", padding=(13, 8), font=("Helvetica", 11))

        outer = tk.Frame(self.root, bg="#f3f6fb")
        outer.pack(fill="both", expand=True, padx=18, pady=12)
        tk.Label(outer, text="SUDOKU", font=("Helvetica", 24, "bold"),
                 bg="#f3f6fb", fg="#172b46").pack(anchor="w")
        tk.Label(outer, text="Constraint Satisfaction  •  Recursive Backtracking + MRV",
                 font=("Helvetica", 11), bg="#f3f6fb", fg="#50637d").pack(anchor="w", pady=(0, 12))

        bar = tk.Frame(outer, bg="#f3f6fb")
        bar.pack(fill="x", pady=(0, 7))
        for label, handler in [
            ("Open TXT / CSV", self.open_file),
            ("Solve", self.solve_board),
            ("Reset", self.reset_board),
            ("Clear", self.clear_board),
        ]:
            button = ttk.Button(bar, text=label, command=handler, style="Action.TButton")
            button.pack(side="left", padx=(0, 7))
            self.buttons.append(button)

        tk.Label(outer, textvariable=self.filename_var, font=("Helvetica", 10),
                 bg="#f3f6fb", fg="#53647b", anchor="w").pack(fill="x", pady=(0, 8))

        grid_container = tk.Frame(outer, bg="#172b46", bd=0)
        grid_container.pack(pady=2)
        # Each 3x3 box has a visible separating gutter and its own subtle shade.
        for r in range(9):
            entry_row: list[tk.Entry] = []
            for c in range(9):
                box_r, box_c = r // 3, c // 3
                shade = "#eef4fb" if (box_r + box_c) % 2 == 0 else "#ffffff"
                validate = (self.root.register(self._valid_key), "%P")
                cell = tk.Entry(
                    grid_container, width=2, justify="center", font=CELL_FONT,
                    fg=EDIT_COLOUR, bg=shade, insertbackground="#172b46",
                    relief="flat", bd=0, highlightthickness=0,
                    validate="key", validatecommand=validate,
                )
                cell.grid(row=r, column=c, padx=(3 if c % 3 == 0 else 1,
                                                3 if c == 8 else 1),
                          pady=(3 if r % 3 == 0 else 1, 3 if r == 8 else 1),
                          ipadx=7, ipady=7)
                cell.bind("<FocusIn>", lambda e: e.widget.select_range(0, tk.END))
                cell.bind("<KeyRelease>", self._cell_changed)
                entry_row.append(cell)
            self.inputs.append(entry_row)

        tk.Label(outer, text="0 or an empty cell means blank  •  Given digits are bold  •  Solved digits are blue",
                 font=("Helvetica", 10), bg="#f3f6fb", fg="#667892").pack(pady=(12, 12))

        stats_frame = tk.LabelFrame(
            outer, text="Search metrics (solver only)", bg="#f3f6fb", fg="#172b46",
            font=("Helvetica", 11, "bold"), relief="groove", padx=12, pady=9,
        )
        stats_frame.pack(fill="x")
        tk.Label(stats_frame, textvariable=self.stats_var, justify="left", anchor="w",
                 bg="#f3f6fb", fg="#233b58", font=("Courier", 11),
                 wraplength=590).pack(fill="x")

        status_frame = tk.Frame(outer, bg="#e6edf5", padx=12, pady=10)
        status_frame.pack(fill="x", pady=(12, 0))
        tk.Label(status_frame, textvariable=self.status_var, bg="#e6edf5", fg="#243750",
                 font=("Helvetica", 11), anchor="w", wraplength=580,
                 justify="left").pack(fill="x")

    @staticmethod
    def _valid_key(proposed: str) -> bool:
        return len(proposed) <= 1 and (not proposed or proposed in "0123456789")

    def _cell_changed(self, event: tk.Event) -> None:
        widget = event.widget
        if isinstance(widget, tk.Entry) and not self._busy:
            widget.configure(font=CELL_FONT, fg=EDIT_COLOUR)
            self.status_var.set("Board edited. Press Solve to search from the current grid.")
            self.stats_var.set("No search has been run on the edited grid.")

    def _grid_values(self) -> list[list[str]]:
        return [[entry.get() for entry in row] for row in self.inputs]

    def _paint(self, board: Board, givens: Board | None = None) -> None:
        givens = board if givens is None else givens
        for r in range(9):
            for c in range(9):
                entry = self.inputs[r][c]
                entry.configure(state="normal")
                entry.delete(0, tk.END)
                if board[r][c]:
                    entry.insert(0, str(board[r][c]))
                clue = bool(givens[r][c])
                entry.configure(font=CLUE_FONT if clue else CELL_FONT,
                                fg=CLUE_COLOUR if clue else SOLVED_COLOUR)
                if self._busy:
                    entry.configure(state="disabled")

    def _load_board(self, board: Board, name: str) -> None:
        self.loaded_board = [row.copy() for row in board]
        self._paint(board)
        self.filename_var.set(f"Loaded: {name}")
        self.status_var.set("Puzzle loaded. Press Solve, or edit any cell first.")
        self.stats_var.set("No search has been run.")

    def open_file(self) -> None:
        if self._busy:
            return
        path = filedialog.askopenfilename(
            parent=self.root, title="Open a Sudoku puzzle",
            filetypes=[("Sudoku puzzles", "*.txt *.csv"), ("Text files", "*.txt"),
                       ("CSV files", "*.csv")],
        )
        if not path:
            return
        try:
            board = read_puzzle(path)
        except (OSError, PuzzleFormatError, PuzzleConflictError) as exc:
            self.status_var.set(f"Cannot open puzzle: {exc}")
            messagebox.showerror("Invalid puzzle", str(exc), parent=self.root)
            return
        self._load_board(board, Path(path).name)

    def reset_board(self) -> None:
        if self._busy:
            return
        self._paint(self.loaded_board)
        self.status_var.set("Restored the last loaded puzzle.")
        self.stats_var.set("No search has been run.")

    def clear_board(self) -> None:
        if self._busy:
            return
        blank = [[0] * 9 for _ in range(9)]
        self._load_board(blank, "Blank board (manual entry)")
        self.status_var.set("Blank board. Enter clues, or open a file.")

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        new_state = "disabled" if busy else "normal"
        for button in self.buttons:
            button.configure(state=new_state)
        for row in self.inputs:
            for entry in row:
                entry.configure(state=new_state)

    def solve_board(self) -> None:
        if self._busy:
            return
        try:
            current = parse_cell_text(self._grid_values())
        except (PuzzleFormatError, PuzzleConflictError) as exc:
            self.stats_var.set("No search was run (input validation failed).")
            self.status_var.set(f"Invalid puzzle: {exc}")
            messagebox.showerror("Invalid puzzle", str(exc), parent=self.root)
            return

        self._set_busy(True)
        self.status_var.set("Solving... searching with backtracking + MRV.")
        self.stats_var.set("Search in progress...")
        self._result_queue = queue.Queue()

        def worker() -> None:
            try:
                self._result_queue.put(solve(current))
            except Exception as exc:  # sent to main thread for display
                self._result_queue.put(exc)

        threading.Thread(target=worker, daemon=True).start()
        self.root.after(40, self._read_result, current)

    def _read_result(self, original: Board) -> None:
        try:
            result = self._result_queue.get_nowait()
        except queue.Empty:
            self.root.after(40, self._read_result, original)
            return
        self._set_busy(False)
        if isinstance(result, Exception):
            self.status_var.set(f"Solver error: {result}")
            self.stats_var.set("No valid result returned.")
            messagebox.showerror("Solver error", str(result), parent=self.root)
            return

        solution, stats = result
        self.stats_var.set(
            f"Time: {stats.elapsed_seconds * 1000:.3f} ms   "
            f"Nodes: {stats.nodes}   Assignments: {stats.assignments}\n"
            f"Backtracks: {stats.backtracks}   Dead ends: {stats.dead_ends}"
        )
        if solution is None:
            self._paint(original)
            self.status_var.set("No solution exists for this Sudoku puzzle.")
            return
        if not is_valid_solution(original, solution):
            self.status_var.set("Internal error: the solution is invalid.")
            return
        self._paint(solution, original)
        self.status_var.set("Solved successfully. Blue digits were filled by the search algorithm.")

    def _shortcut_open(self, _event: tk.Event) -> None:
        self.open_file()

    def _shortcut_solve(self, _event: tk.Event) -> None:
        self.solve_board()


def main() -> None:
    root = tk.Tk()
    SudokuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
