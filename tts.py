import numpy as np
import sounddevice as sd
import asyncio
from google.cloud import texttospeech_v1beta1 as texttospeech
from websocket import send_mouth_signal
from state import is_tts_playing

client = texttospeech.TextToSpeechClient()

async def google_tts_stream_from_gpt_chunks(text: str):
    loop = asyncio.get_event_loop()
    is_tts_playing.set(True)

    with sd.RawOutputStream(
        samplerate=24000,
        channels=1,
        dtype='int16',
        blocksize=4096,
        latency='high'
    ) as stream:
        streaming_config = texttospeech.StreamingSynthesizeConfig(
            voice=texttospeech.VoiceSelectionParams(
                name="ko-KR-Chirp3-HD-Charon",
                language_code="ko-KR"
            ),
            streaming_audio_config=texttospeech.StreamingAudioConfig(
                audio_encoding=texttospeech.AudioEncoding.PCM,
                sample_rate_hertz=24000
            )
        )

        def request_generator():
            yield texttospeech.StreamingSynthesizeRequest(streaming_config=streaming_config)
            yield texttospeech.StreamingSynthesizeRequest(
                input=texttospeech.StreamingSynthesisInput(text=text)
            )

        responses = client.streaming_synthesize(requests=request_generator())

        prev_rms = 0.0  # 이동 평균용 전역 변수

        for response in responses:
            if response.audio_content:
                stream.write(response.audio_content)

                samples = np.frombuffer(response.audio_content, dtype=np.int16).astype(np.float32)
                rms = float(np.sqrt(np.mean(samples**2)))

                # 🎯 이동 평균 적용
                alpha = 0.2
                prev_rms = (1 - alpha) * prev_rms + alpha * rms

                normalized = min(prev_rms / 3000.0, 1.0)
                if normalized < 0.02:
                    normalized = 0.0

                try:
                    await send_mouth_signal(str(normalized))
                except Exception as e:
                    print(f"[Mouth Signal Error] {e}")

        stream.write(b'\x00' * 4800)
        stream.stop()
        stream.close()
        await asyncio.sleep(0.4)
        await send_mouth_signal("0.0")
        is_tts_playing.set(False)