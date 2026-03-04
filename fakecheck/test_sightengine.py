import requests
import json
import time

api_user = "1823764496"
api_secret = "qKz3EKbmrGKUbqjAmQV4inNmUC7jQdGT"
video_url = "https://www.w3schools.com/html/mov_bbb.mp4" # Sample generic video

# 1. Submit video
submit_url = "https://api.sightengine.com/1.0/video/check-sync.json"
params = {
    'models': 'genai',
    'api_user': api_user,
    'api_secret': api_secret,
    'stream_url': video_url
}
r = requests.get(submit_url, params=params)
print(r.json())
