import sys
import os

try:
    import yt_dlp
    print("yt_dlp imported")
except ImportError:
    print("yt_dlp not found")
    sys.exit(1)

image_url = "https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg"
print("Testing yt-dlp on direct image link...")
ydl_opts = {
    'outtmpl': '/tmp/test_image.%(ext)s',
    'quiet': True,
    'no_warnings': True,
}
try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(image_url, download=True)
        print("Success!", info.get('title'))
except Exception as e:
    print(f"yt-dlp failed: {e}")

print("Testing requests fallback on direct link...")
try:
    import requests
    res = requests.get(image_url, stream=True)
    res.raise_for_status()
    # guess extension
    ext = res.headers.get("content-type", "").split("/")[-1]
    if not ext or ext == "jpeg": ext = "jpg"
    final_path = f"/tmp/test_image2.{ext}"
    with open(final_path, "wb") as f:
        for chunk in res.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Requests success! Saved to {final_path}")
except Exception as e:
    print(f"Requests failed: {e}")
