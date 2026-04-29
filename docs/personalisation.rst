Personalisation
===============

dAIana needs to know about you before it can do anything useful.
All personalisation lives inside ``job_hunt/`` — no Python files to touch.

There are three areas to configure:

- :doc:`env` — API keys, LLM model, and your name
- :doc:`latex` — Your projects and cover letter paragraphs
- :doc:`prompts` — What the AI knows about your skills and career tracks

Run ``daiana init`` to create the folder structure, then ``daiana check``
to verify everything is in place before your first hunt.

Quick reference
---------------

.. list-table::
   :header-rows: 1
   :widths: 40 35 25

   * - What to personalise
     - File
     - Required?
   * - API keys, provider, model, user name
     - ``job_hunt/.env``
     - ✅ Yes
   * - Career track labels
     - ``prompts/career/careers.md``
     - ✅ Yes
   * - Project descriptions (AI payload)
     - ``prompts/projects/projects_payload.md``
     - ✅ Yes
   * - Project name → LaTeX mapping
     - ``prompts/projects/projects_name_to_latex.md``
     - ✅ Yes
   * - Project LaTeX commands (CV)
     - ``cv_and_letter/loader/variants_cv.tex``
     - ✅ Yes
   * - Project LaTeX commands (CL inline)
     - ``cv_and_letter/loader/variants_cl.tex``
     - ✅ Yes
   * - Background skills list
     - ``prompts/background/background_payload.md``
     - ✅ Yes
   * - Cover letter body paragraphs
     - ``cv_and_letter/loader/variants_cl.tex``
     - ✅ Yes
   * - Sentence tone & style rules
     - ``prompts/sentence/sentence_prompt.md``
     - Optional


.. toctree::
   :maxdepth: 2

   personalisation/env
   personalisation/latex
   personalisation/prompts