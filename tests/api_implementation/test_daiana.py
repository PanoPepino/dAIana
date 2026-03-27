#!/usr/bin/env python3  # This makes it executable
import argparse
import os
import json
import requests
import signal

from openai import OpenAI
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from contextlib import contextmanager


load_dotenv()  # Load the .env with the key (secret)
client = OpenAI(api_key=os.getenv("PERPLEXITY_API_KEY"),
                base_url="https://api.perplexity.ai")  # The installed agent to throw commands at


# Timeout manager, to cut if it takes more than 5s to extract the info from html
@contextmanager
def timeout(seconds):
    def timeout_handler(signum, frame):
        raise TimeoutError("Process timed out after 5s")
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def job_parser(url_or_file):
    with timeout(5):  # 5s total cap
        session = requests.Session()
        retry = Retry(total=2, backoff_factor=0.1)
        session.mount('http://', HTTPAdapter(max_retries=retry))
        session.mount('https://', HTTPAdapter(max_retries=retry))

    if url_or_file.startswith('https'):
        resp = session.get(url_or_file, timeout=3)
        resp.raise_for_status()
        html_content = resp.text

    else:
        with open(url_or_file, 'r') as f:
            html_content = f.read()

    soup = BeautifulSoup(html_content, 'lxml')  # Scrapper to get info from html
    job_text = ' '.join([p.text for p in soup.find_all(['h1', 'h2', 'p', 'div'],
                                                       class_=lambda x: x and any(kw in x.lower() for kw in ['job', 'position', 'role', 'description']))])

    if not job_text.strip():
        job_text = soup.get_text()[:5000]  # Fallback, truncate tokens

    response = client.chat.completions.create(
        model="sonar",
        messages=[
            {
                "role": "system",
                "content": "JSON extractor ONLY. Match schema exactly."
            },
            {
                "role": "user",
                "content": f"""Extract for LaTeX cover letter from job text:
        Text: {job_text[:4500]}


        Output ONLY:""" + json.dumps({
                    "job_position": "",
                    "company_name": "",
                    "company_challenge": "",
                    "career": "data|rd|quant",
                    "location": "",
                    "job_link": url_or_file
                }, ensure_ascii=False)
            }
        ],
        temperature=0.0
    )

    content = response.choices[0].message.content.strip()
    print("Raw:", repr(content))  # DEBUG: See exact output
    result = json.loads(content)

    return result  # To get the answer


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Daiana: Parse Job HTML with PPLX')
    parser.add_argument("html_file", help="Path to job HTML file")
    args = parser.parse_args()

    result = job_parser(args.html_file)
    print(json.dumps(result, indent=2))
