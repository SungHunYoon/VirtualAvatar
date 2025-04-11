import asyncio
import subprocess
import numpy as np
import sounddevice as sd
from edge_tts import Communicate
from threading import Thread
from state import is_tts_playing
from websocket import send_mouth_signal

async def speak_stream(text):
    if not text.strip() or len(text.strip()) < 2:
        return

    communicate = Communicate(text=text, voice="ko-KR-SunHiNeural")

    # ffmpeg: MP3 → PCM 변환 (실시간 안정화 위해 -re, -bufsize 추가)
    ffmpeg = subprocess.Popen(
        [
            "ffmpeg", "-re", "-i", "pipe:0",
            "-f", "f32le", "-ar", "24000", "-ac", "1",
            "-bufsize", "64k", "pipe:1"
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )

    def audio_player():
        with sd.OutputStream(
            samplerate=24000,
            channels=1,
            dtype='float32',
            blocksize=1024,
            latency='high'  # 지지직 방지 목적
        ) as stream:
            while True:
                chunk = ffmpeg.stdout.read(9600)  # 100ms 분량
                if not chunk:
                    break

                audio = np.frombuffer(chunk, dtype=np.float32)
                stream.write(audio)

                rms = float(np.sqrt(np.mean(audio ** 2)))
                normalized = min(rms * 4, 1.0)

                try:
                    asyncio.run(send_mouth_signal(str(normalized)))
                except Exception as e:
                    print(f"[TTS Send Error] {e}")

    is_tts_playing.set(True)

    player_thread = Thread(target=audio_player, daemon=True)
    player_thread.start()

    try:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                ffmpeg.stdin.write(chunk["data"])
    except Exception as e:
        print(f"[TTS Stream Error] {e}")
    finally:
        ffmpeg.stdin.close()
        player_thread.join()
        ffmpeg.wait()

        await send_mouth_signal("0.0")
        is_tts_playing.set(False)
