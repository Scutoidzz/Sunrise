import json
import os
import queue
import sys
import threading
import time
import zipfile

try:
    import sounddevice as sd
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    print("Vosk or sounddevice not installed. Voice recognition disabled.")

TINY_MODEL_DIR = "voice/vosk-model-tiny-en-us-0.15"
TINY_MODEL_ZIP = "voice/vosk-model-tiny-en-us-0.15.zip"
SMALL_MODEL_DIR = "voice/vosk-model-small-en-us-0.15"

def _ensure_tiny_model():
    if os.path.isdir(TINY_MODEL_DIR):
        return True
    if os.path.exists(TINY_MODEL_ZIP):
        try:
            with zipfile.ZipFile(TINY_MODEL_ZIP, "r") as zip_ref:
                zip_ref.extractall("voice")
            return os.path.isdir(TINY_MODEL_DIR)
        except Exception as e:
            print(f"Failed to extract tiny Vosk model: {e}")
    return False

def get_model_path():
    """Read voice model size from config and return appropriate path."""
    model_size = "tiny"
    low_ram_mode = True
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            model_size = config.get("voice_model_size", "tiny")
            low_ram_mode = config.get("low_ram_mode", True)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    if low_ram_mode:
        model_size = "tiny"

    if model_size == "tiny":
        if _ensure_tiny_model():
            return TINY_MODEL_DIR
        if os.path.isdir(SMALL_MODEL_DIR):
            return SMALL_MODEL_DIR
        return TINY_MODEL_DIR

    if os.path.isdir(SMALL_MODEL_DIR):
        return SMALL_MODEL_DIR
    if _ensure_tiny_model():
        return TINY_MODEL_DIR
    return SMALL_MODEL_DIR


class VoiceRecognizer:
    def __init__(self, lazy_load=True, unload_on_stop=True, queue_max=20):
        self.model = None
        self.recognizer = None
        self.is_listening = False
        self.result_queue = queue.Queue(maxsize=queue_max)
        self.thread = None
        self.sample_rate = 16000
        self.lazy_load = lazy_load
        self.unload_on_stop = unload_on_stop
        
        if not self.lazy_load:
            self._load_model()
    
    def _load_model(self):
        """Load the Vosk model if it exists."""
        if not VOSK_AVAILABLE:
            print("Vosk not available - skipping model load")
            return False

        if self.model is not None and self.recognizer is not None:
            return True
        
        model_path = get_model_path()
        if not model_path or not os.path.exists(model_path):
            print(f"Vosk model not found at {model_path}")
            return False

        try:
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            model_size = "tiny" if "tiny" in model_path else "small"
            print(f"Vosk {model_size} model loaded successfully")
            return True
        except Exception as e:
            print(f"Failed to load Vosk model: {e}")
        return False

    def _unload_model(self):
        self.recognizer = None
        self.model = None
    
    def is_model_available(self):
        """Check if the model is loaded and available."""
        return VOSK_AVAILABLE and self.model is not None

    def start_listening(self):
        if self.is_listening:
            return
        
        if not self.is_model_available():
            if not self._load_model():
                print("Cannot start listening: Vosk model not available")
                return
        if not self.is_model_available():
            return
            
        self.is_listening = True
        self.thread = threading.Thread(target=self._listen_loop)
        self.thread.daemon = True
        self.thread.start()

    def stop_listening(self):
        self.is_listening = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
        if self.unload_on_stop:
            self._unload_model()

    def _listen_loop(self):
        """Main listening loop using sounddevice."""
        def callback(indata, frames, time_info, status):
            """This is called for each audio block."""
            if status:
                print(f"Audio status: {status}", file=sys.stderr)
            # Convert to bytes and feed to recognizer
            data = bytes(indata)
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    if self.result_queue.full():
                        try:
                            self.result_queue.get_nowait()
                        except queue.Empty:
                            pass
                    try:
                        self.result_queue.put_nowait(text)
                    except queue.Full:
                        pass
        
        try:
            # Open audio stream
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=callback
            ):
                while self.is_listening:
                    time.sleep(0.1)
        except Exception as e:
            print(f"Audio stream error: {e}")
            self.is_listening = False

    def get_results(self):
        """Get all accumulated results and clear the queue."""
        results = []
        while not self.result_queue.empty():
            try:
                results.append(self.result_queue.get_nowait())
            except queue.Empty:
                break
        return results
