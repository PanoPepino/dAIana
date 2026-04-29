# Next wave of improvements


- [ ] Add an extra function, i.e. `skill_selector_via_oracle` and related prompts. 
    - WHY? Similarly to `project_selector_via_oracle`, it will allow for further modularity and tuning of the CV and cover letter.
    - HOW:
        1) User defines some given skills. In this case, I think it could be better in the form of .json file, with nested dicts. 
        2) Some of those skills could be also part of a background or similar list.
        3) `skill_selector_via_oracle`, given fine tuned prompts, will match each set of skills against the job description and will output the most fitting skills arranged by order of importance.
        4) If the user accepts the ordering, it will pass the that construction to the Skills & Competencies section of the template_cv.tex file.
        5) Similarly, it will also choose the best suited 3/4 background skills to be passed to the template_cl.tex file.
        6) Render template



