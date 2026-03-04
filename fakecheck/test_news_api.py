import requests
import json

url = "https://news-api14.p.rapidapi.com/v2/search/articles"
querystring = {"query":"nasa","language":"de"}
headers = {
    "x-rapidapi-host": "news-api14.p.rapidapi.com",
    "x-rapidapi-key": "65000146d9msh22d87ec083278f0p19faa3jsnf4ac804ce926"
}
response = requests.get(url, headers=headers, params=querystring)
try:
    print("STATUS:", response.status_code)
    data = response.json()
    print(json.dumps(data, indent=2)[:500])
except Exception as e:
    print(e)
    print(response.text)
