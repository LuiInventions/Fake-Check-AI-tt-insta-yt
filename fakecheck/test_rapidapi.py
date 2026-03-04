import requests
import json

headers = {
    "x-rapidapi-host": "instagram130.p.rapidapi.com",
    "x-rapidapi-key": "b5020146d9msh22d87ec083278f0p19faa3jsnf4ac804ce926"
}

url1 = "https://instagram130.p.rapidapi.com/v1/get"
req1 = requests.get(url1, headers=headers, params={"url":"https://www.instagram.com/reel/DOZFgqxiA8K/"})
print("v1/get:", req1.status_code, req1.text[:200])

url2 = "https://instagram130.p.rapidapi.com/api/instagram/mediaByShortcode"
req2 = requests.post(url2, headers={"content-type": "application/json", **headers}, json={"shortcode":"DOZFgqxiA8K"})
print("mediaByShortcode POST:", req2.status_code, req2.text[:200])

url3 = "https://instagram130.p.rapidapi.com/v1/mediaByUrl"
req3 = requests.get(url3, headers=headers, params={"url":"https://www.instagram.com/reel/DOZFgqxiA8K/"})
print("v1/mediaByUrl:", req3.status_code, req3.text[:200])

url4 = "https://instagram130.p.rapidapi.com/v1/links"
req4 = requests.post(url4, headers={"content-type": "application/json", **headers}, json={"url":"https://www.instagram.com/reel/DOZFgqxiA8K/"})
print("v1/links POST:", req4.status_code, req4.text[:200])
