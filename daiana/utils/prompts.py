# ── Shared rules injected into every prompt ───────────────────────────────────
_LANG_RULE = (
    "Input may be in any language. ALL output fields MUST be in English. "
    "Translate if needed. Never output non-English text in any field.\n"
)

_JSON_RULE = (
    "Output ONLY valid JSON. No markdown, no code fences, no comments, no extra keys. "
    "Missing values → empty string \"\". Never output null. Never omit a field.\n"
)

# ── Job metadata extraction ────────────────────────────────────────
JOB_PROMPT = (
    _LANG_RULE
    + _JSON_RULE
    + "\n"
    "You are a JSON extractor for LaTeX cover letters.\n\n"
    "FIELD RULES:\n"
    "- job_position: in English.\n"
    "- location: city only, UTF-8 chars (ä/ö/å/ó allowed), no postal codes or neighborhoods.\n"
    "- career: EXACTLY one of 'data' | 'rd' | 'quant'.\n\n"
    "CAREER CLASSIFICATION:\n"
    "  'data'  → Data Science, ML, Analytics, BI, Data Engineering.\n"
    "  'rd'    → Software Dev, R&D, Backend, DevOps, SRE, Systems (no ML focus).\n"
    "  'quant' → Quant Analyst/Dev/Trader/Researcher, math/finance-heavy modelling.\n"
    "  If ambiguous, prefer 'data' only with clear ML/statistics evidence; else 'rd'.\n"
)

# ── Challenge sentence ──────────────────────────────────────────────

_COVER_RULE = (
    "Cover letters convert when they mirror job ad vocabulary exactly. "
    "Use ad's own phrasing verbatim where possible. Never embellish.\n"
)

_RESEARCH_RULE = (
    "1. Company mission sets CONTEXT (scale/impact from About page)\n"
    "2. Job responsibilities define DOMAIN (core technical deliverables)\n"
    "3. Requirements specify TENSION (problems they need solved)\n"
    "Use job ad first, supplement with company context only if ad lacks specifics.\n"
)

_STRUCTURE_RULE = (
    "MANDATORY 3-part structure (20-25 words total):\n"
    "• DOMAIN: 3-6 words. Core deliverable from job bullet #1 "
    "(e.g. 'credit risk modeling methodologies', 'data pipeline engineering frameworks')\n"
    "• TENSION: 4-8 words. Key problem/metric from requirements "
    "(e.g. 'stress testing regulatory compliance requirements', 'real-time anomaly detection capabilities')\n"
    "• CONTEXT: 5- words. Scale/stakeholders from company mission "
    "(e.g. 'across Nordic SME lending portfolios', 'for healthcare IT operations globally')\n\n"
    "Formula: '[DOMAIN] and [TENSION] [CONTEXT]'\n"
    "Examples:\n"
    "✅ 'credit risk modeling methodologies and stress testing regulatory compliance requirements across Nordic SME lending portfolios' (17 words)\n"
    "✅ 'data pipeline engineering frameworks and real-time ML inference capabilities for healthcare IT operations globally' (15 words)\n"
    "❌ 'innovative AI solutions that transform healthcare' (forbidden words + too short)\n"
)
SENTENCE_PROMPT = (
    _LANG_RULE
    + _JSON_RULE
    + _COVER_RULE
    + _RESEARCH_RULE
    + _STRUCTURE_RULE
    + "\n\n"
    "You are an elite cover letter strategist. Complete ONLY this fragment:\n\n"
    "  '... position at [COMPANY], motivated by ___'\n\n"
    "Output ONLY the blank as a precise 15-20 word noun phrase.\n\n"
    "Required JSON format:\n"
    """{
      "motivation_phrase": "[DOMAIN] and [TENSION] [CONTEXT]",
      "domain": "[core technical field]",
      "tension": "[specific problem/goal]", 
      "context": "[scale/environment]",
      "challenge_area": "[why this phrasing fits | empty if perfect match]",
      "word_count": 0,
      "job_title_used": "[exact title from ad]"
    }"""
)


# ── Project selector ─────────────────────────────────────────────────
PROJECT_PROMPT = (
    _JSON_RULE
    + "\n"
    "You are a CV relevance engine. Select the 3 projects that best match the job ad.\n"
    "Rank in decreasing relevance using: technical overlap → domain proximity → complexity.\n"
    "Project cosmo can NEVER be ranked first or second. It must always appear as rank three if listed."  # To be modified
    "REQUIRED OUTPUT FIELDS:\n"
    "- selected_1: most relevant project name\n"
    "- selected_2: 2nd most relevant project name\n"
    "- selected_3: 3rd most relevant project name\n"
    "- reason_name_1: 1-sentence reason why selected_1 matches the job\n"
    "- reason_name_2: 1-sentence reason why selected_2 matches the job\n"
    "- reason_name_3: 1-sentence reason why selected_3 matches the job\n"
    "Keep reasons ≤10 words. Never omit any field.\n"
)


# ── Background selector ─────────────────────────────────────────────────
BACKGROUND_PROMPT = (
    _JSON_RULE
    + "\n"
    "You are a CV background relevance engine. Select the 3 backgrounds that best match the job ad.\n"
    "Rank in decreasing relevance using: technical overlap → domain proximity → specificity.\n"
    "REQUIRED OUTPUT FIELDS:\n"
    "- background_1: most relevant background name\n"
    "- background_2: 2nd most relevant background name\n"
    "- background_3: 3rd most relevant background name\n"
    "Use only exact background names from the provided list. Never omit any field. Never invent backgrounds.\n"
)

# ── Schema ──────────────────────────────────────────────────────────────────
SENTENCE_SCHEMA = {
    "company_name":             "company name from the ad",
    "career":                   "one of: data | rd | quant | other",  # To be modified
    "challenge_area":           "1-3 specific challenges the company faces, verbatim from the ad",
    "business_domain":          "domain of the challenge (e.g. logistics, risk management, product dev)",
    "sentence_first_paragraph": "10-15 word phrase: the company's central challenge from the ad",
}

PROJECT_SELECTION_SCHEMA = {
    "selected_1": "name1",
    "selected_2": "name2",
    "selected_3": "name3",
    "reason_name_1": "≤10-word match reason for selected_1",
    "reason_name_2": "≤10-word match reason for selected_2",
    "reason_name_3": "≤10-word match reason for selected_3",
}

BACKGROUND_SELECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "background_one": {"type": "string"},
        "background_two": {"type": "string"},
        "background_three": {"type": "string"},
    },
    "required": ["background_one", "background_two", "background_three"],
}


# ── Oracle: project payload for LLM selection ─────────────────────────────────
# Plain-text mirror of loader/projects.tex — readable by the model.
# Keys must match the \newcommand names in projects.tex exactly.

PROJECTS_PAYLOAD = """\
PROJECTS (name | keywords | description):

- beanim | Python, open-source, modular framework, data viz, scientific communication, animations
  Open-source Python framework for interactive mathematical animations; deployed at 25+ international conferences.
  Modular, reusable design for complex visual explanations without slideware lock-in.

- pokeml | ML pipeline, EDA, feature engineering, multi-model training, cloud deployment, Hugging Face, data science
  End-to-end ML pipeline on 1K+ mixed categorical/numerical dataset with 10+ feature engineering steps.
  Cloud deployment via Hugging Face; full production-ready packaging.

- daiana | LLM API, CLI, web scraping, automation, NLP, Python, workflow automation, document generation
  Terminal CLI with LLM API pipeline to scrape job postings and compile tailored LaTeX documents end-to-end.
  Reduced application time by 70% via full automation and integrated per-career CSV tracker.

- cosmo | parameter estimation, predictive modelling, scientific computing, algorithm design, numerical methods, physics
  Built a parameter estimation framework linking theoretical models to observational data.
  Algorithm adopted by 10+ researchers; directly drove 5 peer-reviewed articles.
"""

# Maps LLM-returned project names → LaTeX \newcommand keys in loader/projects.tex
PROJECT_NAME_TO_LATEX = {
    "beanim": "\\beanim",
    "pokeml": "\\pokeml",
    "daiana": "\\daiana",
    "cosmo":  "\\cosmo",
}
# ── Oracle: Skill selection ─────────────────────────────────

BACKGROUND = [
    "mathematical modeling",
    "high-dimensional analysis",
    "parameter estimation",
    "algorithm development",
    "machine learning",
    "predictive modeling",
    "optimization",
    "data visualization",
    "numerical analysis",
    "non-linear systems analysis",
    "stochastic processes",
    "differential equations",
    "time series analysis",
    "scientific computing",
    "uncertainty quantification",
    "complex systems modeling",
    "simulation-based validation",
    "statistical inference",
    "library development"
]

# ── Payload sent to the model ─────────────────────────────────────────────────

BACKGROUND_PAYLOAD = "Available backgrounds:\n" + "\n".join(
    f"- {item}" for item in BACKGROUND
)
