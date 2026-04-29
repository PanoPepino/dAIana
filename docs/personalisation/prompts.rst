Prompt personalisation
======================

Career tracks
-------------

- **Location**: ``job_hunt/prompts/career/careers.md``

Defines every career label the LLM may assign to a job posting, and that
you pass with ``--career`` / ``-cp`` to ``daiana save``, ``daiana show``,
and ``daiana update``.

.. code-block:: json

    {
      "options": ["data", "backend", "product"]
    }

Each label maps to its own CSV tracker file (e.g. ``job_tracking_data.csv``)
and to a ``\body<label>`` command in ``variants_cl.tex``.

.. note::
   Adding a label here without adding ``\body<label>`` in ``variants_cl.tex``
   will cause a LaTeX compile error on cover letter jobs with that career.

Projects (AI payload)
---------------------

- **Location**: ``job_hunt/prompts/projects/projects_payload.md``

What the LLM reads when selecting which projects to highlight.
Format: ``name | keywords | description``.

.. code-block:: text

    - cloudscale | microservices, backend, distributed systems, AWS, Docker
      Distributed microservices platform handling 1M+ daily requests.

    - codeinsight | AI tooling, code review, developer experience, GitHub
      AI-powered code review assistant that reduced review time by 40%.

    - datastream | Kafka, Spark, real-time analytics, stream processing
      Real-time analytics pipeline ingesting 500K+ events per minute.

    - devtrack | dashboards, developer productivity, analytics
      Internal productivity dashboard used by 200+ developers.

Use keywords that match the vocabulary in your target job postings.

Project name → LaTeX mapping
-----------------------------

- **Location**: ``job_hunt/prompts/projects/projects_name_to_latex.md``

Maps the plain-text names (used by the LLM) to their LaTeX command names
(used in the templates). Every key must exist in ``projects_payload.md``
and every value must exist in both ``variants_cv.tex`` and
``variants_cl.tex``.

.. code-block:: json

    {
      "cloudscale":  "\\cloudscale",
      "codeinsight": "\\codeinsight",
      "datastream":  "\\datastream",
      "devtrack":    "\\devtrack"
    }

Background skills
-----------------

- **Location**: ``job_hunt/prompts/background/background_payload.md``

The LLM picks three skills from this list to populate the
``your_background`` field in the cover letter. Use plain, lowercase phrases.

.. code-block:: text

    Available backgrounds:
    - distributed systems
    - backend development
    - API design
    - cloud infrastructure
    - microservices architecture
    - data engineering
    - system design
    - DevOps practices
    - performance optimization
    - database systems
    - software architecture
    - full-stack development

Sentence style rules
--------------------

- **Location**: ``job_hunt/prompts/sentence/sentence_prompt.md``

Controls how the LLM writes the tailored opening sentence of your cover
letter (``--cl`` / ``--tailor_sentence``). Adjust:

- **Tone rules** — formal vs. conversational, sentence length, forbidden
  clichés (``innovative solutions``, ``passionate about``, etc.)
- **Structure rules** — what the sentence must reference: company challenge,
  role scope, your motivation.

Do not rename the output schema fields — only edit the instruction text
around them.