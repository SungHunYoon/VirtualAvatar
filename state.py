# state.py
from threading import Lock

class TTSState:
    def __init__(self):
        self._flag = False
        self._lock = Lock()

    def set(self, value: bool):
        with self._lock:
            self._flag = value

    def get(self) -> bool:
        with self._lock:
            return self._flag

is_tts_playing = TTSState()
