Quickstart
==========

This page walks you through the full first-time setup: install the package,
copy the template folder to your machine, configure your LLM provider, and
verify everything works before your first hunt.

----

Requirements
------------

Before installing dAIana, make sure you have:

- Python 3.10 or higher.
- ``pdflatex`` and the ``moderncv`` package on your ``$PATH``.
- An API key from **Perplexity** (``sonar`` / ``sonar-pro`` / ``sonar-max``)
  or **OpenAI** (``gpt-4o-mini`` / ``gpt-4o``).

.. code-block:: bash

   # macOS (MacTeX)
   brew install --cask mactex

   # Ubuntu / Debian
   sudo apt install texlive-full

Installation
------------

.. code-block:: bash

   pip install daiana

Step 1 — Copy the template folder
----------------------------------

Run this command from inside the cloned or installed dAIana directory.
It copies the ``job_hunt/`` folder — which contains your LaTeX templates,
prompt files, and tracking folders — to any location you choose.

.. code-block:: bash

   daiana init --copy_dir

You will be prompted for a destination path. If you press Enter, it defaults
to your home directory. The result will be a ``job_hunt/`` folder at that
location, with this structure:

.. code-block:: text

   job_hunt/
   ├── cv_and_letter/
   │   ├── template_cv.tex      ← your CV template
   │   ├── template_cl.tex      ← your cover letter template
   │   └── loader/              ← modular LaTeX \newcommand files
   ├── prompts/                 ← AI prompt files (Markdown)
   │   ├── background/
   │   ├── career/
   │   ├── job/
   │   ├── projects/
   │   └── sentence/
   ├── job_tracking/            ← CSV files are saved here
   └── pdf_output/              ← compiled PDFs land here

.. note::

   All dAIana commands must be run **from inside** this ``job_hunt/`` folder.
   The ``.env`` file created in the next step is written there.

Step 2 — Configure your provider
---------------------------------

Navigate into the copied folder and run:

.. code-block:: bash

   cd path/to/job_hunt
   daiana init --set_env

You will be prompted for:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Prompt
     - What to enter
   * - Provider
     - ``perplexity`` or ``openai``.
   * - Model
     - For example ``sonar``, ``sonar-pro``, or ``gpt-4o-mini``.
   * - Base URL
     - Pre-filled automatically for known providers.
   * - API key name
     - For example ``PERPLEXITY_API_KEY``.
   * - API key value
     - Your actual secret key. The input is hidden.

All values are written to a ``.env`` file in the current directory and loaded
automatically on every subsequent command.

.. tip::

   If you already have an environment file, double-check that the provider,
   model, and API key name match the values expected by your account.

Step 3 — Verify your setup
---------------------------

Before your first hunt, run:

.. code-block:: bash

   daiana check --env --prompts

- ``--env`` prints the loaded environment variables and confirms the LLM client
  can be built with your credentials.
- ``--prompts`` loads every prompt file from ``job_hunt/prompts/`` and confirms
  they are readable and non-empty.

If either check fails, fix the reported issue before continuing.

.. warning::

   Do not skip this step. If the environment or prompt files are misconfigured,
   the later commands may fail in confusing ways.

Next steps
----------

Once ``daiana check`` passes, you are ready to go.

- First hunt → see :doc:`usage`
- Customise templates and prompts → see :doc:`personalisation`