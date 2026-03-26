# dAIana 🎯

> A terminal-first CLI for LaTeX CV & cover letter automation, with built-in job application tracking.

No GUI. No fuss. Fill in a few prompts, get a compiled PDF, and track where you applied — all from your terminal.

---

## Requirements

- Python ≥ 3.8
- `pdflatex` installed and on your PATH
- LaTeX templates placed at `cv_and_letter/template_cv.tex` and `cv_and_letter/template_cl.tex`

---

## Installation

```bash
git clone https://github.com/PanoPepino/Daiana.git
cd Daiana
pip install -e .
```

Verify it works:

```bash
daiana --help
```

---

## Commands

### `daiana compile`

Renders a LaTeX template and compiles it to PDF. Prompts you interactively for job details (position, company, location, career path, link). After compiling, optionally saves the job to a CSV tracker.

**Flags:**

| Flag | Description |
|------|-------------|
| `--cv` | Use the CV template (`template_cv.tex`) |
| `--cl` | Use the cover letter template (`template_cl.tex`) |
| `--username` / `-un` | Your name, used in the output PDF filename (default: `user_name`) |

```bash
daiana compile --cv --username john
daiana compile --cl --username john
```

Cover letter mode asks two extra prompts: your tailored background and the company's challenge(s).

---

### `daiana save`

Manually saves a job application to a per-career CSV file, without compiling a document. Useful when you apply externally and just want to log it.

**Flags:**

| Flag | Description |
|------|-------------|
| `--career` / `-cp` | Career path label, e.g. `"software"` *(required)* |

```bash
daiana save --career software
```

Prompts: job position, company name, location, and an optional link.

---

### `daiana show`

Displays the last N saved applications for a given career path in a formatted table with color-coded status history.

**Flags:**

| Flag | Description |
|------|-------------|
| `--career` / `-cp` | Career path label *(required)* |
| `--rows` / `-rj` | Number of recent entries to display (default: `20`) |

```bash
daiana show --career software
daiana show --career software --rows 10
```

---

### `daiana update`

Updates the status of a saved job application. Finds the matching entry by position + company, shows current status, and lets you set a new one.

**Flags:**

| Flag | Description |
|------|-------------|
| `--career` / `-cp` | Career path label *(required)* |

```bash
daiana update --career software
```

If multiple entries match, you pick from a numbered list. Allowed statuses are defined in `daiana/utils/constants.py`.

---

## Project Structure

```
daiana/
├── cli.py              # Entry point, registers all commands
├── commands/           # Click command wrappers (one per command)
│   ├── compiler_cli.py
│   ├── saver_cli.py
│   ├── shower_cli.py
│   └── updater_cli.py
├── core/               # Business logic (no Click dependencies)
│   ├── compiler.py     # pdflatex runner
│   ├── saver.py        # CSV write logic
│   ├── shower.py       # CSV read logic
│   └── updater.py      # CSV update logic
└── utils/
    ├── for_latex.py    # Template rendering (replace_newcommand)
    ├── for_csv.py      # CSV helpers, history formatting
    └── constants.py    # Allowed statuses, color map
```

---

## Notes

- CSV files are stored per career path (e.g., `software_jobs.csv`) in your working directory.
- Status history is stored as JSON inside the CSV, rendered with colors in the terminal.
- `.DS_Store` and `__pycache__` should be added to `.gitignore`.
