import requests
import json

url = "https://instagram-looter2.p.rapidapi.com/post-dl"
querystring = {"url":"https://www.instagram.com/p/CqIbCzYMi5C/"}
headers = {
    "x-rapidapi-host": "instagram-looter2.p.rapidapi.com",
    "x-rapidapi-key": "65000146d9msh22d87ec083278f0p19faa3jsnf4ac804ce926"
}
response = requests.get(url, headers=headers, params=querystring)
try:
    data = response.json()
    print("STATUS:", data.get('status'))
    if "data" in data and "medias" in data["data"]:
        for m in data["data"]["medias"]:
            print("Media Item Keys:", m.keys())
            if "url" in m:
                print("  - URL:", m["url"][:50], "...")
            elif "link" in m:
                print("  - LINK:", m["link"][:50], "...")
            print("  - Type:", m.get("type"), m.get("mediaType"))
except Exception as e:
    print(e)
    print(response.text)
