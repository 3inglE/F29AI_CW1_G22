"""Sudoku solver using depth-first backtracking with MRV (no propagation)."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter


SIZE = 9
BOX_SIZE = 3
DIGITS = frozenset(range(1, SIZE + 1))
Board = list[list[int]]


class PuzzleFormatError(ValueError):
    """The file or board has an invalid shape or value."""


class PuzzleConflictError(ValueError):
    """Two initial nonzero clues violate a Sudoku rule."""


@dataclass
class SearchStats:
    """Counts for one search run; elapsed_seconds excludes file I/O and output."""

    nodes: int = 0          # Number of recursive calls, including the root.
    assignments: int = 0    # Number of legal candidate placements attempted.
    backtracks: int = 0     # Number of placements undone after a failed subtree.
    dead_ends: int = 0      # Number of states containing an empty cell with no candidates.
    elapsed_seconds: float = 0.0


def read_puzzle(path: str | Path) -> Board:
    """Read exactly nine rows of digits 0-9, separated by spaces or commas."""
    path = Path(path)
    if path.suffix.lower() not in {".txt", ".csv"}:
        raise PuzzleFormatError("Only .txt and .csv files are supported.")

    text = path.read_text(encoding="utf-8-sig")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) != SIZE:
        raise PuzzleFormatError(f"Expected 9 non-empty rows; found {len(lines)}.")

    board: Board = []
    for row_index, line in enumerate(lines, start=1):
        values = [part.strip() for part in line.split(",")] if "," in line else line.split()
        if len(values) != SIZE:
            raise PuzzleFormatError(f"Row {row_index} must contain 9 digits; found {len(values)}.")
        if any(len(value) != 1 or value not in "0123456789" for value in values):
            raise PuzzleFormatError(f"Row {row_index} contains invalid data; use individual digits 0-9.")
        board.append([int(value) for value in values])

    validate_initial_board(board)
    return board


def validate_initial_board(board: Board) -> None:
    """Validate dimensions, values, and conflicts among the given clues."""
    if len(board) != SIZE or any(len(row) != SIZE for row in board):
        raise PuzzleFormatError("The board must contain exactly 9 rows and 9 columns.")

    rows = [set() for _ in range(SIZE)]
    columns = [set() for _ in range(SIZE)]
    boxes = [set() for _ in range(SIZE)]

    for r in range(SIZE):
        for c in range(SIZE):
            value = board[r][c]
            if type(value) is not int or not 0 <= value <= SIZE:
                raise PuzzleFormatError(f"Cell ({r + 1}, {c + 1}) must be an integer from 0 to 9.")
            if value == 0:
                continue

            box_index = (r // BOX_SIZE) * BOX_SIZE + c // BOX_SIZE
            if value in rows[r] or value in columns[c] or value in boxes[box_index]:
                raise PuzzleConflictError(
                    f"Given digit {value} at ({r + 1}, {c + 1}) conflicts with another clue."
                )
            rows[r].add(value)
            columns[c].add(value)
            boxes[box_index].add(value)


def get_candidates(board: Board, row: int, col: int) -> set[int]:
    """Return all digits currently permitted in one empty cell."""
    if board[row][col] != 0:
        return set()

    used = set(board[row])
    used.update(board[r][col] for r in range(SIZE))
    start_row = (row // BOX_SIZE) * BOX_SIZE
    start_col = (col // BOX_SIZE) * BOX_SIZE
    used.update(
        board[r][c]
        for r in range(start_row, start_row + BOX_SIZE)
        for c in range(start_col, start_col + BOX_SIZE)
    )
    return DIGITS - used


def select_mrv(board: Board) -> tuple[int, int, set[int]] | None:
    """Choose the empty cell with fewest candidates (row-major on ties)."""
    best: tuple[int, int, set[int]] | None = None
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != 0:
                continue
            candidates = get_candidates(board, row, col)
            if not candidates:  # Immediately prune a contradictory search state.
                return row, col, candidates
            if best is None or len(candidates) < len(best[2]):
                best = row, col, candidates
    return best  # None means the grid has no empty cells.


def _backtrack(board: Board, stats: SearchStats) -> bool:
    stats.nodes += 1
    choice = select_mrv(board)
    if choice is None:
        return True

    row, col, candidates = choice
    if not candidates:
        stats.dead_ends += 1
        return False

    for digit in sorted(candidates):  # Deterministic, reproducible search order.
        board[row][col] = digit
        stats.assignments += 1
        if _backtrack(board, stats):
            return True
        board[row][col] = 0
        stats.backtracks += 1
    return False


def is_valid_solution(original: Board, solution: Board) -> bool:
    """Independently verify constraints and preservation of the given clues."""
    try:
        validate_initial_board(original)
        validate_initial_board(solution)
    except (PuzzleFormatError, PuzzleConflictError):
        return False
    return all(
        solution[r][c] != 0
        and (original[r][c] == 0 or original[r][c] == solution[r][c])
        for r in range(SIZE)
        for c in range(SIZE)
    )


def solve(original: Board) -> tuple[Board | None, SearchStats]:
    """Solve one board without mutating the input; return None if unsatisfiable."""
    validate_initial_board(original)
    working = [row.copy() for row in original]
    stats = SearchStats()

    start = perf_counter()
    found = _backtrack(working, stats)
    stats.elapsed_seconds = perf_counter() - start

    if not found:
        return None, stats
    if not is_valid_solution(original, working):
        raise RuntimeError("Internal solver error: an invalid solution was produced.")
    return working, stats


def format_board(board: Board) -> str:
    """Present the grid with 3×3 boundaries; zero is shown as a dot."""
    separator = "+-------+-------+-------+"
    output = [separator]
    for r, row in enumerate(board):
        groups = [" ".join(str(value) if value else "." for value in row[c:c + 3])
                  for c in (0, 3, 6)]
        output.append("| " + " | ".join(groups) + " |")
        if (r + 1) % BOX_SIZE == 0:
            output.append(separator)
    return "\n".join(output)


def main() -> int:
    parser = argparse.ArgumentParser(description="Solve a 9x9 Sudoku using backtracking and MRV.")
    parser.add_argument("puzzle", type=Path, help="Path to the input puzzle (.txt or .csv).")
    parser.add_argument("--stats", action="store_true", help="Display search performance metrics.")
    args = parser.parse_args()

    try:
        original = read_puzzle(args.puzzle)
        solution, stats = solve(original)
    except (OSError, PuzzleFormatError, PuzzleConflictError) as error:
        parser.exit(status=2, message=f"Input error: {error}\n")

    if solution is None:
        print("No solution exists for this Sudoku puzzle.")
    else:
        print("Sudoku solved successfully:")
        print(format_board(solution))

    if args.stats:
        print(f"Search time: {stats.elapsed_seconds * 1000:.3f} ms")
        print(f"Search nodes: {stats.nodes}")
        print(f"Attempted assignments: {stats.assignments}")
        print(f"Backtracks: {stats.backtracks}")
        print(f"Dead ends: {stats.dead_ends}")
    return 0 if solution is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
