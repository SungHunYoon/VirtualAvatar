# 🎙️ Virtual Avatar Assistant

발화 감지 → 음성 인식(STT) → GPT 응답 → 음성 합성(TTS) → 아바타 립싱크

**가상 아바타 음성 대화 시스템**을 구현

---

## 🧩 주요 구성 요소

| 모듈 | 설명 |
|------|------|
| `vad.py` | Silero VAD로 발화 구간 감지 |
| `stt.py` | Google STT로 음성 인식 |
| `gpt.py` | OpenAI GPT-4o API로 대화 응답 생성 |
| `tts.py` | Microsoft Edge TTS로 음성 생성 |
| `websocket.py` | 입 모양 제어용 WebSocket 서버 |
| `main.py` | 전체 파이프라인 제어 |
| `state.py` | TTS 재생 상태 동기화 관리 |


---

## ⚙️ 전체 시스템 흐름

1. **마이크 입력 감지**: Silero VAD가 발화를 감지하면
2. **음성 인식 (STT)**: Faster-Whisper 또는 Google STT로 음성을 텍스트로 변환
3. **텍스트 응답 생성**: GPT-4o가 응답을 생성
4. **음성 합성 (TTS)**: Microsoft Edge-TTS가 응답을 음성으로 변환
5. **아바타 립싱크**: 웹 아바타가 WebSocket을 통해 입을 움직임

---

## 🛠️ 설치 방법

### 1. Python 의존성 설치

```bash
pip install torch numpy sounddevice openai edge-tts python-dotenv torchaudio websockets google-cloud-speech
```

### 2. ffmpeg 설치

- Mac: `brew install ffmpeg`
- Ubuntu: `sudo apt install ffmpeg`
- Windows: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

---

## 🔐 환경 변수 설정

`.env` 파일을 프로젝트 루트에 생성하고 아래 항목을 설정하세요:

```env
OPENAI_API_KEY=sk-...
GOOGLE_APPLICATION_CREDENTIALS=./your-google-credentials.json
```

> ⚠️ `GOOGLE_APPLICATION_CREDENTIALS`는 Google Cloud에서 발급한 STT용 서비스 계정 키 경로입니다.

---

### 1. WebSocket 서버 실행 (입모양 연동용)

```bash
python -m http.server 5500
```

### 2. 메인 프로그램 실행

```bash
python main.py
```

> 둘 다 동시에 실행되어야 **아바타 입 모양 제어까지 정상 작동**합니다.

### 3. localhost:5500으로 접속

---

## 📄 참고 모델
- VAD: https://github.com/snakers4/silero-vad
- STT: https://cloud.google.com/speech-to-text
- LLM: https://platform.openai.com/docs/models/gpt-4o
- TTS: https://github.com/rany2/edge-tts

---

## 🖼️ Live2D 모델 참고

- **Live2D Cubism SDK**: https://www.live2d.com/en/download/cubism-sdk/
- **pixi-live2d-display (WebGL용 라이브러리)**: https://github.com/guansss/pixi-live2d-display

모델로는 Live2D 공식 무료 배포 모델인 `Hiyori`를 사용하며, 관련 리소스는 프로젝트의 `hiyori/` 디렉토리에 포함되어 있습니다.

`.model3.json` 파일을 `Live2DModel.from()`에 로드하면 PIXI.js를 통해 웹 브라우저 상에 아바타가 렌더링됩니다.