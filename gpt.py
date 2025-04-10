import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from queue import Queue
from threading import Thread
from tts import speak_stream

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tts_queue = Queue()
history = []
summary = ""
MAX_HISTORY_LEN = 10

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

async def summarize_old_history(old_history):
    summary_prompt = "다음 대화를 요약해줘:\n"
    for msg in old_history:
        summary_prompt += f"{msg['role']}: {msg['content']}\n"

    result = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "다음 대화 내용을 간결하고 핵심만 요약해줘."},
            {"role": "user", "content": summary_prompt}
        ]
    )
    return result.choices[0].message.content.strip()

async def query_gpt_stream(prompt):
    global summary, history

    print("🧠 GPT 스트리밍 응답 시작")

    history.append({"role": "user", "content": prompt})

    # 오래된 히스토리 요약
    if len(history) > MAX_HISTORY_LEN:
        old = history[:-MAX_HISTORY_LEN]
        history = history[-MAX_HISTORY_LEN:]
        summary = await summarize_old_history(old)

    # GPT 메시지 구성
    messages = [{"role": "system", "content": "너는 친절한 한국어 비서야. 짧고 간단하게 대답해줘"}]
    if summary:
        messages.append({"role": "system", "content": f"지금까지의 요약: {summary}"})
    messages.extend(history)

    stream = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True,
    )

    buffer = ""
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            piece = chunk.choices[0].delta.content
            print(piece, end="", flush=True)
            buffer += piece

            if any(p in piece for p in ".!?"):
                tts_queue.put(buffer.strip())
                buffer = ""

    if buffer.strip():
        tts_queue.put(buffer.strip())

    print("\n🧠 GPT 응답 완료")

    history.append({"role": "assistant", "content": buffer.strip()})

def shutdown_tts():
    tts_queue.put(None)
