import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import base64
from urllib.parse import urlparse, parse_qs

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/133.0 Safari/537.36"
    )
}


def decode_bing_url(href):

    print("\nRAW BING URL:")
    print(href)

    try:
        parsed = urlparse(href)
        params = parse_qs(parsed.query)

        encoded = params.get("u", [""])[0]

        print("\nENCODED u:")
        print(encoded)

        if encoded.startswith("a1"):
            encoded = encoded[2:]

        encoded += "=" * (-len(encoded) % 4)

        decoded = base64.urlsafe_b64decode(encoded).decode(
            "utf-8",
            errors="ignore"
        )

        print("\nDECODED URL:")
        print(decoded)

        return decoded

    except Exception as e:

        print("\nDECODE ERROR:")
        print(e)

        return href


query = 'site:linkedin.com/posts "recruitment partner"'

url = "https://www.bing.com/search?q=" + quote(query)

response = requests.get(
    url,
    headers=HEADERS,
    timeout=30
)

print("STATUS:", response.status_code)
print("PAGE SIZE:", len(response.text))

soup = BeautifulSoup(response.text, "html.parser")

print("\n" + "=" * 70)
print("BING RESULTS FOUND")
print("=" * 70)

items = soup.select("li.b_algo")

print("NUMBER OF b_algo RESULTS:", len(items))

for number, item in enumerate(items[:10], start=1):

    title_tag = item.select_one("h2")
    link_tag = item.select_one("h2 a")

    print("\n" + "-" * 70)
    print("RESULT:", number)

    if title_tag:
        print("TITLE:")
        print(title_tag.get_text(" ", strip=True))
    else:
        print("NO TITLE")

    if link_tag:

        raw_url = link_tag.get("href", "")

        print("\nRAW HREF:")
        print(raw_url)

        decode_bing_url(raw_url)

    else:
        print("NO LINK")

    print("\nFULL RESULT TEXT:")
    print(item.get_text(" ", strip=True)[:1500])
