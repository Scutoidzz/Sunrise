import os
import requests
import subprocess
import sys


# TODO: Also add options for non images, perhaps in settings.
URLS = {
    "recommended": "https://download.kiwix.org/zim/wikipedia/wikipedia_en_top_maxi_2025-12.zim",
    
    "1m": "https://download.kiwix.org/zim/wikipedia/wikipedia_en_top1m_maxi_2026-01.zim",

    "100": "https://download.kiwix.org/zim/wikipedia/wikipedia_en_100_2026-01.zim"
}

DEST_FOLDER = "knowledge_data"

def kiwix_download(book, progress_callback=None):

    url = URLS.get(book)
    if not url:
        print(f"Error: Unknown book '{book}'. Options: recommended, 1m, 100")
        return

    if not os.path.exists(DEST_FOLDER):
        os.makedirs(DEST_FOLDER)

    filename = os.path.join(DEST_FOLDER, url.split("/")[-1])
    
    # Check if we already have it
    if os.path.exists(filename):
        subprocess.call(["rm", filename]) 
        pass

    print(f"Starting download: {filename}")
    
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024 * 1024
            downloaded = 0

            with open(filename, "wb") as f:
                for data in response.iter_content(block_size):
                    downloaded += len(data)
                    f.write(data)
                    
                    if total_size > 0 and progress_callback:
                        percent = int((downloaded / total_size) * 100)
                        progress_callback(percent)
                        
        print("Download complete.")

    except Exception as e:
        print(f"Download failed: {e}")