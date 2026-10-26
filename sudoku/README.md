# Sudoku solver: recursive backtracking + MRV

**Coursework:** F29AI, Part 1B. **Language:** Python 3.10+; no external dependencies. All search logic is implemented locally using the Python standard library. The Sudoku rules are the standard 9 x 9 row/column/box constraints.

## Quick start

Run from the folder containing `solver.py`:

```bash
python solver.py puzzles/euler_01.txt
python solver.py puzzles/euler_09.txt --stats
python solver.py puzzles/unsolvable.txt --stats
python -m unittest discover -s tests -v
```

Input format: `.txt` = 9 space-separated rows, each with 9 digits; `.csv` = 9 comma-separated rows, also 9 digits each. Use 0 for blank cells. UTF-8 input is supported. The program prints a completed 9 x 9 grid with 3 x 3 divisions, or an explicit 'No solution' message. Invalid format/clues are reported separately. Exit status: 0 = solved, 1 = consistent clues but no solution, 2 = invalid input or conflicting clues.

## Implemented search (no solver libraries)

`read_puzzle()` -> `validate_initial_board()` -> recursive `_backtrack()` -> `is_valid_solution()` -> `format_board()`.

- `get_candidates()`: for each empty cell (r,c), compute `{1,...,9} - (used in row r, column c, 3x3 box)`.
- `select_mrv()`: scan empty cells in row-major order and choose the fewest candidates; zero candidates implies a dead end. Ties resolve in row-major order.
- `_backtrack()`: try candidate digits in increasing order, recurse, and undo the assignment if the recursive branch fails. Stops at the first complete solution.
- `solve()`: deep-copies rows before search, times search only, validates results after search, and returns a `SearchStats` object.

**Not implemented:** forward checking with persistent domain updates, AC-3, or full constraint propagation. Candidate sets are recomputed on demand; scanning them at MRV selection is not claimed as a separate propagation algorithm.

## Benchmark and dataset

10 consecutive puzzles, labelled `euler_01.txt` through `euler_10.txt`, were transcribed from **Project Euler Problem 96, Grids 01-10**: https://projecteuler.net/resources/documents/0096_sudoku.txt . The source describes the full 50-puzzle collection as ranging in difficulty and having unique solutions; it does **not** assign a numerical difficulty to each grid. We therefore do not relabel individual grids 'easy/medium/hard'. Other example/negative-test files are carried over from the initial project; see `puzzle_sources.csv` for attribution and caveats. The previous `hard.txt` matches the published `grid2` in https://www.norvig.com/sudoku.html .

To reproduce all ten benchmarks:

```bash
python benchmark.py puzzles/euler_*.txt --repeat 11 --csv results_euler_mac.csv
```

On platforms that do not expand a `*` shell wildcard, supply the ten filenames individually. For negative-case timing:

```bash
python benchmark.py puzzles/unsolvable.txt --repeat 11 --csv results_unsolvable_mac.csv
```

**Statistics:** `nodes` = calls to `_backtrack` including initial and success state; `assignments` = legal candidate placements attempted; `backtracks` = attempted placements undone after their recursive subtree failed; `dead_ends` = states whose MRV scan found an empty cell with zero candidates. For this deterministic implementation `nodes = assignments + 1`. `median_ms` = median of 11 `perf_counter()` timings for search only, excluding file parsing, clue checks, solution validation and printing. CSV adds `blanks` and `repeats`. Runs are sequential on one process with no intentional parallelism or cold-start separation; timing is machine dependent. The search counters are deterministic given fixed ordering.

For the student Mac apparatus and the exact run protocol, see `experiment_protocol.md` and `experiment_environment.txt`. The supplied CSV is a measured snapshot, not a hardware-independent guarantee.

## Tests

```bash
python -m unittest discover -s tests -v
```

The suite covers the 10 externally sourced test grids; preserving clues and the caller input; an already solved grid; a one-blank grid; invalid shape/token; CSV parsing; conflicting clues; and a valid-clues but unsatisfiable puzzle. The solver returns one solution; it does not claim to enumerate all solutions or test uniqueness.

## Files

- `solver.py` - the core algorithm and command-line interface.
- `benchmark.py` - repeated benchmarks, statistics and CSV export.
- `tests/test_solver.py` - automatic correctness tests.
- `puzzles/` - sample inputs and ten sourced benchmarks.
- `puzzle_sources.csv` - provenance for each input file.
- `results_euler_mac.csv`, `results_unsolvable_mac.csv` - 16 Oct 2026 Mac measurements; `results_all_mac.csv` combines them; `experiment_environment.txt` records the apparatus.
- `experiment_protocol.md` - test apparatus and limitations.
- The coursework report and demonstration video are separate submission materials; no report draft is included here.

## Graphical interface (Tkinter)

A separate 9 x 9 graphical front end is provided in `gui.py`. It calls the **same** `solve()` implementation as the command-line program; it does not implement a second algorithm and does not use a Sudoku-solving library.

From the `sudoku` folder, run on a desktop machine:

```bash
python -m tkinter           # optional: confirm that Tkinter opens on your Mac
python gui.py               # open the graphical solver
```

- The grid starts with `puzzles/euler_01.txt` if that bundled file is available. Open a `.txt` or `.csv` puzzle using **Open TXT / CSV**, or press **Clear** to type your own clues. A blank field or a zero represents an empty cell.
- **Solve** uses recursive backtracking + MRV in a worker thread, colours solution-filled digits differently from original clues, displays status (solved / no solution / invalid input) and shows search-only timing plus nodes, assignments, backtracks and dead ends.
- **Reset** restores the most recently loaded puzzle; **Clear** starts a new manual board. Invalid clues or input files produce an error message without changing the last successfully loaded puzzle.
- `Command-O` (macOS) or `Ctrl-O` opens a file; `Command-Return` / `Ctrl-Return` starts solving.
- The GUI uses Python's built-in `tkinter` package, which is normally bundled with the macOS python.org Python distribution. If `python -m tkinter` fails, install a Python/Tcl-Tk distribution with Tk support; the CLI remains available without Tk.

On a Mac, run `python gui.py` as a final manual smoke test before recording the demo. The GUI was also exercised in a virtual graphical display using `xvfb-run -a python -m unittest discover -s tests -v`, including open / solve / reset / clear, unsatisfiable input, contradictory clues and cancelled dialogs. GUI timings are not used in the existing command-line benchmark dataset.

**Academic integrity:** Review your institution's AI-use and academic integrity policies. Ensure that you understand and can explain the submitted source code, and disclose any assistance as required.
