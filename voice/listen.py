import json
import os
import queue
import sys
import threading
import time

try:
    import sounddevice as sd
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    print("Vosk or sounddevice not installed. Voice recognition disabled.")

# Path to the Vosk small model (more accurate than tiny)
MODEL_PATH = "voice/vosk-model-small-en-us-0.15"


class VoiceRecognizer:
    def __init__(self):
        self.model = None
        self.recognizer = None
        self.is_listening = False
        self.result_queue = queue.Queue()
        self.thread = None
        self.sample_rate = 16000
        
        # Try to load the model
        self._load_model()
    
    def _load_model(self):
        """Load the Vosk model if it exists."""
        if not VOSK_AVAILABLE:
            print("Vosk not available - skipping model load")
            return
        if os.path.exists(MODEL_PATH):
            try:
                self.model = Model(MODEL_PATH)
                self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
                print("Vosk small model loaded successfully")
            except Exception as e:
                print(f"Failed to load Vosk model: {e}")
        else:
            print(f"Vosk model not found at {MODEL_PATH}")
    
    def is_model_available(self):
        """Check if the model is loaded and available."""
        return VOSK_AVAILABLE and self.model is not None

    def start_listening(self):
        if self.is_listening:
            return
        
        if not self.is_model_available():
            print("Cannot start listening: Vosk model not available")
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
                    self.result_queue.put(text)
        
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