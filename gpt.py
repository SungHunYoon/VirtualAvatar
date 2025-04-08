import openai
from dotenv import load_dotenv
import os
from tts import stream_tts

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

async def query_gpt_stream(text):
    print(f"\n🤖 GPT: {text}")
    stream = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "너는 친근하고 똑똑한 한국어 음성 기반 대화 비서야. 짧고 자연스럽게 대답해줘."},
            {"role": "user", "content": text}
        ],
        stream=True
    )

    buffer = ""
    for chunk in stream:
        content = chunk['choices'][0]['delta'].get("content", "")
        print(content, end="", flush=True)
        buffer += content
        if buffer.endswith("다.") or buffer.endswith("."):
            await stream_tts(buffer)
            buffer = ""
    if buffer:
        await stream_tts(buffer)
