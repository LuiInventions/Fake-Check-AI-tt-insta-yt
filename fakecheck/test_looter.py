import requests
import json

url = "https://instagram-looter2.p.rapidapi.com/post-dl"
querystring = {"url":"https://www.instagram.com/reel/DOZFgqxiA8K/"}
headers = {
    "x-rapidapi-host": "instagram-looter2.p.rapidapi.com",
    "x-rapidapi-key": "65000146d9msh22d87ec083278f0p19faa3jsnf4ac804ce926"
}
response = requests.get(url, headers=headers, params=querystring)
print("STATUS:", response.status_code)
try:
    print(json.dumps(response.json(), indent=2))
except:
    print(response.text)
