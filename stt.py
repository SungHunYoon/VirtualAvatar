import os
from dotenv import load_dotenv
import numpy as np
from google.cloud import speech

class GoogleSTT:
    def __init__(self, sample_rate=16000):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        self.sample_rate = sample_rate
        self.client = speech.SpeechClient()
        self.buffer = []

    def add_chunk(self, chunk):
        # float32 → int16 변환 후 PCM bytes로 저장
        int_chunk = (np.array(chunk) * 32767).astype(np.int16)
        self.buffer.extend(int_chunk.tobytes())

    def transcribe_buffer(self):
        if len(self.buffer) < int(self.sample_rate * 0.5 * 2):  # 0.5초 분량
            return ""

        audio_bytes = bytes(self.buffer)
        self.buffer.clear()

        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.sample_rate,
            language_code="ko-KR",
        )

        try:
            response = self.client.recognize(config=config, audio=audio)
            return " ".join([result.alternatives[0].transcript for result in response.results])
        except Exception as e:
            print(f"[Google STT Error] {e}")
            return ""
