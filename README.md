# F29AI Coursework 1 — Combined Code Submission

This archive combines the Python Sudoku solver from **Part 1B** and **exactly five PDDL source files** from **Part 2A–2C**. The PDDL directory structure, filenames, domain names, and problem names match the original starter package. The source files contain explanatory comments.

**Language and dependencies:** Python **3.10 or newer** (tested on Python 3.13.5); **no third-party Python packages** are needed for the Sudoku command-line solver or benchmark. The optional GUI uses Python's standard-library **Tkinter** with an available graphical display. No Sudoku- or CSP-solver library is used.

## Part 1B — Sudoku (Python)

From the extracted package directory:

```bash
cd sudoku
python solver.py puzzles/euler_01.txt
python solver.py puzzles/euler_09.txt --stats
python solver.py puzzles/unsolvable.txt --stats
python gui.py
python -m unittest discover -s tests -v
```

`solver.py` is the required command-line implementation. It reads 9x9 Sudoku puzzles from `.txt` or `.csv` files, where **0 means empty**. It prints a legible solution or reports that the puzzle has no solution. The implemented search is recursive **backtracking with Minimum Remaining Values (MRV)**, implemented in project code rather than an external solver. `gui.py` is an optional interactive front end calling that same search function.

To reproduce the performance measurements:

```bash
python benchmark.py puzzles/euler_*.txt --repeat 11 --csv new_results.csv
```

The `puzzles/` directory contains representative and regression test inputs. Original puzzle provenance is in `puzzle_sources.csv`; the recorded student Mac benchmark results and environment are included for reproducibility. More complete instructions are in `sudoku/README.md`.

## Part 2 — PDDL files (exact starter layout)

```text
PDDL/
├── PartA&B/
│   ├── domain.pddl       (domain: lunar)
│   ├── mission1.pddl     (problem: lunar-mission-1)
│   └── mission2.pddl     (problem: lunar-mission-2)
└── PartC/
    ├── domain-ext.pddl   (domain: lunar-extended)
    └── mission3.pddl     (problem: lunar-mission-3)
```

`domain.pddl` is shared by Missions 1 and 2; `domain-ext.pddl` adds astronaut constraints for Mission 3. Both use only PDDL `:strips` and `:typing`. To generate plans, open the corresponding domain/problem pair in a supported PDDL planner, for example Pyperplan 2.1 or a course-approved planner:

- Mission 1: `PDDL/PartA&B/domain.pddl` + `PDDL/PartA&B/mission1.pddl`
- Mission 2: `PDDL/PartA&B/domain.pddl` + `PDDL/PartA&B/mission2.pddl`
- Mission 3: `PDDL/PartC/domain-ext.pddl` + `PDDL/PartC/mission3.pddl`

The three supplied models were previously run using Pyperplan 2.1 (`gbf` + `hff`) and produced executable plans of 10, 20, and 24 actions, respectively. Planner software is **not bundled** and is not needed for the Sudoku solver. No supplementary PDDL problem files are included.
