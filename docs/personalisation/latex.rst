LaTeX personalisation
=====================

Projects (CV bullets)
---------------------

- **Location**: ``job_hunt/cv_and_letter/loader/variants_cv.tex``

One ``\newcommand`` per project. Each renders as a titled bullet block
inside the CV.

.. code-block:: latex

    \newcommand{\cloudscale}{
    \textcolor{color3}{\textbf{CloudScale — Distributed Microservices Platform}:}
    \begin{itemize}
    \item Designed and deployed a \href{https://github.com/you/cloudscale}{microservices platform}
          handling 1M+ daily requests with 99.9\% uptime on AWS.
    \item Emphasised scalability through clean, containerised architecture.
    \end{itemize}
    }

Add one block per project. The command name (e.g. ``\cloudscale``) must
match the value in ``prompts/projects/projects_name_to_latex.md``.

Projects (cover letter inline)
-------------------------------

- **Location**: ``job_hunt/cv_and_letter/loader/variants_cl.tex``

One ``\newcommand`` per project. Each renders as a short inline phrase
inside the cover letter sentence.

.. code-block:: latex

    \newcommand{\cloudscale}{
        \textit{CloudScale}, a distributed microservices platform designed to handle
        high-throughput workloads with fault-tolerant, containerised services on AWS}

The command name must match the corresponding CV command exactly.

Cover letter body paragraphs
-----------------------------

- **Location**: ``job_hunt/cv_and_letter/loader/variants_cl.tex``

Each career track needs a fixed closing paragraph. The command selected at
compile time is ``\body<career>`` — e.g. ``backend`` → ``\bodybackend``.

.. code-block:: latex

    \newcommand{\bodybackend}{
    My primary focus has been designing and optimising backend systems under
    demanding performance and reliability constraints ...
    }

    \newcommand{\bodydata}{
    My professional interests have increasingly gravitated towards large-scale
    data infrastructure — robust ingestion pipelines and low-latency stream
    processing ...
    }

    \newcommand{\bodyproduct}{
    Alongside my systems background, I have developed a strong interest in
    product-facing engineering ...
    }

Edit the text to match your voice. Add a new ``\body<label>`` command for
every new career label you define in ``careers.md``.