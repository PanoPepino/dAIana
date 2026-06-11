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


Career heading sentence
-----------------------

- **Location**: ``job_hunt/prompts/career/career_headings.md``

Maps each career slug to the heading sentence that appears in the CV header
(the ``cv_heading_sentence`` LaTeX slot). The LLM reads this mapping after
extracting the job's career path via ``--extract`` and injects the matching
sentence verbatim into the compiled document.

Format: JSON object where every key is a career slug and every value is a
plain-text heading sentence.

.. code-block:: json

    {
      "software": "Senior Software Engineer — Backend, Distributed Systems & Cloud Infrastructure",
      "data": "Data Engineer — Pipelines, Analytics & ML Infrastructure",
      "product": "Product Manager — Growth, Strategy & Cross-functional Leadership"
    }

Keep the value concise (one line). It is inserted directly into your LaTeX
CV header, so avoid special LaTeX characters (``&``, ``%``, ``$``, etc.) —
dAIana escapes them automatically.


Skills inventory (AI payload)
------------------------------

- **Location**: ``job_hunt/prompts/skills/skills_payload.md``

This file defines the technical "DNA" the LLM scans when selecting skills
for your CV. It is structured into categories that map directly to the
``\cvitem`` structure in your LaTeX templates.

Format: free-form markdown where each category is a label followed by a
comma-separated list of tools and technologies.

.. code-block:: text

    Backend & Architecture: Python (FastAPI, Django, Flask),
    Distributed Systems (gRPC, RabbitMQ, Kafka), Cloud Native (AWS Lambda, Docker, Kubernetes),
    Microservices design, System Scalability, Event-driven architecture.

    Data Engineering & ML: SQL (PostgreSQL, Redshift),
    NoSQL (Redis, MongoDB), Big Data (Apache Spark, Airflow), ETL pipeline design,
    MLOps (MLflow, Kubeflow), Model deployment, Feature stores.

    DevOps & Infrastructure: Infrastructure as Code (Terraform, Pulumi),
    CI/CD (GitHub Actions, GitLab CI), Monitoring & Observability
    (Prometheus, Grafana, ELK Stack),
    Linux Kernel tuning, Network security, Git workflow optimization.

    Languages & Tools: Python, Rust, Go, TypeScript, C++,
    Bash, SQL, LaTeX, VS Code, IntelliJ, Jira, Agile/Scrum.

How it works during Oracle:

The LLM parses this payload and compares your items' keywords against the
job description text. It ranks categories based on the total relevance weight
of the matches found. Up to 4 categories are returned, each with a tailored
item list. The final selection is injected as a pre-formatted LaTeX block
(``selected_skills_latex``).

.. tip::

   Keep category labels consistent with your template's ``\cvitem`` headers.
   If you change a label here, ensure the LaTeX template is updated to match,
   otherwise compilation will succeed but the formatting may misalign.


Core strengths inventory (AI payload)
--------------------------------------

- **Location**: ``job_hunt/prompts/core_strengths/core_strengths_payload.md``

Defines the soft-skill and cross-functional strengths the LLM selects from
when ``--select_core_strengths`` is used. The LLM picks and ranks the **5
most relevant** entries for the target job posting.

Format: a plain bullet list of strength labels, one per line.

.. code-block:: text

    - Complex problem solving
    - Analytical reasoning
    - Systems thinking
    - Attention to detail
    - Technical communication
    - Cross-functional collaboration
    - Mentorship & knowledge sharing
    - Ownership & accountability
    - Adaptability under ambiguity
    - Stakeholder management

How it works during Oracle:

The LLM reads the full list and selects the 5 entries whose labels best
match the language and priorities of the job posting. The ordered selection
is stored in slots ``_core_strength_1`` through ``_core_strength_5`` and
injected into your CV template as a ``\cvitem`` block automatically.

.. tip::

   Use concise, recognisable labels (2–4 words). Verbose phrases reduce
   matching accuracy. Aim for 10–15 entries in the inventory so the LLM
   always has meaningful alternatives to rank from.


Summary templates
-----------------

- **Location**: ``job_hunt/prompts/summary/summary_<career>.md``

One Markdown file per career slug (e.g. ``summary_software.md``,
``summary_data.md``). Each file contains the base summary paragraph that
appears at the top of your CV, with two placeholders the LLM fills in:

- ``[Company name]`` — replaced with the target company's name.
- ``[Company challenge]`` — replaced with the main challenge or goal
  mentioned in the job posting.

.. code-block:: text

    Senior software engineer with 8+ years building distributed backend systems
    at scale. At [Company name], I am excited to apply that experience to
    [Company challenge], combining technical depth with a track record of
    shipping reliable, high-performance services.

How it works during Oracle:

1. ``--extract`` is required in the same invocation so that the career slug
   is known before the summary template is loaded.
2. dAIana loads ``summary/summary_<career>.md`` and passes it to the LLM
   together with the scraped job text.
3. The LLM fills ``[Company name]`` and ``[Company challenge]`` from the
   job description and returns a finalised summary string.
4. The result is stored in ``selected_summary_latex`` and injected into your
   CV template automatically.

.. note::

   ``--select_summary`` **requires** ``--extract`` in the same call::

       daiana oracle --url "..." --extract --select_summary

   Running ``--select_summary`` alone will raise an error because the career
   path cannot be determined without extraction.


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
