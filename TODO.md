# Next wave of improvements


- [ ] Fix issue with updater (something about tuple) when oracle/hunt mode.
- [ ] Make simple init that copies contents of templates folder wherever.

- [ ] Create a basic daiana `init` CLI command.
    - WHY: In this way, dAIana can guide the user to set things up. From basic info, to selecting career paths and so on.
    - HOW:
        0) It should ask permission to copy/paste the templates/ directory at the location where dAIana is invoked.
        1) First, dAIana asks the user name, family_name, phonenumber, email, linkedin and other socialnetwork information.
        2) It goes then and substitute these fields in the basic information. (PERHAPS I should create a basic_info.tex where all this should be located?)
        3) Ask for the API key to set the enviroment with the key (I guess that this key is common to the VENV?)
        4) Ideally it should then do some initial scrapping of the user's LinkedIn profile to extract background and skills? + Recommend 3/4 career_paths.
        5) It should then explain the user how dAIana works. 
        6) Guide the user towards the templates/ directory and give commands on writing down to tailor the CV, cover letter and skills + project files as user wants, but following dAIana requirements.
        7) Some extra steps I cannot imagine yet.


- [ ] Add an extra function, i.e. `skill_selector_via_oracle` and related prompts. 
    - WHY? Similarly to `project_selector_via_oracle`, it will allow for further modularity and tuning of the CV and cover letter.
    - HOW:
        1) User defines some given skills. In this case, I think it could be better in the form of .json file, with nested dicts. 
        2) Some of those skills could be also part of a background or similar list.
        3) `skill_selector_via_oracle`, given fine tuned prompts, will match each set of skills against the job description and will output the most fitting skills arranged by order of importance.
        4) If the user accepts the ordering, it will pass the that construction to the Skills & Competencies section of the template_cv.tex file.
        5) Similarly, it will also choose the best suited 3/4 background skills to be passed to the template_cl.tex file.
        6) Render template



- [ ] Create a more robust readme.md 