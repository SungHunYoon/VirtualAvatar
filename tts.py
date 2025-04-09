import asyncio
import numpy as np
import sounddevice as sd
import subprocess
from edge_tts import Communicate

async def speak_stream(text):
    communicate = Communicate(text=text, voice="ko-KR-SunHiNeural")

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            mp3_data = chunk["data"]

            process = subprocess.Popen(
                ["ffmpeg", "-i", "pipe:0", "-f", "wav", "-ar", "24000", "-ac", "1", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            try:
                wav_data, _ = process.communicate(mp3_data, timeout=5)
                audio_array = np.frombuffer(wav_data, dtype=np.int16).astype(np.float32) / 32768.0
                sd.play(audio_array, samplerate=24000)
                sd.wait()
            except subprocess.TimeoutExpired:
                process.kill()
