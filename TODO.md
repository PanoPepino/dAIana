

# Important things to do
- [X] Create compiler so that the bash file is called and runs the .tex files.
- [X] Fix template_letter thing + name of templates.
- [X] Add fun descriptions to each function (prepare your hunt, show your preys, etc.)
- [X] Try to implement API thing to call GPT/Perplexity with given prompt to provide recommended path and stuff.
- [X] Enhance update command so that one can choose position and then change any column.
- [X] Fix coloring prompt output. (investigate rich-click stuff)



# For Saturday 28th March

- [ ] Create Legend for color meaning.
- [ ] Create help commands so that anyone can understand what each thing does.
- [ ] Document compiler and any other func.



# Next wave of improvements
- [ ] Continue developing the test_daiana.py: Engineer prompt that always hits a good companychallenge issue. Ideally, it should allow you to manually edit the json before accepting and sending to compile.
- [ ] Create an "oracle" command: It calls the AI, feeds a job description link and then the AI provides suggested skills and projects among the ones you have stored for your CV and tailored first paragraph last sentence about your background and company challenges. It will also provide dict to pass to CV and CL to compile.
- [ ] Create a "hunt" command: It calls oracle and stops displaying the options it recommends. If you press yes, it will then compile and save in database.
