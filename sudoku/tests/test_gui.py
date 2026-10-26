"""GUI input and headless-display tests; run with xvfb-run on Linux."""

import time
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gui import SudokuGUI, parse_cell_text
from solver import PuzzleConflictError, PuzzleFormatError, read_puzzle

try:
    import tkinter as tk
except ImportError:
    tk = None

BASE = Path(__file__).resolve().parents[1]


class GridParsingTests(unittest.TestCase):
    def test_zeros_and_blanks(self):
        cells = [[""] * 9 for _ in range(9)]
        cells[0][0] = "5"
        cells[0][4] = "0"
        result = parse_cell_text(cells)
        self.assertEqual(result[0][0], 5)
        self.assertEqual(result[0][4], 0)

    def test_invalid_value(self):
        cells = [[""] * 9 for _ in range(9)]
        cells[0][0] = "11"
        with self.assertRaises(PuzzleFormatError):
            parse_cell_text(cells)

    def test_conflicting_clues(self):
        cells = [[""] * 9 for _ in range(9)]
        cells[0][0] = cells[0][1] = "7"
        with self.assertRaises(PuzzleConflictError):
            parse_cell_text(cells)

    def test_invalid_shape(self):
        with self.assertRaises(PuzzleFormatError):
            parse_cell_text([[""] * 9] * 8)


@unittest.skipIf(tk is None, "Tkinter not installed")
class WindowTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest(f"No graphical display available: {exc}")
        self.root.withdraw()
        self.app = SudokuGUI(self.root)

    def tearDown(self):
        if hasattr(self, "root"):
            self.root.destroy()

    def _await_solver(self):
        until = time.monotonic() + 5.0
        while self.app._busy and time.monotonic() < until:
            self.root.update()
            time.sleep(0.01)
        self.assertFalse(self.app._busy, "GUI solver did not finish")
        self.root.update()

    def test_sample_loaded_and_reset_after_solving(self):
        initial = self.app._grid_values()
        self.assertEqual(initial[0][0], "")
        self.app.solve_board()
        self._await_solver()
        solved = self.app._grid_values()
        self.assertTrue(all(value in "123456789" for row in solved for value in row))
        self.assertIn("Solved successfully", self.app.status_var.get())
        self.assertIn("Nodes:", self.app.stats_var.get())
        self.app.reset_board()
        self.assertEqual(self.app._grid_values(), initial)

    def test_unsolvable_remains_unsolved(self):
        board = read_puzzle(BASE / "puzzles" / "unsolvable.txt")
        self.app._load_board(board, "unsolvable.txt")
        self.app.solve_board()
        self._await_solver()
        self.assertIn("No solution", self.app.status_var.get())
        self.assertEqual(self.app._grid_values(), [[str(v) if v else "" for v in row] for row in board])

    def test_invalid_edit_does_not_crash_gui(self):
        self.app.clear_board()
        self.app.inputs[0][0].insert(0, "7")
        self.app.inputs[0][1].insert(0, "7")
        with patch("gui.messagebox.showerror"):
            self.app.solve_board()
        self.assertFalse(self.app._busy)
        self.assertIn("Invalid puzzle", self.app.status_var.get())

    def test_clear_and_open_csv(self):
        self.app.clear_board()
        self.assertTrue(all(not v for row in self.app._grid_values() for v in row))
        board = read_puzzle(BASE / "puzzles" / "euler_02.txt")
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "example.csv"
            csv_path.write_text("\n".join(",".join(map(str, row)) for row in board), encoding="utf-8")
            with patch("gui.filedialog.askopenfilename", return_value=str(csv_path)):
                self.app.open_file()
            self.assertEqual(self.app.filename_var.get(), "Loaded: example.csv")
            self.assertEqual(parse_cell_text(self.app._grid_values()), board)
            self.app.solve_board()
            self._await_solver()
            self.app.reset_board()
            self.assertEqual(parse_cell_text(self.app._grid_values()), board)

    def test_cancel_dialog_leaves_grid_unchanged(self):
        before = self.app._grid_values()
        with patch("gui.filedialog.askopenfilename", return_value=""):
            self.app.open_file()
        self.assertEqual(self.app._grid_values(), before)


if __name__ == "__main__":
    unittest.main()
