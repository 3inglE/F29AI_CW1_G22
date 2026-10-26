"""Run with: python -m unittest discover -s tests -v"""

import tempfile
import unittest
from pathlib import Path

from solver import (
    PuzzleConflictError,
    PuzzleFormatError,
    get_candidates,
    is_valid_solution,
    read_puzzle,
    select_mrv,
    solve,
    validate_initial_board,
)


PUZZLES = Path(__file__).resolve().parents[1] / "puzzles"


class SudokuSolverTests(unittest.TestCase):
    def test_easy_matches_reference_answer(self):
        puzzle = read_puzzle(PUZZLES / "easy.txt")
        before = [row.copy() for row in puzzle]
        answer, stats = solve(puzzle)
        self.assertEqual(answer, read_puzzle(PUZZLES / "solved.txt"))
        self.assertEqual(puzzle, before, "求解不应修改调用者传入的题目")
        self.assertTrue(is_valid_solution(puzzle, answer))
        self.assertGreater(stats.assignments, 0)

    def test_other_puzzles_produce_valid_solutions(self):
        for name in ("medium.txt", "hard.txt"):
            with self.subTest(name=name):
                puzzle = read_puzzle(PUZZLES / name)
                answer, stats = solve(puzzle)
                self.assertIsNotNone(answer)
                self.assertTrue(is_valid_solution(puzzle, answer))
                self.assertEqual(stats.nodes, stats.assignments + 1)

    def test_project_euler_grids_01_to_10(self):
        """All ten independently sourced benchmark inputs have valid solutions."""
        for number in range(1, 11):
            filename = PUZZLES / f"euler_{number:02}.txt"
            with self.subTest(puzzle=filename.name):
                puzzle = read_puzzle(filename)
                previous = [row.copy() for row in puzzle]
                solution, stats = solve(puzzle)
                self.assertIsNotNone(solution)
                self.assertTrue(is_valid_solution(puzzle, solution))
                self.assertEqual(puzzle, previous)
                self.assertEqual(stats.nodes, stats.assignments + 1)

    def test_pre_solved_board_is_unchanged(self):
        solved = read_puzzle(PUZZLES / "solved.txt")
        result, stats = solve(solved)
        self.assertEqual(result, solved)
        self.assertEqual((stats.assignments, stats.backtracks, stats.nodes), (0, 0, 1))

    def test_one_empty_cell(self):
        solved = read_puzzle(PUZZLES / "solved.txt")
        partial = [row.copy() for row in solved]
        partial[0][0] = 0
        self.assertEqual(get_candidates(partial, 0, 0), {5})
        self.assertEqual(select_mrv(partial), (0, 0, {5}))
        answer, stats = solve(partial)
        self.assertEqual(answer, solved)
        self.assertEqual((stats.assignments, stats.backtracks), (1, 0))

    def test_valid_initial_configuration_can_be_unsatisfiable(self):
        puzzle = read_puzzle(PUZZLES / "unsolvable.txt")
        validate_initial_board(puzzle)  # No immediate duplicate clues.
        answer, stats = solve(puzzle)
        self.assertIsNone(answer)
        self.assertGreater(stats.nodes, 0)

    def test_initial_conflicts_are_rejected(self):
        with self.assertRaises(PuzzleConflictError):
            read_puzzle(PUZZLES / "conflict.txt")

    def test_invalid_shape_is_rejected(self):
        with self.assertRaises(PuzzleFormatError):
            solve([[0] * 9 for _ in range(8)])

    def test_invalid_cell_value_is_rejected(self):
        puzzle = [[0] * 9 for _ in range(9)]
        puzzle[0][0] = 10
        with self.assertRaises(PuzzleFormatError):
            solve(puzzle)

    def test_csv_file_supported(self):
        contents = (PUZZLES / "easy.txt").read_text(encoding="utf-8")
        csv_text = "\n".join(",".join(line.split()) for line in contents.splitlines())
        with tempfile.TemporaryDirectory() as folder:
            filename = Path(folder) / "sample.csv"
            filename.write_text(csv_text, encoding="utf-8")
            self.assertEqual(read_puzzle(filename), read_puzzle(PUZZLES / "easy.txt"))

    def test_csv_empty_cell_must_be_explicit_zero(self):
        contents = (PUZZLES / "easy.txt").read_text(encoding="utf-8")
        csv_text = "\n".join(",".join(line.split()) for line in contents.splitlines())
        with tempfile.TemporaryDirectory() as folder:
            filename = Path(folder) / "bad.csv"
            filename.write_text(csv_text.replace("5,3,0", "5,3,", 1), encoding="utf-8")
            with self.assertRaises(PuzzleFormatError):
                read_puzzle(filename)

    def test_bad_file_token_is_rejected(self):
        contents = (PUZZLES / "easy.txt").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as folder:
            filename = Path(folder) / "bad.txt"
            filename.write_text(contents.replace("5 3 0", "5 3 10", 1), encoding="utf-8")
            with self.assertRaises(PuzzleFormatError):
                read_puzzle(filename)


if __name__ == "__main__":
    unittest.main()
