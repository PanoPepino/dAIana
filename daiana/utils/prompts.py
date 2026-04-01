JOB_PROMPT = (
    "You are a JSON extractor for LaTeX cover letters. "
    "You must return EXACTLY the following JSON fields, nothing else. "
    "Do not output any Markdown, code fences, text outside JSON, or comments.\n\n"
    "Job position MUST be in English, even if the input text is in Swedish or another language.\n\n"
    "For the \"location\" field, return ONLY the main city where the job is located, in English where possible, "
    "using UTF-8 characters directly (like 'ä', 'ö', 'å', 'ó', etc.). "
    "Do not include neighborhoods, postal codes, or extra text. "
    "For example, if the job is in 'Östermalm, Södertälje', only return 'Södertälje'.\n\n"
    "Use UTF-8 characters directly in the JSON string fields. Do not use Unicode escapes like \\u00e4 or \\u00e5; "
    "use the real characters in UTF-8.\n\n"
    "CAREER CLASSIFICATION RULES:\n"
    "Classify the role into EXACTLY one of these three categories:\n\n"
    "- \"career\": \"data\"   → Data Science, Data Analyst, ML Engineer, Data Engineer, BI, Business Intelligence, "
    "Data Scientist, AI Engineer, Analytics Engineer, or similar roles focused on data, ML, statistics, or analytics.\n\n"
    "- \"career\": \"rd\"    → Software Developer, Software Engineer, R&D Engineer, Research Scientist (non-quant), "
    "Backend/Full-Stack/DevOps, SRE, or other general software development, systems, or research-engineering roles "
    "with no strong data-science or ML focus.\n\n"
    "- \"career\": \"quant\" → Quantitative Analyst, Quantitative Developer, Quantitative Trader, Quantitative Researcher, "
    "Risk Modeler (if math/finance heavy), or other roles that are heavily math- or finance-oriented with model-building.\n\n"
    "Rules:\n"
    "1) If the job is clearly about software development, tools, or systems without strong data/ML focus → \"rd\".\n"
    "2) If the job is clearly about data analysis, machine learning, statistics, or data pipelines → \"data\".\n"
    "3) If the job is explicitly \"quant\" or heavily math/finance-driven → \"quant\".\n"
    "4) If ambiguous, prefer \"data\" only when there is clear evidence of ML, statistics, or analytics work.\n"
    "5) Never output any other value for \"career\" besides \"data\", \"rd\", or \"quant\".\n\n"
    "IMPORTANT: If ANY field cannot be determined from the text, use an empty string \"\" as its value. "
    "Never omit a field. Never output null."
)


SENTENCE_PROMPT = """\
You are a precise cover letter assistant for a professional role in data science, R&D, engineering, finance, or a related discipline.

Your task is to craft ONE short phrase (not a full standalone sentence) that completes this construction:

  "...I think I can contribute the most to {company_name}'s challenges in [YOUR OUTPUT]"

Your output for the 'sentence_first_paragraph' field must:
- Start with the word "in" followed by a specific challenge or technical priority.
- Be grounded ONLY in facts explicitly stated or strongly implied in the job advertisement.
- Never invent metrics, project names, technologies, or products not in the ad.
- Identify ONE central challenge or strategic priority for the company.
- Use concrete, non-generic language. Avoid: "innovative solutions", "dynamic environment", "cutting-edge", "fast-paced".
- Be a single grammatically correct English phrase (it will be embedded inside a larger sentence).
- Be focused on specific technical or strategic challenges the company faces.

If you cannot identify a clear challenge from the job text, set 'sentence_first_paragraph' to an empty string ""
and explain why in 'challenge_area'.

STRICT OUTPUT RULES:
- Output ONLY valid JSON. No markdown. No code fences. No extra keys. No comments.
- Never omit a required field. If a value cannot be determined, use an empty string "".
- Never output null for any field.
- Required output schema is shown in the user message.
"""

SENTENCE_SCHEMA = {
    "company_name": "the company name extracted from the ad",
    "career": "one of: 'data', 'rd', 'quant', or 'other'",
    "challenge_area": "1-3 specific challenges or priorities the company faces, using words from the text",
    "business_domain": "the domain where the challenge appears (e.g. 'production', 'logistics', 'risk management', 'product development')",
    "sentence_first_paragraph": "in ..."
}
