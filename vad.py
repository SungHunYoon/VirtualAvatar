import torch
import numpy as np

class SileroVAD:
    def __init__(self, sample_rate=16000, chunk_size=512, threshold=0.5):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.threshold = threshold
        self.model, _ = torch.hub.load('snakers4/silero-vad', 'silero_vad', trust_repo=True)
        self.model.eval()

    def is_speech(self, chunk: np.ndarray) -> bool:
        if len(chunk) != self.chunk_size:
            return False
        with torch.no_grad():
            x = torch.from_numpy(chunk).float().unsqueeze(0)
            prob = self.model(x, self.sample_rate).item()
        return prob > self.threshold
