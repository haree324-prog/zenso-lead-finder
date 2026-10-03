import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

query = 'site:linkedin.com/posts "manpower agency" "India"'

url = "https://www.google.com/search?q=" + quote(query)

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/133.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=30)

print("Status:", response.status_code)
print("Page size:", len(response.text))

soup = BeautifulSoup(response.text, "html.parser")

print("\n--- SEARCH RESULTS ---\n")

results = soup.select("div.MjjYud")

for result in results[:10]:
    text = result.get_text(" ", strip=True)

    links = result.select("a")

    linkedin_url = ""

    for link in links:
        href = link.get("href", "")
        if "linkedin.com/posts/" in href:
            linkedin_url = href
            break

    if linkedin_url:
        print("LINKEDIN POST:")
        print(linkedin_url)
        print("TEXT:")
        print(text[:1500])
        print("-" * 80)
