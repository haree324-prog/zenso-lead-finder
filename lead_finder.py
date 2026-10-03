import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse, parse_qs
import base64
import re
import time

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/133.0 Safari/537.36"
    )
}

# Employer-side recruitment/manpower commercial intent.
QUERIES = [
    'site:linkedin.com/posts "recruitment partner"',
    'site:linkedin.com/posts "recruitment partners"',
    'site:linkedin.com/posts "recruitment agency" "looking for"',
    'site:linkedin.com/posts "recruitment agencies" "looking for"',
    'site:linkedin.com/posts "seeking recruitment agencies"',
    'site:linkedin.com/posts "manpower supplier"',
    'site:linkedin.com/posts "manpower suppliers"',
    'site:linkedin.com/posts "manpower agency" "looking for"',
    'site:linkedin.com/posts "staffing partner"',
    'site:linkedin.com/posts "staffing partners"',
    'site:linkedin.com/posts "recruitment vendor"',
    'site:linkedin.com/posts "staffing vendor"',
    'site:linkedin.com/posts "manpower quotation"',
    'site:linkedin.com/posts "recruitment quotation"',
    'site:linkedin.com/posts "submit quotation" recruitment',
    'site:linkedin.com/posts "submit proposal" recruitment',
    'site:linkedin.com/posts "recruitment proposal"',
    'site:linkedin.com/posts "invite agencies" recruitment',
    'site:linkedin.com/posts "bulk hiring" "recruitment partner"',
    'site:linkedin.com/posts "manpower requirement" agency',
    'site:linkedin.com/posts "recruitment requirement" agency',
    'site:linkedin.com/posts "hiring support" "agency"',
]

COUNTRIES = [
    "UAE",
    "Saudi Arabia",
    "Qatar",
    "Oman",
    "Kuwait",
    "Bahrain",
    "DRC",
    "Congo",
    "Zambia",
    "Tanzania",
    "Uganda",
    "Kenya",
    "Ethiopia",
    "Ghana",
    "Nigeria",
    "Rwanda",
    "Mozambique",
    "Botswana",
    "Namibia",
    "South Africa",
]


def decode_bing_url(href):
    """
    Bing normally puts the real destination inside a tracking URL.
    Try to recover the original LinkedIn URL.
    """

    if not href:
        return ""

    if "linkedin.com/" in href:
        # It may already be the real URL.
        if href.startswith("http"):
            return href

    try:
        parsed = urlparse(href)
        params = parse_qs(parsed.query)

        encoded = params.get("u", [""])[0]

        if not encoded:
            return href

        # Bing commonly prefixes its encoded destination with a1.
        if encoded.startswith("a1"):
            encoded = encoded[2:]

        encoded += "=" * (-len(encoded) % 4)

        decoded = base64.urlsafe_b64decode(encoded).decode(
            "utf-8", errors="ignore"
        )

        if decoded.startswith("http"):
            return decoded

    except Exception:
        pass

    return href


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def search_bing(query):
    url = "https://www.bing.com/search?q=" + quote(query)

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        print("\nQUERY:", query)
        print("STATUS:", response.status_code)
        print("PAGE SIZE:", len(response.text))

        soup = BeautifulSoup(response.text, "html.parser")

        results = []

        for item in soup.select("li.b_algo"):

            title_tag = item.select_one("h2")
            link_tag = item.select_one("h2 a")

            if not title_tag or not link_tag:
                continue

            title = clean_text(title_tag.get_text(" ", strip=True))
            bing_url = link_tag.get("href", "")

            destination = decode_bing_url(bing_url)

            snippet_tag = item.select_one(".b_caption")
            snippet = ""

            if snippet_tag:
                snippet = clean_text(
                    snippet_tag.get_text(" ", strip=True)
                )

            results.append({
                "title": title,
                "url": destination,
                "snippet": snippet,
            })

        return results

    except Exception as e:
        print("SEARCH ERROR:", e)
        return []


def is_linkedin_post(url):
    if not url:
        return False

    url_lower = url.lower()

    if "linkedin.com/posts/" in url_lower:
        return True

    if "linkedin.com/feed/update/" in url_lower:
        return True

    return False


def looks_like_excluded_page(url):
    """
    We only want LinkedIn posts.
    Exclude companies, profiles, jobs, etc.
    """

    if not url:
        return True

    url_lower = url.lower()

    excluded = [
        "/company/",
        "/in/",
        "/jobs/",
        "/school/",
        "/groups/",
        "/events/",
    ]

    return any(x in url_lower for x in excluded)


def looks_like_commercial_lead(text):
    """
    First-stage qualification.
    We deliberately require commercial recruitment/manpower intent.
    """

    text = text.lower()

    intent_terms = [
        "recruitment agency",
        "recruitment agencies",
        "recruitment partner",
        "recruitment partners",
        "recruitment vendor",
        "staffing partner",
        "staffing partners",
        "staffing vendor",
        "manpower supplier",
        "manpower suppliers",
        "manpower agency",
        "recruitment quotation",
        "manpower quotation",
        "submit quotation",
        "submit proposal",
        "recruitment proposal",
        "invite agencies",
        "seeking recruitment",
        "looking for recruitment",
        "looking for agencies",
        "recruitment requirement",
        "manpower requirement",
        "hiring support",
        "bulk hiring",
    ]

    return any(term in text for term in intent_terms)


def main():

    print("=" * 70)
    print("ZENSO LINKEDIN EMPLOYER LEAD FINDER")
    print("=" * 70)

    all_leads = []
    seen_urls = set()

    # First test the intent queries without countries.
    # This lets us see whether Bing exposes LinkedIn posts at all.
    test_queries = QUERIES[:]

    # Add a limited country batch for the first test.
    for country in COUNTRIES[:5]:
        for base_query in QUERIES[:6]:
            test_queries.append(
                base_query + " " + country
            )

    print("\nTOTAL SEARCH QUERIES:", len(test_queries))

    for query in test_queries:

        results = search_bing(query)

        for result in results:

            url = result["url"]

            if not is_linkedin_post(url):
                continue

            if looks_like_excluded_page(url):
                continue

            combined_text = (
                result["title"] + " " + result["snippet"]
            )

            if not looks_like_commercial_lead(combined_text):
                continue

            if url in seen_urls:
                continue

            seen_urls.add(url)

            lead = {
                "title": result["title"],
                "url": url,
                "snippet": result["snippet"],
                "matched_query": query,
            }

            all_leads.append(lead)

        # Small pause to reduce aggressive request behaviour.
        time.sleep(1)

    print("\n")
    print("=" * 70)
    print("QUALIFIED LINKEDIN POST LEADS")
    print("=" * 70)

    if not all_leads:
        print("NO QUALIFIED LINKEDIN POSTS FOUND IN THIS TEST.")
    else:
        for number, lead in enumerate(all_leads, start=1):

            print("\nLEAD", number)
            print("TITLE:", lead["title"])
            print("URL:", lead["url"])
            print("SNIPPET:", lead["snippet"])
            print("QUERY:", lead["matched_query"])

    print("\n")
    print("=" * 70)
    print("TOTAL QUALIFIED POSTS:", len(all_leads))
    print("=" * 70)


if __name__ == "__main__":
    main()
