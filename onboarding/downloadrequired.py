import subprocess 
import requests
import zipfile
import os
from .finish_up_tests import verify_files as vf

def download_embedding(progress_callback=None):
    embedding_link = "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/onnx/model.onnx?download=true"
    to_path = "starry/model.onnx"
    response = requests.get(embedding_link, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(to_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if progress_callback and total_size > 0:
                    progress = int((downloaded / total_size) * 100)
                    progress_callback(progress)

def download_sst(progress_callback=None):
    """Download Vosk small English model (~120MB) - more accurate than tiny."""
    voice_link = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    to_path = "voice/vosk-model-small-en-us-0.15.zip"
    
    os.makedirs("voice", exist_ok=True)
    
    response = requests.get(voice_link, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(to_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if progress_callback and total_size > 0:
                    progress = int((downloaded / total_size) * 100)
                    progress_callback(progress)
    
    if progress_callback:
        progress_callback(100)
    
    extract_dir = "voice"
    with zipfile.ZipFile(to_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    if vf() == False:
        raise Exception("Files not found, user will be reminded on cardUI")
    elif vf() == True:
        print("Files found, Finishing setup")
    
    os.remove(to_path)

