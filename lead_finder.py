import requests
from bs4 import BeautifulSoup

url = "https://www.linkedin.com/search/results/content/?keywords=manpower%20India"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/133.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=30)

print("Status:", response.status_code)
print("Page size:", len(response.text))

soup = BeautifulSoup(response.text, "html.parser")

text = soup.get_text(" ", strip=True)

print("\n--- LINKEDIN TEXT SAMPLE ---\n")
print(text[:5000])
