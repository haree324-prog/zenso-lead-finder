import requests

url = "https://www.linkedin.com/search/results/content/?keywords=manpower"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=20)

print("Status:", response.status_code)
print("LinkedIn page received:", len(response.text), "characters")

if response.status_code == 200:
    print("LinkedIn public page is reachable.")
else:
    print("LinkedIn returned status:", response.status_code)
