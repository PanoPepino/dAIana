from openai import OpenAI
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup

load_dotenv()
client = OpenAI(api_key=os.getenv("PERPLEXITY_API_KEY"), base_url="https://api.perplexity.ai")

# Simulate HTML input (replace with file read)
html_content = """
<html><body>
<h1>Data Scientist - Spotify</h1>
<p>Location: Stockholm. Company: Spotify AB. Ideal for data science career.</p>
</body></html>
"""
soup = BeautifulSoup(html_content, 'lxml')  # Clean text
text = soup.get_text()

response = client.chat.completions.create(
    model="sonar",
    messages=[{
        "role": "user",
        "content": f"Extract from job text: {text}\n\nOutput ONLY JSON: {{\"job_position\": \"\", \"company_name\": \"\", \"career\": \"data science\", \"location\": \"\"}}"
    }]
)
print(response.choices[0].message.content)
