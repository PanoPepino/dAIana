

# Important things to do
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


# FIRST WEEK APRIL

- [ ] Create a good, cheap, bullet proof!!! prompt to extract information on the company challenges and CRAFT a tailored sentence based on those chanllenges. 

- [ ] Document core/ and utils/ scripts
- [ ] Start basic init to input name and stuff of the like + career paths.




# Next wave of improvements

- [ ] Create an oracle mode (--tailor_cv) to do as follows:
    - Based on your saved skills & projects, it will match them against the job description and reorganise their potential position in the template_cv to maximise chances for succesful application.
    

- [ ] Create some sort of init:
    - This should deploy the templates in a desired location:
    - Then ask the user for name, surname, phone, and things of the like
    - With that info, it will go and substitute things in the latex files (Perhaps create an overall contact.tex to subthings?). 
    - Then it should ask for the linkedin link, scrap your information, evaluate and recommend 3/4 different career paths.
    - If so, it will create 3/4 .csv with those names in the job_tracking folder. 
    - With the scrapped information, it will create a set some document where:
        - All your skills are saved in some sort of dict.
        - All your selected projects are stored.
    - Then it will fix the specific instructiosn for the AI inputs and deploy those specific careers inside the latex files to easily manipulate when compiling.
