import sys
import os
import subprocess
import warnings
warnings.filterwarnings("ignore")

import imageio_ffmpeg
from faster_whisper import WhisperModel

MODEL_SIZE = "tiny"
model = None

def get_model():
    global model
    if model is None:
        model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return model

def convert_to_wav(input_path):
    output_wav = input_path + ".wav"
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, "-y", "-i", input_path,
        "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
        output_wav
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return output_wav

def transcribe(audio_path):
    wav_path = None
    try:
        if not audio_path.endswith(".wav"):
            wav_path = convert_to_wav(audio_path)
            target = wav_path
        else:
            target = audio_path

        m = get_model()
        segments, info = m.transcribe(target, beam_size=5, language="pt")
        text = " ".join([seg.text for seg in segments]).strip()
        return text
    finally:
        if wav_path and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except Exception:
                pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        if os.path.exists(audio_file):
            print(transcribe(audio_file))
        else:
            print("File not found:", audio_file)
    else:
        print("Ready for transcription")
