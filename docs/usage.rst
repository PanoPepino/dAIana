Usage
=====

All commands must be run from inside your ``job_hunt/`` folder (the one
created by ``daiana init --copy_dir``). This is where the ``.env`` file
lives and where PDFs and CSVs are written.

This page covers the main user-facing commands in the order you are most
likely to use them:

1. ``hunt`` — full end-to-end workflow.
2. ``show`` — inspect saved applications.
3. ``update`` — change the status or edit a saved entry.
4. ``oracle`` — extract and tailor job data without compiling.
5. ``compile`` — build a CV or cover letter from prompts or manual input.
6. ``save`` — log an application directly to the tracker.

.. role:: hunt
.. role:: show
.. role:: update
.. role:: oracle
.. role:: compile
.. role:: save

.. raw:: html

   <style>
   .hunt { color: rgb(240, 60, 90); font-weight: 700; }
   .show { color: rgb(200, 120, 100); font-weight: 700; }
   .update { color: rgb(245, 200, 220); font-weight: 700; }
   .oracle { color: rgb(230, 190, 60); font-weight: 700; }
   .compile { color: rgb(30, 170, 240); font-weight: 700; }
   .save { color: rgb(0, 200, 120); font-weight: 700; }
   </style>

----

:hunt:`daiana hunt`
-------------------

The full end-to-end pipeline in a single command:
**scrape → extract → tailor → compile → open → save**.

At least one of ``--cv`` or ``--cl`` must be passed.

.. code-block:: bash

   daiana hunt --url "https://jobs.example.com/role" --cv --cl --username jane

**Flags**

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Flag
     - Description
   * - ``--url`` / ``-u``
     - URL of the job posting *(required)*.
   * - ``--cv``
     - Extract job info and compile your CV.
   * - ``--cl``
     - Craft a tailored cover letter sentence and compile your cover letter.
   * - ``--username`` / ``-un``
     - Your name for the output PDF filename (default: ``user_name``).
   * - ``--verbose``
     - Show full LaTeX compilation log in the terminal.

**What happens**

1. dAIana scrapes the job posting at ``--url``.
2. The LLM extracts structured job info: position, company, location, career track, and link.
3. If ``--cl`` is set, the LLM also crafts a tailored first-paragraph sentence for your cover letter.
4. The extracted data is displayed in the terminal and can be edited.
5. LaTeX compilation runs for each requested document.
6. You can open the generated PDF(s) with your default viewer.
7. You can save the application to your CSV tracker.
8. The command reports total elapsed time.

.. tip::

   Use ``--verbose`` the first time you run on a new machine to confirm
   ``pdflatex`` is finding all packages correctly.

----

:show:`daiana show`
-------------------

Display your last N saved applications for a given career path as a
colour-coded table with status history and totals.

.. code-block:: bash

   daiana show --career software
   daiana show -cp data -rj 10

**Flags**

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Flag
     - Description
   * - ``--career`` / ``-cp``
     - Career path label *(required)*.
   * - ``--rows`` / ``-rj``
     - Number of recent entries to display (default: ``20``, min: ``1``).

The table footer shows the CSV path and the total number of applications
across all statuses.

----

:update:`daiana update`
-----------------------

Update the status or any editable field of a saved job application.
The entry is located by matching **position + company name**. If multiple
entries match, you are shown a numbered list to pick from.

.. code-block:: bash

   daiana update --career software --status
   daiana update -cp data --field
   daiana update -cp data --erase

**Flags**

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Flag
     - Description
   * - ``--career`` / ``-cp``
     - Career path label *(required)*.
   * - ``--status`` / ``-s``
     - Interactively set a new application status.
   * - ``--field`` / ``-f``
     - Edit any other field of the saved entry.
   * - ``--erase`` / ``-e``
     - Delete a row from the tracker.

**Allowed statuses**

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Status
     - Meaning
   * - ``applied``
     - Application submitted, no response yet.
   * - ``contacted``
     - Recruiter or hiring manager has reached out.
   * - ``int_1``
     - First interview scheduled or completed.
   * - ``int_2``
     - Second interview scheduled or completed.
   * - ``offered``
     - Offer received.
   * - ``rejected``
     - Application rejected.

----

:oracle:`daiana oracle`
-----------------------

Scrape a job posting URL and send the text to the AI for extraction and
tailoring without compiling PDFs.

At least one of ``--extract``, ``--tailor_sentence``, ``--select_projects``,
``--select_background``, ``--select_skills``, ``--select_core_strengths``,
or ``--select_summary`` must be passed.

.. code-block:: bash

   daiana oracle --url "https://jobs.example.com/role" --extract --tailor_sentence
   daiana oracle --url "https://jobs.example.com/role" --extract --select_skills
   daiana oracle --url "https://jobs.example.com/role" --extract --select_core_strengths
   daiana oracle --url "https://jobs.example.com/role" --extract --select_summary
   daiana oracle --url "https://jobs.example.com/role" --extract --select_skills --select_projects

**Flags**

.. list-table::
   :widths: 28 72
   :header-rows: 1

   * - Flag
     - Description
   * - ``--url`` / ``-u``
     - URL of the job posting *(required)*.
   * - ``--extract``
     - Extract structured job info: position, company, location, career, and link.
   * - ``--tailor_sentence``
     - Craft a tailored phrase for the first paragraph of your cover letter.
   * - ``--select_projects``
     - Pick the 3 best matching projects from your projects inventory.
   * - ``--select_background``
     - Select the 3 most relevant background items for the cover letter.
   * - ``--select_skills``
     - Rank and select the most relevant skill categories and items from your
       skills inventory (``skills_payload.md``) for the given job posting.
       The result is displayed as a **Selected Skills** panel and passed
       automatically to ``compile --cv`` as the CV skills block.
   * - ``--select_core_strengths``
     - Rank and select the 5 most relevant core strengths from your inventory
       (``core_strengths_payload.md``) for the given job posting.
       The result is displayed as a **Selected Core Strengths** panel.
   * - ``--select_summary``
     - Select and tailor the best summary template for the target career and
       company. Requires ``--extract`` to be run in the same invocation so
       that the career path can be determined.

.. note::

   **How ``--select_skills`` works**

   1. dAIana reads your ``skills_payload.md`` inventory.
   2. The LLM ranks your skill categories and picks the most relevant items
      per category for the target job.
   3. Up to 4 skill categories are returned, each with a tailored item list.
   4. The selection is shown in a colour-coded **Selected Skills** panel.
   5. You can edit individual categories and item lists interactively before
      they are forwarded to the compiler.
   6. The final ``\\cvitem`` LaTeX block is injected into your CV template
      automatically — no manual editing required.

   To customise which skills are available for selection, edit
   ``prompts/skills/skills_payload.md`` in your ``job_hunt/`` folder.

.. note::

   **How ``--select_core_strengths`` works**

   1. dAIana reads your ``core_strengths_payload.md`` inventory.
   2. The LLM picks and ranks the 5 most relevant strengths for the target job.
   3. The selection is shown in a colour-coded **Selected Core Strengths** panel.
   4. The ordered list is injected into your CV template as a ``\\cvitem``
      block automatically.

   To customise which strengths are available for selection, edit
   ``prompts/core_strengths/core_strengths_payload.md`` in your ``job_hunt/`` folder.

.. note::

   **How ``--select_summary`` works**

   1. ``--extract`` must be included in the same call so that the career path
      is known.
   2. dAIana loads the summary template matching your career slug from
      ``prompts/summary/summary_<career>.md``.
   3. The LLM fills the ``[Company name]`` and ``[Company challenge]``
      placeholders using the scraped job text.
   4. The tailored summary is shown in a **Selected Summary** panel and
      injected directly into your CV template.

   To customise the base summary, edit
   ``prompts/summary/summary_<career>.md`` in your ``job_hunt/`` folder.
   One file per career slug (e.g. ``summary_software.md``, ``summary_data.md``).

This command is useful when you want the AI output but do not want to
compile a PDF yet.

----

:compile:`daiana compile`
-------------------------

Render a LaTeX template and compile it to PDF from interactive prompts.
Use this when you already know the job details or want to enter them manually.

.. code-block:: bash

   daiana compile --cv
   daiana compile --cl --username jane

**Flags**

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Flag
     - Description
   * - ``--cv``
     - Use the CV template.
   * - ``--cl``
     - Use the cover letter template.
   * - ``--username`` / ``-un``
     - Name used in the output PDF filename (default: ``user_name``).
   * - ``--verbose``
     - Print LaTeX compilation log details to the terminal.

After compilation, you can optionally save the job to the CSV tracker.

----

:save:`daiana save`
-------------------

Manually log a job application to the CSV tracker **without compiling anything**.
This is useful when you apply through an external portal and just want to
record the application.

.. code-block:: bash

   daiana save --career software

**Flags**

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Flag
     - Description
   * - ``--career`` / ``-cp``
     - Career path label *(required)* — for example, ``software`` or ``data``.

After the flag, you are prompted for:

- Job position
- Company name
- Location
- Job link *(optional)*

The entry is appended to ``job_tracking/<career>.csv`` with status ``applied``.
