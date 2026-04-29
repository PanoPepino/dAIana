Architecture
============

The project follows a layered architecture split into seven top-level packages.
Each layer has a single responsibility, making it easy to extend or swap
components without touching unrelated code.

.. code-block:: text

   daiana/
   ├── cli.py                  # Entry point — registers all Click commands
   ├── commands/               # Thin Click command wrappers
   ├── config/                 # Settings and environment loading
   ├── core/                   # Business logic (one module per command)
   ├── domain/                 # Data models and validation
   ├── infra/                  # I/O adapters (files, LLM, CSV, scraping)
   ├── services/               # Orchestration — glues core + infra together
   └── utils/                  # Shared helpers and constants


``cli.py``
----------

The single entry point declared in ``pyproject.toml``. Imports every
sub-command from ``commands/`` and registers it on the root ``@cli`` group.
You never need to edit this file unless you add a brand-new top-level command.


commands/
---------

One file per CLI command. Each module contains only the Click decorator
boilerplate (flags, prompts, option parsing) and a single call into the
matching service. No business logic lives here.

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Module
     - Command it wires up
   * - ``check_comm.py``
     - ``daiana check`` — validates the ``.env`` file
   * - ``compiler_comm.py``
     - ``daiana compile`` — compiles LaTeX → PDF
   * - ``hunter_comm.py``
     - ``daiana hunt`` — scrapes a URL and runs the full AI pipeline
   * - ``init_comm.py``
     - ``daiana init`` — scaffolds the project folder
   * - ``oracles_comm.py``
     - ``daiana oracle`` — asks the LLM a free-form question
   * - ``saver_comm.py``
     - ``daiana save`` — saves a job to the CSV tracker
   * - ``shower_comm.py``
     - ``daiana show`` — displays saved jobs
   * - ``updater_comm.py``
     - ``daiana update`` — updates a job record


config/
-------

``settings.py`` loads ``.env`` via ``python-dotenv``, exposes typed
constants (provider, model, user name, paths), and raises clear errors when
required keys are missing. Everything else reads config through this module —
never directly from ``os.environ``.


core/
-----

Pure business logic. Each module mirrors a command and knows nothing about
Click or the file system — it receives plain Python objects and returns them.

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Module
     - Responsibility
   * - ``compiler.py``
     - Builds the ``pdflatex`` command, handles aux-file cleanup
   * - ``hunter.py``
     - Orchestrates scrape → LLM extraction → template substitution
   * - ``initer.py``
     - Generates the scaffold folder and starter files
   * - ``oracles.py``
     - Sends a free-form prompt to the LLM and returns the response
   * - ``saver.py``
     - Validates and appends a job record to the CSV tracker
   * - ``shower.py``
     - Filters and formats job records for display
   * - ``updater.py``
     - Locates a record by ID and applies field updates


domain/
-------

``models.py`` defines the data classes (e.g. ``JobRecord``, ``HuntResult``)
shared across layers. ``validation.py`` contains reusable validators called
from both ``core/`` and ``services/`` to enforce business rules before data
is persisted or sent to an LLM.


infra/
------

Adapters that talk to the outside world. Swap any adapter without changing
business logic.

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Module
     - What it wraps
   * - ``csv_repository.py``
     - Read / write the ``job_tracking_*.csv`` files
   * - ``filesystem.py``
     - Path resolution, directory creation, file copy helpers
   * - ``latex_repository.py``
     - Reads ``.tex`` templates, applies ``\\newcommand`` substitutions
   * - ``llm_client.py``
     - Unified client for OpenAI and Perplexity APIs
   * - ``prompt_repository.py``
     - Loads Markdown prompt files from ``job_hunt/prompts/``
   * - ``scraper.py``
     - Fetches and cleans job-posting HTML via ``requests`` + ``bs4``


services/
---------

Thin orchestration layer. Each service wires together one or more ``core``
modules with the ``infra`` adapters they need, then returns the result to
the command layer. Keeping this separation means ``core`` logic stays
unit-testable without mocking I/O.

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Module
     - What it orchestrates
   * - ``check_service.py``
     - Loads settings and reports missing keys
   * - ``compile_service.py``
     - Resolves paths → injects variables → calls ``compiler.py``
   * - ``hunt_service.py``
     - scraper → LLM → latex_repository → compiler
   * - ``init_service.py``
     - filesystem helpers → initer logic
   * - ``oracle_service.py``
     - prompt_repository → llm_client → oracles core
   * - ``save_service.py``
     - validation → csv_repository
   * - ``show_service.py``
     - csv_repository → formatter
   * - ``update_service.py``
     - csv_repository → validation → write-back


utils/
------

Stateless helpers shared everywhere. No layer-specific imports allowed here.

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Module
     - Contents
   * - ``constants.py``
     - String literals, default values, path constants
   * - ``design/``
     - Click styling helpers (colours, banners, progress indicators)
   * - ``for_check.py``
     - Helpers used by the check command (key presence, format tests)
   * - ``for_csv.py``
     - CSV parsing, column normalisation, date formatting
   * - ``for_hunt.py``
     - Text cleaning and chunking utilities for the hunt pipeline
   * - ``for_init.py``
     - Template-file generation helpers for ``daiana init``
   * - ``for_latex.py``
     - ``latex_escape()`` and ``replace_newcommand()`` string utilities
   * - ``for_oracle.py``
     - Prompt-building helpers for oracle queries
   * - ``for_update.py``
     - Field-diff helpers for the update command
   * - ``prompt_loader.py``
     - Reads and caches Markdown prompt files from disk
   * - ``prompts.py``
     - Assembled prompt strings passed to the LLM