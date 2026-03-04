import requests
import os
import json
import sys

# use existing rapidapi key from backend config
env_path = "/home/serveradmin/Fake Check App/fakecheck/.env"
rapidapi_key = None
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("RAPIDAPI_KEY="):
                rapidapi_key = line.strip().split("=", 1)[1].strip().strip('"\'')
                break

if not rapidapi_key:
    # try config.py
    sys.path.append("/home/serveradmin/Fake Check App/fakecheck/backend")
    try:
        from config import get_settings
        rapidapi_key = get_settings().RAPIDAPI_KEY
    except Exception as e:
        print(f"Could not load key: {e}")
        sys.exit(1)

print(f"Using RapidAPI Key starting with: {rapidapi_key[:5]}...")

# 1. Try Sonoteller API (Music analysis)
# Endpoint: https://rapidapi.com/sonoteller-ai-sonoteller-ai-default/api/sonoteller-ai
url = "https://sonoteller-ai.p.rapidapi.com/analyze"
print("\nTesting Sonoteller API format...")
print("Requires sending audio or youtube link. We will just check if we have access.")

headers = {
"X-RapidAPI-Key": rapidapi_key,
"X-RapidAPI-Host": "sonoteller-ai.p.rapidapi.com"
}
# Just a dummy request to check Auth
response = requests.get("https://sonoteller-ai.p.rapidapi.com/info", headers=headers)
print("Sonoteller Info:", response.status_code, response.text[:100])

