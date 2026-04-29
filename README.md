<div align="center">

# 🏹 dAIana 🏹
*- Let the AI Goddess guide your steps when hunting down your next job position -*

</div>

---




**dAIana** is a terminal-based Python CLI that calls **AI APIs** to tailor LaTeX CVs and cover letters from job posting URLs. It **automates** scraping, extraction, personalization, and PDF compilation in one workflow.


## **⚠️ Before you start**
>
> dAIana does **NOT** write your CV or cover letter from scratch.
> You need to **WRITE** your own LaTeX modular files first!!
>
> See TEMPLATES in (`job_hunt/cv_and_letter/*.tex`)
>
> The idea: you build your CV and cover letter as a set of **MODULAR sections** (e.g. different project blocks, different skill summaries). dAIana then reads the job posting and picks **which sections fit best** for that specific role.



## **Quickstart**

```bash
pip install daiana
daiana init --copy_dir                # Copy job_hunt dir. (cv & cover letter + prompts template) wherever you want
cd "to/desired/location"
daiana init --set_env                 # Set your LLM API provider and prompts directory
daiana check --env --prompts          # Verify setup of env and prompts before hunting
daiana hunt --url "https://jobs.example.com/role" --cv --cl
```



## **Most Relevant Commands**

### 🥝 `daiana init`

First-time setup. Configure your LLM provider and copy your `job_hunt` folder.

| Flag | Description |
|------|-------------|
| `--copy_directory` | Copy the local `job_hunt/` folder to a new path |
| `--set_env` | Set provider, model, base URL, API key name and value — saved to `.env` |


```bash
daiana init --set_env
daiana init --copy_directory
```



### 🩶 `daiana check`

Inspect your setup before running a hunt. Diagnose environment and prompt files.

| Flag | Description |
|------|-------------|
| `--env` | Display loaded env vars and verify the LLM client can be built |
| `--prompts` | Load and inspect all prompt assets used by the oracle |

```bash
daiana check --env --prompts
```


### 🔴 `daiana hunt`

Full end-to-end pipeline: scrape → extract → tailor → compile → open .pdfsd → save.

At least one of `--cv` or `--cl` must be passed.

| Flag | Description |
|------|-------------|
| `--url` / `-u` | URL of the job posting *(required)* |
| `--cv` | Extract job info and compile your CV |
| `--cl` | Craft a tailored cover letter sentence and compile your cover letter |
| `--username` / `-un` | Your name for the output PDF filename (default: `user_name`) |

```bash
daiana hunt --url "https://jobs.example.com/role" --cv --cl --username jane
```

**Workflow:**

1. Scrapes the job posting at `--url`
2. Calls the LLM to extract job info and/or craft a cover letter phrase
3. Displays the result — asks if you want to edit any field
4. Compiles the requested document(s) to PDF
5. Asks if you want to open the generated PDF(s)
6. Asks if you want to save the job to your CSV tracker



### 🟫 `daiana show`

Display your last N saved applications for a given career path — color-coded by status with a legend.

| Flag | Description |
|------|-------------|
| `--career` / `-cp` | Career path label *(required)* |
| `--rows` / `-rj` | Number of recent entries to display (default: `20`, min: `1`) |

```bash
daiana show -cp software
daiana show -cp data -rj 10
```

Outputs a formatted table followed by a status legend and a total application count for that given career path.

### 🩷 `daiana update`

Update the status or any field of a saved job application. Finds the entry by position + company.

| Flag | Description |
|------|-------------|
| `--career` / `-cp` | Career path label *(required)* |
| `--status` / `-s` | Set a new application status |
| `--field` / `-f` | Edit any other field of the saved entry |
| `--erase` / `-e` | Erase any row |



```bash
daiana update --career software --status
daiana update -cp data -e
```
