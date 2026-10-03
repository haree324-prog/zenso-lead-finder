import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

query = 'site:linkedin.com/posts manpower recruitment'

url = "https://www.bing.com/search?q=" + quote(query)

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

print("\n--- BING RESULTS ---\n")

count = 0

for result in soup.select("li.b_algo"):

    title = result.select_one("h2")
    link = result.select_one("h2 a")

    if title and link:
        title_text = title.get_text(" ", strip=True)
        href = link.get("href", "")

        print("TITLE:", title_text)
        print("URL:", href)

        text = result.get_text(" ", strip=True)
        print("TEXT:", text[:1000])

        print("-" * 80)

        count += 1

print("\nTOTAL RESULTS:", count)
