import os
import requests
import sys

# THE "MAXI" MENU (Images Included)
# These files contain the full articles AND images.
URLS = {
    # 1. THE RECOMMENDATION (~6.5 GB)
    # Top 50,000 articles + Images. Fits on most standard SD cards.
    "recommended": "https://download.kiwix.org/zim/wikipedia/wikipedia_en_top_maxi_2024-05.zim",
    
    # 2. THE HEAVYWEIGHT (~48 GB)
    # Top 1 Million articles + Images. 
    # WARNING: Ensure you have 50GB+ free space before running this.
    "1m": "https://download.kiwix.org/zim/wikipedia/wikipedia_en_top1m_maxi_2024-06.zim",

    # 3. THE TESTER (~30 MB)
    # Top 100 articles + Images. Perfect for testing your image-extraction code.
    "100": "https://download.kiwix.org/zim/wikipedia/wikipedia_en_100_maxi_2024-06.zim"
}

DEST_FOLDER = "knowledge_data"

def kiwix_download(book, progress_callback=None):
    """
    Downloads the requested Kiwix ZIM file (Maxi/Image versions).
    :param book: 'recommended' (6GB), '1m' (48GB), or '100' (30MB)
    """
    url = URLS.get(book)
    if not url:
        print(f"Error: Unknown book '{book}'. Options: recommended, 1m, 100")
        return

    if not os.path.exists(DEST_FOLDER):
        os.makedirs(DEST_FOLDER)

    filename = os.path.join(DEST_FOLDER, url.split("/")[-1])
    
    # Check if we already have it
    if os.path.exists(filename):
        print(f"File {filename} already exists. Skipping download.")
        if progress_callback:
            progress_callback(100)
        return

    print(f"Starting download: {filename}")
    
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024 * 1024 # 1MB chunks
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