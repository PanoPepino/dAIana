Environment & identity
======================

- **Location**: ``job_hunt/.env``

``daiana init`` creates this file. In canse you missed the option ``daiana init --set_env``, open it and fill in your credentials
and defaults. ``daiana check`` will warn you if any required key is missing.

.. code-block:: bash

    # ── LLM provider ────────────────────────────────
    DAIANA_PROVIDER=perplexity          # or: openai
    DAIANA_MODEL=sonar                  # perplexity: sonar | sonar-pro | sonar-max
                                        # openai:      gpt-4o-mini | gpt-4o
    PERPLEXITY_API_KEY=pplx-...
    OPENAI_API_KEY=sk-...               # only needed if DAIANA_PROVIDER=openai

    # ── Identity ─────────────────────────────────────
    DAIANA_USER_NAME=jane               # used as the PDF filename suffix

``DAIANA_USER_NAME`` is the default value for the ``--username`` flag in
``daiana hunt`` and ``daiana compile``. You can always override it per run.