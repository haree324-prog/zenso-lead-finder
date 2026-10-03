import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

query = 'site:linkedin.com/posts "manpower" "recruitment"'

url = "https://www.google.com/search?q=" + quote(query)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/133.0 Safari/537.36"
    )
}

response = requests.get(url, headers=headers, timeout=30)

print("STATUS:", response.status_code)
print("PAGE SIZE:", len(response.text))

soup = BeautifulSoup(response.text, "html.parser")

print("\n--- ALL LINKEDIN URLS FOUND ---\n")

found = 0

for link in soup.find_all("a"):
    href = link.get("href", "")
    text = link.get_text(" ", strip=True)

    if "linkedin.com" in href.lower():
        found += 1

        print("LINK:", href[:1000])
        print("TEXT:", text[:1000])
        print("-" * 80)

print("\nTOTAL LINKEDIN LINKS FOUND:", found)

print("\n--- PAGE TITLE ---\n")
print(soup.title.get_text(strip=True) if soup.title else "No title")

print("\n--- FIRST 3000 CHARACTERS OF PAGE TEXT ---\n")
print(soup.get_text(" ", strip=True)[:3000])
