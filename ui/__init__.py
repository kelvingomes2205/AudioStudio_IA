"""Pacote de Interface Visual (UI) do AudioStudio IA."""

from ui.theme import COLORS, FONTS
from ui.sidebar import SidebarFrame
from ui.tts_view import TTSView
from ui.whisper_view import WhisperView
from ui.wave_visualizer import WaveVisualizer
from ui.settings_view import SettingsView
from ui.app import AudioStudioApp

__all__ = [
    "COLORS",
    "FONTS",
    "SidebarFrame",
    "TTSView",
    "WhisperView",
    "WaveVisualizer",
    "SettingsView",
    "AudioStudioApp"
]
