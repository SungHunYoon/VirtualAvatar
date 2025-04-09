import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from queue import Queue
from threading import Thread
import asyncio
from tts import speak_stream

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tts_queue = Queue()

def tts_worker():
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    while True:
        text = tts_queue.get()
        if text is None:
            break
        if text.strip():
            try:
                loop.run_until_complete(speak_stream(text))
            except RuntimeError as e:
                print(f"[TTS Error] {e}")

Thread(target=tts_worker, daemon=True).start()

async def query_gpt_stream(prompt):
    print("🧠 GPT 스트리밍 응답 시작")
    stream = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 친절한 한국어 비서야. 짧고 간단하게 대답해줘"},
            {"role": "user", "content": prompt}
        ],
        stream=True,
    )

    buffer = ""
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            piece = chunk.choices[0].delta.content
            print(piece, end="", flush=True)
            buffer += piece

            if any(p in piece for p in ".!?") or len(buffer) > 20:
                tts_queue.put(buffer.strip())
                buffer = ""

    if buffer.strip():  # 마지막 남은 내용도 처리
        tts_queue.put(buffer.strip())

    print("\n🧠 GPT 응답 완료")

def shutdown_tts():
    tts_queue.put(None)
