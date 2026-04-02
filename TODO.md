# Next wave of improvements

- [ ] Rewrite Prompts to be bullet proof. Should be sort, yet powerful and concise so that AI understand what user wants exactly.
- [ ] Move Prompts (including `extract_job_via_oracle` and `write_sentence_via_oracle` user inputs) to templates. 
    - WHY? Because in this way one can easily manipulate and change the prompts to tune to their needs.
- [ ] Subsequently, this would imply to make those function go and read the prompts in that directory.
- [ ] Add an extra function, i.e. `project_selector_via_oracle` and related prompts. 
    - WHY? The idea is to increase the modularity of this project. The user can define some default projects in templates/cv_and_letter/loader/variants.tex and call those in the template_cv.tex by substituting according to supervised choices of AI.
    - HOW?:
        1) User defines some rigid projects in the form of name_project -> \begin{itemize} points of project \end{itemize} to be nested inside the project itemize. Each project has a latex \command name. Similar to paragraphs in cover letter (see variants.tex)
        2) User defines some rigid sentences about each of those projects. Similarly, give to each sentence a given latex \command name.
        3) `project_selector_via_oracle`, given the right prompt to identify challenges and requirements of the job position, **selects** 3 (or more, by user choice) projects by relevance and matching to the job requirements.
        4) It lets the user rearrange them from terminal
        5) If right, it selects also associated latex \commands for each project sentence and arrange by importance.
        6) It passes those projects \commands names to substitute in template of the cv and it also passes the associated project sentences to the cover letter.
        6) Render template

- [] Add an extra function, i.e. `skill_selector_via_oracle` and related prompts. 
    - WHY? Similarly to `project_selector_via_oracle`, it will allow for further modularity and tuning of the CV and cover letter.
    - HOW:
        1) User defines some given skills. In this case, I think it could be better in the form of .json file, with nested dicts. 
        2) Some of those skills could be also part of a background or similar list.
        3) `skill_selector_via_oracle`, given fine tuned prompts, will match each set of skills against the job description and will output the most fitting skills arranged by order of importance.
        4) If the user accepts the ordering, it will pass the that construction to the Skills & Competencies section of the template_cv.tex file.
        5) Similarly, it will also choose the best suited 3/4 background skills to be passed to the template_cl.tex file.
        6) Render template

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

----
----






# Important things (Already DONE)
- [X] Create compiler so that the bash file is called and runs the .tex files.
- [X] Fix template_letter thing + name of templates.
- [X] Add fun descriptions to each function (prepare your hunt, show your preys, etc.)
- [X] Try to implement API thing to call GPT/Perplexity with given prompt to provide recommended path and stuff.
- [X] Enhance update command so that one can choose position and then change any column.
- [X] Fix coloring prompt output. (investigate rich-click stuff)
- [X] Create an "oracle" command: It calls the AI, feeds a job description link and then the AI provides suggested skills and projects among the ones you have stored for your CV and tailored first paragraph last sentence about your background and company challenges. It will also provide dict to pass to CV and CL to compile.
- [X] Create Legend for color meaning of status.
- [X] Create help commands so that anyone can understand what each thing does.
- [X] Create a "hunt" command: It calls oracle and stops displaying the options it recommends. If you press yes, it will then compile and save in database.
- [X] To create 2 flags for oracle. One for extracting job data, one for tailor sentences.
- [X] Apply both flags to the hunt command. Add possibility of rewriting dicts before compiling.
- [X] Push and check what import and similar things are required for satisfactory pytest
- [X] Get a fucking good deployment, please.


