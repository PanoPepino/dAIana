

JOB_PROMPT = (
    "You are a JSON extractor for LaTeX cover letters. "
    "You must return EXACTLY the following JSON fields, nothing else. "
    "Do not output any Markdown, text outside JSON, or comments.\n\n"
    "Job position MUST be in English, even if the input text is in Swedish or another language.\n\n"
    "For the \"location\" field, return ONLY the main city where the job is located, in English where possible, "
    "using UTF-8 characters directly (like 'ä', 'ö', 'å', 'ó', etc.). "
    "Do not include neighborhoods, postal codes, or extra text. "
    "For example, if the job is in 'Östermalm, Södertälje', only return 'Södertälje'.\n\n"
    "Use UTF-8 characters directly in the JSON string fields. Do not use Unicode escapes like \\u00e4 or \\u00e5; "
    "use the real characters in UTF-8.\n\n"
    # ... keep your career rules here ...
    "CAREER CLASSIFICATION RULES:\n"
    "Classify the role into EXACTLY one of these three categories:\n\n"
    "- \"career\": \"data\"   → Data Science, Data Analyst, ML Engineer, Data Engineer, BI, Business Intelligence, "
    "Data Scientist, AI Engineer, Analytics Engineer, or similar roles focused on data, ML, statistics, or analytics.\n\n"
    "- \"career\": \"rd\"    → Software Developer, Software Engineer, R&D Engineer, Research Scientist (non‑quant), "
    "Backend/Full‑Stack/DevOps, SRE, or other general software development, systems, or research‑engineering roles "
    "with no strong data‑science or ML focus.\n\n"
    "- \"career\": \"quant\" → Quantitative Analyst, Quantitative Developer, Quantitative Trader, Quantitative Researcher, "
    "Risk Modeler (if math/finance heavy), or other roles that are heavily math‑ or finance‑oriented with model‑building.\n\n"
    "Rules:\n"
    "1) If the job is clearly about software development, tools, or systems without strong data/ML focus → \"rd\".\n"
    "2) If the job is clearly about data analysis, machine learning, statistics, or data pipelines → \"data\".\n"
    "3) If the job is explicitly \"quant\" or heavily math/finance‑driven → \"quant\".\n"
    "4) If ambiguous, prefer \"data\" only when there is clear evidence of ML, statistics, or analytics work.\n"
    "5) Never output any other value for \"career\" besides \"data\", \"rd\", or \"quant\"."
)


SENTENCE_PROMPT = """\
You are a precise cover letter assistant for a professional role in data science, R&D, engineering, finance, or a related discipline.  

Write ONE sentence for a cover letter that starts exactly with:

  "can contribute the most to {{company_name}}'s challenges in ..."

STRICT RULES:
1. Only use facts explicitly stated or strongly implied in the job advertisement text.
2. NEVER invent metrics, project names, technologies, or specific products not in the ad.
3. Identify ONE central challenge or strategic priority for the company in this role, such as:
   - building data‑driven models or analytics
   - developing and improving products, systems, or processes
   - managing risk or financial performance
   - improving operational efficiency or customer experience
4. The "..." must clearly express that challenge using concrete, non‑generic language.
5. Avoid vague fillers: do NOT use "innovative solutions", "dynamic environment", "cutting‑edge", or "fast‑paced".
6. The sentence (which is for the ending of a first paragraph in a text) must be a single, grammatically correct English sentence.
7. The sentence must be focused on specific technical issues that the company challenge or strategy may be facing.
8. While the sentence construction is "can contribute the most to {{company_name}}'s challenges in...", the relevant output must just be "in ...", where ellipse is the crafted sentence.
8. Output ONLY valid JSON using the exact schema shown below — no markdown, no extra keys, no comments.
"""

SENTENCE_SCHEMA = {
    "company_name": "the company name from the ad",
    "career": "one of: 'data', 'rd', 'finance', or 'other'",
    "challenge_area": "a short phrase describing the main challenge for the company in this role",
    "business_domain": "the domain where the challenge appears (e.g. 'production', 'logistics', 'risk management', 'product development')",
    "sentence_first_paragraph": "in ..."
}
