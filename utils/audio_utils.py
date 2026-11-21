"""
AudioStudio IA - Utilitários de Áudio e Formatação
===================================================
Funções auxiliares para manipulação de arquivos de áudio, medição precisa de duração,
geração de legendas SRT, conversão de timestamps e fallback senoidal seguro.
"""

import os
import math
import wave
import struct
import shutil
import subprocess
from pathlib import Path
from typing import List

# Extensões comuns de mídia compatíveis com Whisper / ffmpeg
SUPPORTED_AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".mp4", ".flac", ".ogg", ".aac", ".wma", ".mov", ".mkv"
}


def format_time(seconds: float) -> str:
    """Converte segundos em formato MM:SS para exibição amigável em logs e cronômetros."""
    mins, secs = divmod(int(max(0.0, seconds)), 60)
    return f"{mins:02d}:{secs:02d}"


def format_srt_timestamp(seconds: float) -> str:
    """Converte segundos para o formato padrão de legendas SRT: HH:MM:SS,mmm."""
    seconds = max(0.0, seconds)
    millis = int((seconds - int(seconds)) * 1000)
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def get_audio_duration(file_path: str) -> float:
    """
    Obtém a duração exata do arquivo de áudio em segundos.
    Usa ffprobe (instalado no sistema) com fallback para wave e estimativa por bitrate.
    """
    if not os.path.exists(file_path):
        return 10.0

    # 1. Tenta usar ffprobe (suporta MP3, WAV, M4A, MP4, FLAC, OGG, WMA, etc.)
    ffprobe_bin = shutil.which("ffprobe") or r"C:\ffmpeg\ffprobe.exe"
    if ffprobe_bin and (shutil.which("ffprobe") or os.path.exists(ffprobe_bin)):
        try:
            cmd = [
                ffprobe_bin,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            val = float(res.stdout.strip())
            if val > 0.05:
                return val
        except Exception:
            pass

    # 2. Tenta ler via biblioteca padrão wave (para arquivos .wav)
    try:
        with wave.open(file_path, "r") as w:
            frames = w.getnframes()
            rate = w.getframerate()
            if rate > 0:
                return float(frames) / float(rate)
    except Exception:
        pass

    # 3. Estimativa proporcional segura por tamanho de arquivo (~128 kbps = 16 KB/s)
    try:
        size_bytes = os.path.getsize(file_path)
        est = size_bytes / 16000.0
        return max(5.0, est)
    except Exception:
        return 30.0


def scan_audio_files(directory_path: str) -> List[str]:
    """Varre recursivamente uma pasta e retorna todos os arquivos de áudio suportados."""
    found_files = []
    if not os.path.exists(directory_path):
        return found_files

    for root, _, files in os.walk(directory_path):
        for f in files:
            if Path(f).suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS:
                found_files.append(os.path.join(root, f))
    return sorted(found_files)


def generate_demo_tone(file_path: str, duration: float = 2.0, frequency: float = 440.0) -> bool:
    """
    Gera um tom senoidal WAV puro e suave (16-bit Mono, 22.05 kHz) sem dependências externas.
    Utilizado como fallback seguro de áudio quando nenhuma biblioteca externa de TTS está instalada.
    """
    try:
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        with wave.open(file_path, "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            frames = bytearray()
            for i in range(num_samples):
                t = float(i) / sample_rate
                envelope = math.sin(math.pi * t / duration)
                value = int(32767.0 * 0.3 * envelope * math.sin(2.0 * math.pi * frequency * t))
                frames.extend(struct.pack("<h", max(-32768, min(32767, value))))
            wav_file.writeframes(frames)
        return True
    except Exception as e:
        print(f"[AudioUtils] Falha ao sintetizar tom senoidal: {e}")
        return False
