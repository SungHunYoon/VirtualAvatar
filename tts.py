import asyncio
import sounddevice as sd
import numpy as np
import edge_tts

async def stream_tts(text):
    tts = edge_tts.Communicate(text=text, voice="ko-KR-SunHiNeural")
    async for chunk in tts.stream():
        if chunk["type"] == "audio":
            audio = np.frombuffer(chunk["data"], dtype=np.int16)
            sd.play(audio, samplerate=24000)
            sd.wait()
