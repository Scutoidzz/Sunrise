import subprocess 
import requests
import tarfile
import os

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
    voice_link = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-zipformer-en-2023-02-21.tar.bz2"
    to_path = "voice/sherpa-onnx-streaming-zipformer-en-2023-02-21.tar.bz2"
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
    with tarfile.open(to_path, "r:bz2") as tar:
        tar.extractall(path=extract_dir)
    
    os.remove(to_path)

