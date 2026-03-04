import requests

url = "https://instagram130.p.rapidapi.com/api/instagram/links"
payload = { "url": "https://www.instagram.com/reel/DOZFgqxiA8K/" }
headers = {
    "content-type": "application/json",
    "x-rapidapi-host": "instagram130.p.rapidapi.com",
    "x-rapidapi-key": "b5020146d9msh22d87ec083278f0p19faa3jsnf4ac804ce926"
}
response = requests.post(url, json=payload, headers=headers, timeout=10)
print("STATUS:", response.status_code)
print("BODY:", response.text)
