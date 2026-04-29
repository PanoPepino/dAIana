dAIana
======


**dAIana** is a Python CLI that uses AI API requests from the terminal to tailor LaTeX CVs and cover letters. Feed it a job posting URL, and it scrapes the description, sends it to an LLM for extraction and personalization, then compiles the final documents into PDFs.

.. warning::

   dAIana does **not** write your CV or cover letter from scratch.
   You bring your own LaTeX files. The tool reads a job posting and selects
   **which modular pieces of your templates** to activate for that role.
   No LaTeX setup → nothing to compile.

Here a simple table of all the pages you will find in this documentation.


.. grid:: 2
   :gutter: 2

   .. grid-item-card:: 🚀 Quickstart
      :link: quickstart
      :link-type: doc

      Install the package, copy your templates, configure your API provider,
      and verify everything works before your first hunt.

   .. grid-item-card:: 🔴 Usage
      :link: usage
      :link-type: doc

      Full reference for every command: ``hunt``, ``save``, ``show``, ``update``
      — flags, workflows, and examples.

   .. grid-item-card:: ✏️ Personalisation
      :link: personalisation
      :link-type: doc

      How to wire up your own LaTeX templates and tune the AI prompts
      so the output actually sounds like you.

   .. grid-item-card:: 🗂️ Architecture
      :link: architecture
      :link-type: doc

      How the codebase is layered — commands, core logic, services,
      infra adapters, and utilities explained in one place.


.. admonition:: Why the name dAIana?
   :class: tip

   dAIana comes from Diana, the Roman goddess of the hunt. The name fits the tool’s purpose: hunt down job postings, target the right role, and generate tailored application material from the terminal. Track your prey. Hunt.

.. toctree::
   :hidden:
   :maxdepth: 2

   quickstart
   usage
   personalisation
   architecture