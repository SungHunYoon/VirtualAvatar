import asyncio
import subprocess
import numpy as np
import sounddevice as sd
from edge_tts import Communicate
from threading import Thread

async def speak_stream(text):
    if not text.strip() or len(text.strip()) < 2:
        return

    communicate = Communicate(text=text, voice="ko-KR-SunHiNeural")

    # ffmpeg: MP3 → PCM 스트리밍
    ffmpeg = subprocess.Popen(
        ["ffmpeg", "-i", "pipe:0", "-f", "f32le", "-ar", "24000", "-ac", "1", "pipe:1"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )

    def audio_player():
        with sd.OutputStream(samplerate=24000, channels=1, dtype='float32') as stream:
            while True:
                chunk = ffmpeg.stdout.read(24000 * 4 // 10)
                if not chunk:
                    break
                audio = np.frombuffer(chunk, dtype=np.float32)
                stream.write(audio)

    # 🎯 여기를 `await` 하지 않도록 변경!
    player_thread = Thread(target=audio_player, daemon=True)
    player_thread.start()

    try:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                ffmpeg.stdin.write(chunk["data"])
    except Exception as e:
        print(f"[TTS Stream Error] {e}")

    ffmpeg.stdin.close()
    player_thread.join()
    ffmpeg.wait()
