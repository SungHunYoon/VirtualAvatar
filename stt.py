from collections import deque
import numpy as np
from faster_whisper import WhisperModel

class Whisper:
    def __init__(self, sample_rate=16000):
        self.model = WhisperModel("base", device="cpu", compute_type="int8")
        self.sample_rate = sample_rate
        self.buffer = []

    def add_chunk(self, chunk):
        self.buffer.extend(chunk.tolist())

    def transcribe_buffer(self):
        if len(self.buffer) < self.sample_rate * 0.5:
            return ""

        audio = np.array(self.buffer, dtype=np.float32)

        segments, _ = self.model.transcribe(audio, language="ko", beam_size=2)
        self.buffer.clear()
        return " ".join([seg.text.strip() for seg in segments])