"""
AudioStudio IA - Motor de Síntese de Voz (TTS)
================================================
Encapsulamento do motor de conversão de texto para fala (Text-to-Speech)
utilizando pyttsx3 com suporte a vozes instaladas, ajuste de velocidade,
volume e fallback seguro de áudio.
"""

import os
import shutil
from typing import List, Dict, Any, Optional
from utils.audio_utils import generate_demo_tone


class TTSEngine:
    """Gerenciador do motor de síntese de voz (TTS)."""

    def __init__(self):
        self._engine = None
        self._backend_type = "fallback"
        self._init_engine()

    def _init_engine(self):
        """Inicializa a biblioteca pyttsx3 se disponível no ambiente."""
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._backend_type = "pyttsx3"
        except Exception:
            self._backend_type = "fallback"

    @property
    def backend_type(self) -> str:
        """Retorna o tipo de motor ativo ('pyttsx3' ou 'fallback')."""
        return self._backend_type

    def get_available_voices(self) -> List[Dict[str, str]]:
        """Retorna catálogo de vozes configuradas para a interface."""
        voices = [
            {"id": "pt_br_antonio", "label": "Voz Masculina (Antônio - Padrão PT-BR)"},
            {"id": "pt_br_francisca", "label": "Voz Feminina (Francisca - PT-BR)"},
            {"id": "pt_br_leticia", "label": "Voz Feminina (Letícia - Natural PT-BR)"},
            {"id": "en_us_brian", "label": "Voz Masculina (Brian - EN-US)"},
            {"id": "en_us_emma", "label": "Voz Feminina (Emma - EN-US)"}
        ]
        return voices

    def generate_speech(
        self,
        text: str,
        output_path: str,
        voice_id: str,
        rate_factor: float = 1.0,
        volume: float = 1.0
    ) -> bool:
        """
        Gera arquivo de áudio narrado a partir do texto fornecido.
        Salva no caminho output_path (.wav ou .mp3).
        """
        clean_text = text.strip()
        if not clean_text:
            return False

        if self._backend_type == "pyttsx3" and self._engine:
            try:
                # Taxa base: 175 wpm * multiplicador
                self._engine.setProperty('rate', int(175 * rate_factor))
                self._engine.setProperty('volume', min(1.0, max(0.0, volume)))

                # Seleção de voz do sistema
                sys_voices = self._engine.getProperty('voices')
                if sys_voices:
                    is_female = any(name in voice_id for name in ["francisca", "leticia", "emma", "fem"])
                    matched = False
                    for v in sys_voices:
                        v_name = v.name.lower()
                        v_id = v.id.lower()
                        if is_female and any(k in v_name or k in v_id for k in ["maria", "francisca", "zira", "female"]):
                            self._engine.setProperty('voice', v.id)
                            matched = True
                            break
                        elif not is_female and any(k in v_name or k in v_id for k in ["antonio", "david", "helio", "male"]):
                            self._engine.setProperty('voice', v.id)
                            matched = True
                            break
                    if not matched and sys_voices:
                        self._engine.setProperty('voice', sys_voices[0].id)

                # Salva em arquivo
                temp_wav = output_path if output_path.lower().endswith(".wav") else output_path + ".wav"
                self._engine.save_to_file(clean_text, temp_wav)
                self._engine.runAndWait()

                if temp_wav != output_path and os.path.exists(temp_wav):
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    shutil.move(temp_wav, output_path)
                return True
            except Exception as e:
                print(f"[TTSEngine] Erro na síntese com pyttsx3 ({e}). Recorrendo ao fallback seguro.")

        # Fallback senoidal para teste caso biblioteca de síntese não esteja instalada
        return generate_demo_tone(output_path, duration=2.5)

    @staticmethod
    def play_audio(file_path: str):
        """Reproduz arquivo de áudio de forma não-bloqueante no Windows."""
        if not os.path.exists(file_path):
            return
        try:
            import winsound
            winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"[TTSEngine] Aviso ao reproduzir áudio: {e}")
