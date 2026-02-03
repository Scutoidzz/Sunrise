import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer
import requests
import subprocess
import re
import sys

class SunriseBackend():
    def __init__(self):
        # Tools are optional; avoid NameError if they are not defined yet.
        try:
            self.tools = [
                dim_screen,
                brighten_screen,
                turn_on_bluetooth,
                turn_off_bluetooth,
                knowledge_search,
                what_can_you_do,
                play_video,
                play_song,
            ]
        except NameError:
            self.tools = []

        self.path_to_model = "starry/model.onnx"

    def load_model(self):
        self.session = ort.InferenceSession(self.path_to_model)
        try:
            self.tokenizer = Tokenizer.from_pretrained("starry/tokenizer.json")
        except Exception:
            self.tokenizer = Tokenizer.from_file("starry/tokenizer.json")

    def process(self, text):
        return self.send_to_embedding(text)

    def send_to_embedding(self, text):
        if not hasattr(self, "session") or not hasattr(self, "tokenizer"):
            self.load_model()

        if text is None:
            text = ""
        if not isinstance(text, str):
            text = str(text)

        encoding = self.tokenizer.encode(text)
        ids = list(encoding.ids)
        mask = list(encoding.attention_mask) if encoding.attention_mask else [1] * len(ids)
        types = list(encoding.type_ids) if encoding.type_ids else [0] * len(ids)

        target_len = None
        for input_meta in self.session.get_inputs():
            shape = input_meta.shape
            if shape and isinstance(shape[-1], int):
                target_len = shape[-1]
                break

        if target_len:
            pad_id = self.tokenizer.token_to_id("[PAD]")
            if pad_id is None:
                pad_id = 0

            if len(ids) > target_len:
                ids = ids[:target_len]
                mask = mask[:target_len]
                types = types[:target_len]
            elif len(ids) < target_len:
                pad_count = target_len - len(ids)
                ids = ids + [pad_id] * pad_count
                mask = mask + [0] * pad_count
                types = types + [0] * pad_count

        input_ids = np.asarray([ids], dtype=np.int64)
        attention_mask = np.asarray([mask], dtype=np.int64)
        token_type_ids = np.asarray([types], dtype=np.int64)

        def _dtype_from_onnx(onnx_type):
            if "int32" in onnx_type:
                return np.int32
            if "int64" in onnx_type:
                return np.int64
            if "float16" in onnx_type:
                return np.float16
            if "float" in onnx_type:
                return np.float32
            return np.int64

        inputs = {}
        input_metas = self.session.get_inputs()
        if len(input_metas) == 1:
            meta = input_metas[0]
            inputs[meta.name] = input_ids.astype(_dtype_from_onnx(meta.type), copy=False)
        else:
            for meta in input_metas:
                name = meta.name.lower()
                if "input" in name and "id" in name:
                    arr = input_ids
                elif "attention" in name or "mask" in name:
                    arr = attention_mask
                elif "token_type" in name or "type_id" in name or "segment" in name:
                    arr = token_type_ids
                else:
                    arr = input_ids
                inputs[meta.name] = arr.astype(_dtype_from_onnx(meta.type), copy=False)

        outputs = self.session.run(None, inputs)

        embedding = None
        for out in outputs:
            if isinstance(out, np.ndarray) and out.ndim == 2:
                embedding = out
                break
        if embedding is None:
            for out in outputs:
                if isinstance(out, np.ndarray) and out.ndim == 3:
                    mask_f = attention_mask.astype(np.float32)
                    mask_f = np.expand_dims(mask_f, axis=-1)
                    summed = (out * mask_f).sum(axis=1)
                    denom = np.clip(mask_f.sum(axis=1), 1e-9, None)
                    embedding = summed / denom
                    break
        if embedding is None:
            embedding = outputs[0]

        if isinstance(embedding, np.ndarray) and embedding.ndim >= 1:
            embedding = embedding[0]
        return embedding.tolist() if hasattr(embedding, "tolist") else embedding
        
