

1 - Go to perplexity -> API (set account (taxation is quite high))
2 - I installed pip install openai python-dotenv beautifulsoup4 lxml in my VENV
3 - Tested it works with python -c "import openai; print('Ready')"
4 - Created an API Key from Perplexity API.
5 - Created a .env (not really a VENV) where I stored my API key (superprivate)
6 - Created a simple test_pplx.py to test. One can choose 3 levels of sonar.
7 - Created a more complex .py, that eats a fake .html file created ad-hoc and spits out a json with my desired FIELDNAMES information.
8 - Created an even more complex .py, that eats a real url and spits out a json with my desired FIELDNAMES information.












ARGPARSE -> To transform python script into terminal command. so no need to use python.py at the beginning.
ROBUST PARSING -> real job sites use JS/dynamic content; requests + BS4 fetches full pages. Prompt must ignore noise
DEFENSIVE PARSING -> If the website you want to parse is chaos, help AI to find what you want.