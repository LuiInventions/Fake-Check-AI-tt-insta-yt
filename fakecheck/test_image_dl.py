import urllib.request
import yt_dlp
import uuid

# A dummy target URL mimicking an IG image CDN link
image_url = "https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg"
output_path = f"/tmp/{uuid.uuid4()}.%(ext)s"

ydl_opts = {
    'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]/bestvideo+bestaudio/best',
    'outtmpl': output_path,
    'quiet': True,
    'no_warnings': True,
}

print("Testing yt-dlp on direct image link...")
try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(image_url, download=True)
        print("Success!", info.get('title'))
except Exception as e:
    print(f"yt-dlp failed: {e}")

print("\nTesting requests fallback on direct link...")
try:
    import requests
    res = requests.get(image_url, stream=True)
    res.raise_for_status()
    # guess extension from content-type
    ext = res.headers.get("content-type", "").split("/")[-1]
    if not ext or ext == "jpeg": ext = "jpg"
    final_path = f"/tmp/test_image.{ext}"
    with open(final_path, "wb") as f:
        for chunk in res.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Requests success! Saved to {final_path}")
except Exception as e:
    print(f"Requests failed: {e}")
