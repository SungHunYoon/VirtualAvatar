import sounddevice as sd
import queue
import asyncio
import numpy as np
import collections
import threading
import http.server
import socketserver

from vad import SileroVAD
from stt import GoogleSTT
from gpt import query_gpt_stream
from state import is_tts_playing
from websocket import start_ws_server

# 📦 웹서버 자동 실행
def start_web_server():
    PORT = 5500
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"🌐 HTTP 서버 실행 중: http://localhost:{PORT}")
        httpd.serve_forever()

# ✅ 백그라운드 웹 서버 실행
threading.Thread(target=start_web_server, daemon=True).start()

vad = SileroVAD()
stt = GoogleSTT()
audio_queue = queue.Queue()

recording = False
silence_counter = 0
SILENCE_LIMIT = 12
ROLLING_BUFFER_LIMIT = 48
rolling_buffer = collections.deque(maxlen=ROLLING_BUFFER_LIMIT)

def audio_callback(indata, frames, time_info, status):
    chunk = indata[:, 0].copy()
    audio_queue.put(chunk)

async def main():
    global recording, silence_counter
    await start_ws_server()
    print("🟢 시스템 시작")
    with sd.InputStream(
        samplerate=16000,
        channels=1,
        blocksize=512,
        dtype='float32',
        callback=audio_callback
    ):
        while True:
            if is_tts_playing.get():
                rolling_buffer.clear()
                while not audio_queue.empty():
                    audio_queue.get_nowait()
                continue

            chunk = audio_queue.get()
            rolling_buffer.append(chunk)

            if vad.is_speech(chunk):
                if not recording:
                    print("🎤 발화 시작")
                    recording = True
                    for prev_chunk in rolling_buffer:
                        stt.add_chunk(prev_chunk)
                silence_counter = 0
                stt.add_chunk(chunk)
            elif recording:
                silence_counter += 1
                if silence_counter >= SILENCE_LIMIT:
                    print("🛑 발화 종료")
                    result = stt.transcribe_buffer()
                    if result:
                        print(f"🗣️ 텍스트 인식 : {result}\n")
                        await query_gpt_stream(result)
                    recording = False
                    silence_counter = 0

if __name__ == "__main__":
    asyncio.run(main())
