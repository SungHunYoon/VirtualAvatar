# 🎙️ Virtual Avatar Assistant

Silero 기반 VAD, Whisper 기반 STT, GPT-4o 기반 대화 생성, edge-tts를 활용하여 **가상 아바타 음성 대화 시스템**을 구현

---

## 🧩 주요 구성 요소

| 모듈 | 설명 |
|------|------|
| `vad.py` | Silero VAD 모델로 발화 구간을 감지 |
| `stt.py` | Faster-Whisper 모델을 사용해 실시간 음성 인식 |
| `gpt.py` | GPT-4o API로 텍스트에 대한 응답을 생성 |
| `tts.py` | edge-tts를 활용하여 실시간 음성 출력 |
| `main.py` | 위 모든 모듈을 통합하여 실시간 대화 흐름을 제어 |

---

## 🛠️ 설치 및 실행

### 1. 의존성 설치
```bash
pip install torch numpy sounddevice openai faster-whisper edge-tts python-dotenv torchaudio
```

### 2. OpenAI API 키 설정
`.env` 파일 내 다음 항목을 본인의 키로 설정:
```text
OPENAI_API_KEY = "your-api-key"
```

### 3. 실행
```bash
python main.py
```

---

## ⚙️ 동작 방식

1. 사용자가 마이크에 대고 말을 시작하면 Silero VAD로 음성 감지
2. 감지된 음성은 Whisper에 전달
3. Whisper가 텍스트로 변환
4. 해당 텍스트는 GPT-4o API에 전달되어 응답을 생성
5. edge-tts를 통해 다시 음성으로 출력

---

## 📄 참고 모델
- VAD: https://github.com/snakers4/silero-vad
- STT: https://github.com/SYSTRAN/faster-whisper
- TTS: https://github.com/rany2/edge-tts
- LLM: OpenAI GPT-4o API
