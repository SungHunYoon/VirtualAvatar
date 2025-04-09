import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from tts import speak_stream

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

    text_accum = ""
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            text_piece = chunk.choices[0].delta.content
            print(text_piece, end="", flush=True)
            text_accum += text_piece
            await speak_stream(text_piece)
    print("\n🧠 GPT 응답 완료")
