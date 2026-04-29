# Configuration file for the Sphinx documentation builder.
#
# dAIana — single-page documentation site
#
# Structure:
#   daiana/          <- package
#   docs/
#     source/
#       conf.py      <- this file
#       index.md     <- your single page (MyST Markdown)
#       _static/     <- custom CSS, logo, etc.
#     Makefile
#
# Workflow:
#   1) Write your content in docs/source/index.md (MyST Markdown).
#   2) Drop any assets (logo, custom CSS) into docs/source/_static/.
#   3) Run:  cd docs && make clean html
#   4) Preview: open build/html/index.html
#   5) Push to main → GitHub Actions auto-deploys to GitHub Pages.

import os
import sys

# -- Path setup ---------------------------------------------------------------

# Point Sphinx at the package so autodoc can find it if needed later.
sys.path.insert(0, os.path.abspath("../../"))  # repo root
sys.path.insert(0, os.path.abspath("../../daiana"))  # package

# -- Project information ------------------------------------------------------

project = "dAIana"
copyright = "2026, PanoPepino"
author = "PanoPepino"
release = "1.0.0"

# -- General configuration ----------------------------------------------------

extensions = [
    "myst_parser",              # Write content in Markdown instead of RST
    "sphinx.ext.autodoc",
    "sphinx_design",          # for the grid cards
]


# Accept both .rst and .md source files
source_suffix = {
    ".rst": "restructuredtext",
    ".md":  "markdown",
}

# MyST options — enables useful directives in your .md files
myst_enable_extensions = [
    "colon_fence",      # :::note / :::warning blocks
    "deflist",          # definition lists
    "tasklist",         # - [ ] / - [x] checkboxes
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- HTML output --------------------------------------------------------------

html_theme = "furo"
html_title = "dAIana 🏹"
html_short_title = "dAIana"

# Optional: drop a logo at docs/source/_static/logo.svg
# html_logo = "_static/logo.svg"

html_static_path = ["_static"]

# GitHub Pages base URL
html_baseurl = "https://panopepino.github.io/dAIana/"

# Disable Jekyll processing on GitHub Pages
html_extra_path = [".nojekyll"]

# Proper file extensions for GitHub Pages
html_file_suffix = ".html"
html_link_suffix = ".html"

# -- Furo theme options -------------------------------------------------------
# Brand colour pulled from COMMAND_COLORS["init"] in daiana/utils/design/colors.py
# Khaki/warm sand for light mode, slightly lighter for dark mode.

html_theme_options = {
    "sidebar_hide_name": False,
    "light_css_variables": {
        "color-brand-primary":    "#BC8A5F",   # khaki — init colour
        "color-brand-content":    "#BC8A5F",
        "color-highlight-on-target": "#FDF3E7",
    },
    "dark_css_variables": {
        "color-brand-primary":    "#D4A96A",
        "color-brand-content":    "#D4A96A",
        "color-highlight-on-target": "#3A2F1E",
    },
    # Footer links
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/PanoPepino/dAIana",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0"
                     viewBox="0 0 16 16" height="1em" width="1em"
                     xmlns="http://www.w3.org/2000/svg">
                  <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53
                            5.47 7.59.4.07.55-.17.55-.38
                            0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94
                            -.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53
                            .63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66
                            .07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95
                            0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12
                            0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27
                            .68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82
                            .44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15
                            0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48
                            0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38
                            A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
                </svg>
            """,
            "class": "",
        },
    ],
}

# -- Syntax highlighting ------------------------------------------------------

pygments_style = "friendly"
pygments_dark_style = "monokai"   # Furo-specific dark mode highlighter
