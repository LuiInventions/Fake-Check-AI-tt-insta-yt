import requests

url = "https://instagram130.p.rapidapi.com/api/instagram/mediaByShortcode"
payload = { "shortcode": "DOZFgqxiA8K" }
headers = {
    "content-type": "application/json",
    "x-rapidapi-host": "instagram130.p.rapidapi.com",
    "x-rapidapi-key": "b5020146d9msh22d87ec083278f0p19faa3jsnf4ac804ce926"
}
response = requests.post(url, json=payload, headers=headers)
print("STATUS:", response.status_code)
print("HEADERS:", response.headers)
print("BODY:", response.text)
