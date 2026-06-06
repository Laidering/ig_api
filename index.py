from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

# ============================
#      IG DOWNLOADER 
# ============================
def ig_dl(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 15; 23124RA7EO Build/AQ3A.240829.003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.7444.174 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://dirpy.com/'
        }

        # Create URL
        if 'dirpy.com' not in url:
            dirpy_url = f"https://dirpy.com/studio?url={requests.utils.quote(url)}"
        else:
            dirpy_url = url

        response = requests.get(dirpy_url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Title
        title_tag = soup.find('h2', class_='panel-title')
        title = title_tag.get_text().strip() if title_tag else "Instagram Video"

        # Clean title
        title = re.sub(r'ig Video Download', '', title, flags=re.IGNORECASE).strip()

        # Video URL
        video_url = None
        
        # Primary method
        media_source = soup.find('source', id='media-source')
        if media_source and media_source.get('src'):
            video_url = media_source['src']
        
        # Alternative methods
        if not video_url:
            video_tag = soup.find('video')
            if video_tag and video_tag.get('src'):
                video_url = video_tag['src']
        
        if not video_url:
            # Meta tag se bhi try karo
            meta_video = soup.find('meta', property='og:video')
            if meta_video and meta_video.get('content'):
                video_url = meta_video['content']

        if not video_url:
            return {"error": "Video link Not Found."}

        return {
            "title": title,
            "videoUrl": video_url,
        }

    except Exception as e:
        return {"error": str(e)}


# ============================
#      FLASK ROUTES
# ============================

@app.route('/download/instagram', methods=['GET'])
def download_instagram():
    url = request.args.get('url')
    
    if not url:
        return jsonify({"status": False, "error": "Url is required"}), 400
    
    if 'instagram.com' not in url:
        return jsonify({"status": False, "error": "Enter Valid Instagram URL"}), 400

    result = ig_dl(url)
    
    if "error" in result:
        return jsonify({"status": False, "error": result["error"]}), 500
    else:
        return jsonify({"status": True, "result": result}), 200


# Optional: Health Check
@app.route('/')
def home():
    return jsonify({
        "status": True,
        "message": "Instagram Downloader API is running",
        "endpoints": ["/download/instagram?url=INSTAGRAM_LINK"]
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)