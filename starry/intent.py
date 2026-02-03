import json
import os
import math

try:
    import numpy as np
    _HAS_NUMPY = True
except Exception as exc:
    np = None
    _HAS_NUMPY = False
    _NUMPY_ERROR = exc

try:
    from starry.process import SunriseBackend
except Exception as exc:
    SunriseBackend = None
    _BACKEND_ERROR = exc


DEFAULT_THRESHOLD = 0.5
DEFAULT_INTENTS = {
    "LIGHT_ON": [
        "turn on the light",
        "turn the light on",
        "turn on lights",
        "lights on",
        "light on",
        "switch on the light",
        "switch the light on",
        "turn on the lamp",
    ],
    "LIGHT_OFF": [
        "turn off the light",
        "turn the light off",
        "turn off lights",
        "lights off",
        "light off",
        "switch off the light",
        "switch the light off",
        "turn off the lamp",
    ],
}
DEFAULT_INTENTS_PATH = os.path.join(os.path.dirname(__file__), "intents.json")


def load_intent_examples(path=DEFAULT_INTENTS_PATH):
    if path and os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
            if isinstance(data, dict):
                cleaned = {}
                for key, phrases in data.items():
                    if not isinstance(phrases, list):
                        continue
                    cleaned_phrases = [str(p).strip() for p in phrases if str(p).strip()]
                    if cleaned_phrases:
                        cleaned[str(key)] = cleaned_phrases
                if cleaned:
                    return cleaned
        except Exception as exc:
            print(f"Failed to load intents from {path}: {exc}")
    return dict(DEFAULT_INTENTS)


def _to_vector(vec):
    if _HAS_NUMPY:
        return np.asarray(vec, dtype=np.float32).reshape(-1)
    return [float(x) for x in vec]


def _normalize(vec):
    if _HAS_NUMPY:
        denom = np.linalg.norm(vec)
        if denom == 0:
            return vec
        return vec / denom

    denom = math.sqrt(sum(v * v for v in vec))
    if denom == 0:
        return vec
    return [v / denom for v in vec]


def _mean(vectors):
    if _HAS_NUMPY:
        return np.mean(vectors, axis=0)
    length = len(vectors[0])
    sums = [0.0] * length
    for vec in vectors:
        for idx, val in enumerate(vec):
            sums[idx] += val
    return [val / len(vectors) for val in sums]


def _dot(a, b):
    if _HAS_NUMPY:
        return float(np.dot(a, b))
    return sum(x * y for x, y in zip(a, b))


class IntentRouter:
    def __init__(self, examples=None, examples_path=DEFAULT_INTENTS_PATH, threshold=DEFAULT_THRESHOLD):
        self.examples = examples if examples is not None else load_intent_examples(examples_path)
        self.threshold = threshold
        self._backend = None
        self._intent_vectors = None
        self._use_embeddings = True

        if SunriseBackend is None:
            self._use_embeddings = False
            print(f"Embedding backend unavailable: {_BACKEND_ERROR}")
            return

        try:
            self._backend = SunriseBackend()
        except Exception as exc:
            self._use_embeddings = False
            self._backend = None
            print(f"Embedding backend init failed: {exc}")

    def _embed(self, text):
        vec = self._backend.process(text)
        return _to_vector(vec)

    def _prepare_vectors(self):
        if not self._use_embeddings or not self._backend:
            return

        vectors = {}
        for intent, phrases in self.examples.items():
            phrase_vecs = []
            for phrase in phrases:
                try:
                    vec = self._embed(phrase)
                except Exception as exc:
                    print(f"Embedding failed for '{phrase}': {exc}")
                    self._use_embeddings = False
                    self._backend = None
                    return
                vec = _to_vector(vec)
                phrase_vecs.append(_normalize(vec))

            if phrase_vecs:
                mean_vec = _mean(phrase_vecs)
                vectors[intent] = _normalize(mean_vec)

        self._intent_vectors = vectors

    def _keyword_match(self, text):
        text_lower = text.lower()
        best_intent = None
        best_len = 0
        for intent, phrases in self.examples.items():
            for phrase in phrases:
                phrase_lower = phrase.lower()
                if phrase_lower and phrase_lower in text_lower:
                    if len(phrase_lower) > best_len:
                        best_len = len(phrase_lower)
                        best_intent = intent
        if best_intent:
            return best_intent, 1.0, "keyword"
        return None, 0.0, "keyword"

    def match(self, text):
        if not text:
            return None, 0.0, "none"

        if self._use_embeddings and self._intent_vectors is None:
            self._prepare_vectors()

        if self._use_embeddings and self._intent_vectors:
            try:
                vec = _normalize(_to_vector(self._embed(text)))
            except Exception as exc:
                print(f"Embedding failed for '{text}': {exc}")
                self._use_embeddings = False
                self._backend = None
                return self._keyword_match(text)

            best_intent = None
            best_score = -1.0
            for intent, proto in self._intent_vectors.items():
                score = _dot(vec, proto)
                if score > best_score:
                    best_score = score
                    best_intent = intent
            return best_intent, best_score, "embedding"

        return self._keyword_match(text)

    def handle(self, text, handlers):
        intent, score, method = self.match(text)
        if not intent:
            return None
        if method == "embedding" and score < self.threshold:
            return None

        handler = handlers.get(intent)
        if not handler:
            return None
        result = handler()
        return {
            "intent": intent,
            "score": score,
            "method": method,
            "result": result,
        }
