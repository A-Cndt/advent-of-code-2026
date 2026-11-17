# Advent of Code solver (GUI)

![CI](https://github.com/A-Cndt/advent-of-code-2026/actions/workflows/ci.yml/badge.svg)
![Quality](https://github.com/A-Cndt/advent-of-code-2026/actions/workflows/quality.yml/badge.svg)
![License](https://img.shields.io/github/license/A-Cndt/advent-of-code-2026)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)

A small desktop application to work on [Advent of Code](https://adventofcode.com)
puzzles day by day: pick a day, fetch the puzzle page and your personal input,
then run your own `part1` / `part2` functions on the examples or on your input.

> The interface labels are currently in French; code and comments are in English.

## Features

- Calendar sidebar to choose the day.
- Fetches the puzzle page (to extract the example blocks) and your personal
  input from adventofcode.com. The input is downloaded only once and cached.
- Runs `part1(data)` / `part2(data)` from `days/dayXX/solution.py`, which is
  reloaded on every run (no restart needed).
- Compares the example results with the expected values you enter.
- Copies the result of your input to the clipboard.
- Shows the result, the execution time and everything your code prints.

## Getting started

```bash
pip install -r requirements.txt
python app.py
```

1. Click **Cookie de session** and paste the value of your `session` cookie
   (browser developer tools > Cookies > adventofcode.com).
2. Select a day, then click **Récupérer énoncé + input**.
3. Click **Éditer solution.py** and write your solution.
4. Run it with **F5** / **F6** (part 1 / part 2), **F7** (both parts).

Requires Python 3.9+ and PySide6.

## Writing a solution

Each day has its own folder, created automatically with this skeleton:

```python
def parse(data):
    return data.strip().splitlines()

def part1(data):
    lines = parse(data)
    return None

def part2(data):
    lines = parse(data)
    return None
```

`data` is the raw text of the example or of your input. Whatever the function
returns is displayed (and compared with the expected value for examples).

## Keyboard shortcuts

| Key | Action |
| --- | --- |
| `F5` / `F6` | Run part 1 / part 2 on the active tab |
| `F7` | Run both parts one after the other |
| `Ctrl+E` / `Ctrl+I` | Show the Example / Input tab |

## Project layout

```text
app.py              entry point
requirements.txt
src/
    aoc_core.py     files, network, execution of the solutions
    aoc_gui.py      PySide6 interface
days/
    day01/solution.py
    ...
```

## Configuration

| Environment variable | Purpose |
| --- | --- |
| `AOC_SESSION` | Session cookie (alternative to the `.aoc_session` file) |
| `AOC_CONTACT` | Contact details appended to the `User-Agent` header (e-mail, repository URL...) |

## Security and Advent of Code etiquette

- Your session cookie is a credential. It is stored in `.aoc_session`, which
  is git-ignored and restricted to your user where the OS supports it. Never
  commit it; if it ever ends up in a commit, remove it from the history and
  log in again to get a new one.
- Advent of Code asks not to share puzzle texts or personal inputs. The
  `.gitignore` therefore tracks only `days/*/solution.py`; inputs, examples
  and scraped puzzle data stay local.
- The application only contacts adventofcode.com when you click the fetch
  button, and never downloads the same input twice.
- Set `AOC_CONTACT` so the maintainers can reach you if your tool misbehaves.
