import sounddevice as sd
import queue
import asyncio
import numpy as np
import collections
from vad import SileroVAD
from stt import Whisper
from gpt import query_gpt_stream

vad = SileroVAD()
stt = Whisper()
audio_queue = queue.Queue()

recording = False
silence_counter = 0
SILENCE_LIMIT = 12  # 약 384ms
ROLLING_BUFFER_LIMIT = 48  # 약 1.5초 분량
rolling_buffer = collections.deque(maxlen=ROLLING_BUFFER_LIMIT)

def audio_callback(indata, frames, time_info, status):
    chunk = indata[:, 0].copy()
    audio_queue.put(chunk)

async def main():
    global recording, silence_counter
    print("🟢 시스템 시작")
    with sd.InputStream(
        samplerate=16000,
        channels=1,
        blocksize=512,
        dtype='float32',
        callback=audio_callback
    ):
        while True:
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
                        print(f"🗣️ 위스퍼 인식 : {result}\n")
                    recording = False
                    silence_counter = 0

if __name__ == "__main__":
    asyncio.run(main())
