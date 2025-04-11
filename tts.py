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

    # ffmpeg: MP3 → PCM 실시간 스트리밍
    ffmpeg = subprocess.Popen(
        ["ffmpeg", "-i", "pipe:0", "-f", "f32le", "-ar", "24000", "-ac", "1", "pipe:1"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )

    def audio_player():
        with sd.OutputStream(samplerate=24000, channels=1, dtype='float32') as stream:
            while True:
                chunk = ffmpeg.stdout.read(9600)  # 100ms 분량
                if not chunk:
                    break

                # 오디오 재생
                audio = np.frombuffer(chunk, dtype=np.float32)
                stream.write(audio)

                # 📈 볼륨(RMS) 계산
                rms = float(np.sqrt(np.mean(audio ** 2)))
                normalized = min(rms * 4, 1.0)  # 보정값 2배

                # 🧠 입 모양 WebSocket 전송 (문자열로 변환)
                try:
                    asyncio.run(send_mouth_signal(str(normalized)))
                except Exception as e:
                    print(f"[TTS Send Error] {e}")

    is_tts_playing.set(True)

    player_thread = Thread(target=audio_player, daemon=True)
    player_thread.start()

    try:
        # edge-tts로 TTS 오디오 스트리밍 받기
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                ffmpeg.stdin.write(chunk["data"])
    except Exception as e:
        print(f"[TTS Stream Error] {e}")
    finally:
        ffmpeg.stdin.close()
        player_thread.join()
        ffmpeg.wait()

        # 🔴 입 닫기
        await send_mouth_signal("0.0")
        is_tts_playing.set(False)
