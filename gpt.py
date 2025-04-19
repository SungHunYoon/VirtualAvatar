import asyncio
import threading
import os
from queue import Queue
from openai import AsyncOpenAI
from dotenv import load_dotenv
from tts import google_tts_stream_from_gpt_chunks
from state import is_tts_playing

load_dotenv()
gpt_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tts_queue = Queue()

# 전역 히스토리
history = [{"role": "system", "content": "너는 친절한 한국어 비서야. 짧고 간단하게 대답해줘."}]
MAX_HISTORY_LEN = 10

# 백그라운드 TTS 쓰레드 실행

def tts_worker():
    while True:
        text = tts_queue.get()
        if text is None:
            break
        asyncio.run(google_tts_stream_from_gpt_chunks(text))

threading.Thread(target=tts_worker, daemon=True).start()

# GPT 스트리밍 응답 후 전체 텍스트를 TTS 큐에 전달
async def query_gpt_stream(prompt: str):
    global history

    history.append({"role": "user", "content": prompt})

    while len(history) > MAX_HISTORY_LEN * 2 + 1:
        del history[1:3]

    stream = await gpt_client.chat.completions.create(
        model="gpt-4o",
        messages=history,
        stream=True,
    )

    print("\n🧠 GPT 스트리밍 응답 시작")
    full_response = ""
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            piece = chunk.choices[0].delta.content
            print(piece, end="", flush=True)
            full_response += piece

    print("\n🧠 GPT 응답 완료")

    if full_response.strip():
        history.append({"role": "assistant", "content": full_response.strip()})
        tts_queue.put(full_response.strip())