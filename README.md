# dAIana 🏹

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

> Each command is color-coded in the terminal to help you navigate at a glance. Colors come from `daiana/utils/constants.py`.

### 🔵 `daiana compile` <sub>Electric Moonlit Blue `#1AAAF0`</sub>

Renders a LaTeX template and compiles it to PDF. Prompts you interactively for job details (position, company, location, career path, link). After compiling, optionally saves the job to a CSV tracker.

**Flags:**

| Flag | Description |
|------|-------------|
| `--cv` | Use the CV template (`template_cv.tex`) |
| `--cl` | Use the cover letter template (`template_cl.tex`) |
| `--username` / `-un` | Your name, used in the output PDF filename (default: `user_name`) |

Cover letter mode asks two extra prompts: your tailored background and the company's challenge(s).

---

### 🟢 `daiana save` <sub>Vivid Moss Green `#00C878`</sub>

Manually saves a job application to a per-career CSV file, without compiling a document. Useful when you apply externally and just want to log it.

**Flags:**

| Flag | Description |
|------|-------------|
| `--career` / `-cp` | Career path label, e.g. `"software"` *(required)* |

Prompts: job position, company name, location, and an optional link.

---

### 🟫 `daiana show` <sub>Rich Warm Brown `#C88C64`</sub>

Displays the last N saved applications for a given career path in a formatted table with color-coded status history.

**Flags:**

| Flag | Description |
|------|-------------|
| `--career` / `-cp` | Career path label *(required)* |
| `--rows` / `-rj` | Number of recent entries to display (default: `20`) |

---

### 🩷 `daiana update` <sub>Vivid Peach Pink `#F5C8DC`</sub>

Updates the status of a saved job application. Finds the matching entry by position + company, shows current status, and lets you set a new one. If multiple entries match, you pick from a numbered list.

**Flags:**

| Flag | Description |
|------|-------------|
| `--career` / `-cp` | Career path label *(required)* |

Allowed statuses are defined in `daiana/utils/constants.py`.

---

### 🔴 `daiana hunt` <sub>Electric Crimson `#F03C5A`</sub>

The full end-to-end hunt: calls `oracle` to get AI-powered recommendations, displays them, and — if you confirm — compiles the documents and saves the application to the tracker in one shot.

**Flags:**

| Flag | Description |
|------|-------------|
| `--career` / `-cp` | Career path label *(required)* |

---

### 🟡 `daiana oracle` <sub>Radiant Oracle Gold `#E6BE3C`</sub>

Feeds a job description URL to an LLM and returns tailored recommendations: suggested skills, projects from your CV, and a first-paragraph draft for your cover letter. Outputs a structured dict you can pipe into `compile`.

**Flags:**

| Flag | Description |
|------|-------------|
| `--url` / `-u` | URL of the job posting *(required)* |
| `--career` / `-cp` | Career path label *(required)* |

---

## Status Color Legend

When `daiana show` renders your application history, each status is color-coded:

| Status | Color | Meaning |
|--------|-------|---------|
| `applied` | Off-white `#F0F0F0` | Sent the application |
| `contacted` | Pale cream yellow `#FAF0B4` | Recruiter reached out |
| `int_1` | Warm green `#96C896` | First interview scheduled |
| `int_2` | Vibrant turquoise `#46D2BE` | Second interview scheduled |
| `offered` | Vivid success green `#00C878` | Offer received 🎉 |
| `rejected` | Electric crimson `#F03C5A` | Rejected |

---

## Project Structure

```
daiana/
├── cli.py              # Entry point, registers all commands
├── commands/           # Click command wrappers (one per command)
│   ├── compiler_cli.py
│   ├── hunter_cli.py
│   ├── oracler_cli.py
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
    ├── styles.py       # Terminal styling helpers
    └── constants.py    # Allowed statuses, color map
```

---

## Notes

- CSV files are stored per career path (e.g., `software_jobs.csv`) in your working directory.
- Status history is stored as JSON inside the CSV, rendered with colors in the terminal.
- Requires an OpenAI API key in `.env` for `oracle` and `hunt` commands.

---

## 🔭 What's Coming

- **Color prompt output polish** — fixing rich-click integration so interactive prompts inherit command colors consistently.
- **Color legend in the terminal** — `daiana show` will display an inline legend of status colors without needing the README.
- **Better in-terminal `--help`** — each command will have richer, self-documenting help strings so first-time users need zero external docs.
- **Smarter oracle prompt** — engineering a prompt that always returns a well-structured `company_challenge` JSON, with the option to manually edit it before confirming and sending to compile.
- **`daiana hunt` full loop** — once oracle is rock-solid, `hunt` will complete the full cycle: scrape → recommend → edit → compile → save, all in a single command.
