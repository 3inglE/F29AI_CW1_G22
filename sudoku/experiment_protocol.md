# Performance experiment protocol (Part 1B)

## Input set and provenance

The evaluation uses the **first ten consecutive puzzles**, Grids 01-10, from Project Euler, Problem 96. Source: https://projecteuler.net/resources/documents/0096_sudoku.txt (accessed 15 October 2026). The official source describes its collection of fifty puzzles as varying in difficulty with unique solutions; it does not label each of our selected ten grids with a validated difficulty rating. The fixed selection (01-10) avoids choosing only puzzles that favor the method. `puzzle_sources.csv` gives exact file-to-grid mappings and clue counts.

Separate functionality tests include a complete grid, a single blank, conflicting clues, malformed files, CSV, and consistent but unsatisfiable clues. The unsatisfiable input is a negative functionality test, not part of the ten-puzzle solvable benchmark.

## Method

1. Run `python -m unittest discover -s tests -v`. This should pass all twelve test methods (one iterates over the ten Project Euler grids).
2. From the project root, run `python benchmark.py puzzles/euler_*.txt --repeat 11 --csv results_euler.csv` (POSIX shell). Run the same command using ten explicit filenames if shell globbing is unsupported.
3. For the negative case, run `python benchmark.py puzzles/unsolvable.txt --repeat 11 --csv results_unsolvable.csv`.
4. For each puzzle, the runner reads/clue-validates the puzzle once and invokes `solve` eleven times. `perf_counter` times only the recursive `_backtrack` call, excluding file I/O, initial clue checking, final solution validation and printing; it reports the median of eleven observations.
5. Candidate values are tried in ascending numeric order. MRV ties use row-major ordering. The script asserts all repetitions return identical solutions and deterministic counters, and independently checks solved grids.

## Machine and runtime (student Mac measurements)

- Benchmark date: 16 October 2026, local time in the uploaded `environment.txt`.
- Python: CPython 3.13.5.
- Operating system: macOS 26.4; architecture: arm64.
- Machine identifier: Mac17,3 (MacBook Air as reported by the operator).
- Repetitions: 11 sequential runs per puzzle in one process, no intentional parallelism.
- `median_ms` is the median search-only elapsed time measured by `perf_counter()`.
- Source evidence: `results_euler_mac.csv`, `results_unsolvable_mac.csv`, `experiment_environment.txt`.
- Results vary with CPU load, hardware and timing noise; deterministic node and backtrack counts are reproducible for the same algorithm/ordering.

## Counter semantics

- `nodes`: number of recursive calls, including the initial/root and final successful state.
- `assignments`: candidate placements actually attempted (always `nodes - 1` here).
- `backtracks`: placements undone after the child subtree failed.
- `dead_ends`: recursive states in which the MRV scan finds an empty cell without legal values.
- `blanks`: zeros in the input.
- `median_ms`: median search time across repetitions.

## Interpretation limitations

The experiment demonstrates correctness and search effort across these specific instances. It **does not** establish that MRV outperforms plain backtracking, because there is no baseline implementation, and it does not estimate population-level performance of all Sudoku puzzles. Puzzle clue count is not a reliable difficulty rating, and the external source does not rate individual grids. Timing differences of a few milliseconds may reflect runtime noise. No timeout/performance claim is made for every logically valid puzzle; worst-case search remains exponential. The long-running Norvig `hard1` test was not included in the standard dataset or report.
