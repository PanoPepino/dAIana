# dAIana 🏹

> Terminal CLI package for LaTeX CV & cover letter automation with AI tailored recommendations, with built-in job application tracking.

No GUI. No fuss. Fill in a few prompts, get a compiled PDF, and track where you applied — all from your terminal.

Built for people who apply to multiple roles across different career tracks and are tired of copy-pasting job details, tweaking cover letters by hand, and losing track of where they applied.



## Commands

### 🔴 `daiana hunt`

The full end-to-end pipeline: scrapes the job URL via `oracle`, displays extracted information, optionally compiles your CV and/or cover letter, opens the generated PDFs, and saves the application to the CSV tracker — all in one command.

At least one of `--cv` or `--cl` must be passed.

**Flags:**

| Flag | Description |
|------|-------------|
| `--url` / `-u` | URL of the job posting *(required)* |
| `--cv` | Extract job info and compile your CV |
| `--cl` | Craft a tailored cover letter sentence and compile your cover letter |
| `--username` / `-un` | Your name for the output PDF filename (default: `user_name`) |
| `--verbose` | Show LaTeX compilation details |
| `--csv-path` | Path prefix for the CSV tracker file (default: `job_tracking`) |

**Workflow:**

1. Scrapes the job posting at `--url`.
2. Calls the LLM to extract job info (`--cv`) and/or craft a cover letter phrase (`--cl`).
3. Displays the result and asks if you want to edit any field.
4. Compiles the requested document(s) to PDF.
5. Asks if you want to open the generated PDF(s) with your default viewer.
6. Asks if you want to save the job to your CSV tracker.
7. Reports total elapsed time.

**Example:**

```bash
daiana hunt -u "https://jobs.example.com/ml-engineer" --cv --cl --username jane
```
---

### 🟡 `daiana oracle`

Scrapes a job posting URL and sends the text to an LLM (Perplexity `sonar` / `sonar-pro`) to extract structured job information and, optionally, a tailored cover letter phrase.

At least one of `--extract` or `--tailor_sentence` must be passed. You can use both together.

**Flags:**

| Flag | Description |
|------|-------------|
| `--url` / `-u` | URL of the job posting *(required)* |
| `--extract` | Extract structured job info: position, company, location, career, and link |
| `--tailor_sentence` | Craft a tailored phrase for the first paragraph of your cover letter |
| `--project_selector`| Based on your projects, it will select the best ones |
| `--background_selector`| Based on your background, it will select the 3 optimal skills to write down in the cover letter |




---


### 🔵 `daiana compile` 

Renders a LaTeX template and compiles it to PDF. Prompts you interactively for job details (position, company, location, career path, link). After compiling, optionally saves the job to a CSV tracker.

**Flags:**

| Flag | Description |
|------|-------------|
| `--cv` | Use the CV template (`template_cv.tex`) |
| `--cl` | Use the cover letter template (`template_cl.tex`) |
| `--username` / `-un` | Your name, used in the output PDF filename (default: `user_name`) |
| `--verbose` | Print LaTeX compilation log details to the terminal |

---

### 🟢 `daiana save` 

Manually saves a job application to a per-career CSV file, without compiling a document. Useful when you apply externally and just want to log it.

**Flags:**

| Flag | Description |
|------|-------------|
| `--career` / `-cp` | Career path label, e.g. `"software"` *(required)* |

Prompts: job position, company name, location, and an optional link.

---

### 🟫 `daiana show` 

Displays the last N saved applications for a given career path in a formatted table with color-coded status history.

**Flags:**

| Flag | Description |
|------|-------------|
| `--career` / `-cp` | Career path label *(required)* |
| `--rows` / `-rj` | Number of recent entries to display (default: `20`) |

---

### 🩷 `daiana update` 

Updates the status of a saved job application. Finds the matching entry by position + company, shows current status, and lets you set a new one. If multiple entries match, you pick from a numbered list.

**Flags:**

| Flag | Description |
|------|-------------|
| `--career` / `-cp` | Career path label *(required)* |
| `--status` / `-s` | Update the application status (choose from allowed values) |
| `--field` / `-f` | Edit any other field of the saved entry |

Allowed statuses are defined in `daiana/utils/constants.py`.

---





## Project Structure

```
daiana/
├── cli.py              # Entry point, registers all commands
├── commands/           # Click command wrappers (one per command)
│   ├── compiler_comm.py
│   ├── hunter_comm.py
│   ├── oracler_comm.py
│   ├── saver_comm.py
│   ├── shower_comm.py
│   └── updater_comm.py
├── core/               # Business logic (no Click dependencies)
│   ├── compiler.py     # pdflatex runner and template rendering
│   ├── hunter.py       # Full Logic: scrape → extract → tailor → modify → compile → show → save
│   ├── oracler.py      # LLM pipeline: scrape → extract → tailor
│   ├── saver.py        # CSV write logic
│   ├── shower.py       # CSV read logic
│   └── updater.py      # CSV update logic
└── utils/
    ├── prompts.py      # LLM system prompts and output schemas
    ├── for_latex.py    # Template rendering (replace_newcommand)
    ├── for_oracle.py   # Web scraping and oracle dict helpers
    ├── for_hunt.py     # validations and other things
    ├── for_update.py   # helpers for easy updating
    ├── colors.py       # Colors of status, commands, and general UI
    ├── ui.py           # Class of UI to decorate all information in the terminal
    ├── styles.py       # Terminal styling helpers
    └── constants.py    # Allowed statuses, mode config
```
