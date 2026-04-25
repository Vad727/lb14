from pathlib import Path
import wave
import math
import struct

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "test_inputs"
INPUT_DIR.mkdir(parents=True, exist_ok=True)

def create_wav(path: Path, duration_sec: float, freq: float = 440.0, sample_rate: int = 16000):
    n_samples = int(duration_sec * sample_rate)
    with wave.open(str(path), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        for i in range(n_samples):
            value = int(12000 * math.sin(2 * math.pi * freq * i / sample_rate))
            wav.writeframes(struct.pack("<h", value))

create_wav(INPUT_DIR / "normal.wav", duration_sec=1.5)
create_wav(INPUT_DIR / "short.wav", duration_sec=0.05)

(INPUT_DIR / "empty.wav").write_bytes(b"")
(INPUT_DIR / "broken.wav").write_bytes(b"RIFF0000WAVEbroken_data")
(INPUT_DIR / "not_audio.wav").write_text("Это не аудиофайл, а обычный текст.", encoding="utf-8")

print("Тестовые файлы созданы в:", INPUT_DIR)