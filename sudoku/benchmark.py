"""Collect reproducible Sudoku search statistics for an assignment report."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import median

from solver import PuzzleConflictError, PuzzleFormatError, is_valid_solution, read_puzzle, solve


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark backtracking + MRV for the coursework report.")
    parser.add_argument("puzzles", nargs="+", type=Path, help="Paths of input Sudoku puzzles.")
    parser.add_argument("--repeat", type=int, default=11, help="Repeats per puzzle (default 11).")
    parser.add_argument("--csv", type=Path, help="Optional CSV output path.")
    args = parser.parse_args()
    if args.repeat <= 0:
        parser.error("--repeat must be positive")

    results: list[dict[str, str | int | float]] = []
    for path in args.puzzles:
        try:
            board = read_puzzle(path)
            runs = [solve(board) for _ in range(args.repeat)]
        except (OSError, PuzzleFormatError, PuzzleConflictError) as error:
            parser.error(f"{path}: {error}")

        first_solution, first_stats = runs[0]
        for solution, _ in runs:
            if solution is not None and not is_valid_solution(board, solution):
                raise RuntimeError(f"Invalid solved grid for {path}")
        if any(solution != first_solution for solution, _ in runs):
            raise RuntimeError(f"Inconsistent solutions between repetitions: {path}")
        if any(
            (stats.nodes, stats.assignments, stats.backtracks, stats.dead_ends)
            != (first_stats.nodes, first_stats.assignments, first_stats.backtracks, first_stats.dead_ends)
            for _, stats in runs
        ):
            raise RuntimeError(f"Inconsistent search counts between repetitions: {path}")

        row = {
            "puzzle": path.name,
            "blanks": sum(cell == 0 for row in board for cell in row),
            "status": "solved" if first_solution is not None else "unsatisfiable",
            "median_ms": round(median(stats.elapsed_seconds * 1000 for _, stats in runs), 4),
            "nodes": first_stats.nodes,
            "assignments": first_stats.assignments,
            "backtracks": first_stats.backtracks,
            "dead_ends": first_stats.dead_ends,
            "repeats": args.repeat,
        }
        results.append(row)

    keys = ["puzzle", "blanks", "status", "median_ms", "nodes", "assignments", "backtracks", "dead_ends", "repeats"]
    for item in results:
        print(" | ".join(f"{key}={item[key]}" for key in keys))

    if args.csv:
        with args.csv.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        print(f"CSV saved: {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
