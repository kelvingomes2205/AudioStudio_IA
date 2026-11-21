"""
AudioStudio IA - Janela Principal e Gerenciador de Ciclo de Vida
==================================================================
Janela raiz CTk com arquitetura responsiva, alternância de abas
(Texto para Áudio, Áudio para Texto e Configurações) e encerramento seguro.
"""

from tkinter import messagebox
import customtkinter as ctk

from ui.theme import COLORS
from ui.sidebar import SidebarFrame
from ui.tts_view import TTSView
from ui.whisper_view import WhisperView
from ui.settings_view import SettingsView
from core.tts_engine import TTSEngine

# Configuração Global do CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AudioStudioApp(ctk.CTk):
    """Janela principal da aplicação AudioStudio IA."""

    def __init__(self):
        super().__init__()

        # Metadados e Geometria da Janela
        self.title("AudioStudio IA — Estúdio de Voz & Transcrição")
        self.geometry("1220x760")
        self.minsize(1050, 660)
        self.configure(fg_color=COLORS["bg_dark"])

        # Inicialização dos Motores Core
        self.tts_engine = TTSEngine()

        # Interceptação de Fechamento de Janela
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._is_closing = False

        # Configuração do Grid Raiz (Coluna 0: Sidebar estática | Coluna 1: Conteúdo expansível)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._build_layout()

    def _build_layout(self):
        """Monta os containers principais da aplicação."""
        # Barra lateral (largura 275 para acomodar perfeitamente os botões)
        self.sidebar = SidebarFrame(self, on_navigate_callback=self.navigate_to_tab, width=275)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Container principal de visualização
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Inicialização das Views (Abas)
        self.view_tts = TTSView(self.main_container, self.tts_engine)
        self.view_whisper = WhisperView(self.main_container)
        self.view_settings = SettingsView(self.main_container)

        # Exibe a aba inicial (Texto para Áudio)
        self.current_view = None
        self.navigate_to_tab("tts")

    def navigate_to_tab(self, tab_id: str):
        """Alterna suavemente a view exibida no container principal."""
        if self.current_view:
            self.current_view.grid_forget()

        if tab_id == "tts":
            self.view_tts.grid(row=0, column=0, sticky="nsew")
            self.current_view = self.view_tts
        elif tab_id in ["whisper", "stt"]:
            self.view_whisper.grid(row=0, column=0, sticky="nsew")
            self.current_view = self.view_whisper
        elif tab_id == "settings":
            self.view_settings.grid(row=0, column=0, sticky="nsew")
            self.current_view = self.view_settings

    def on_closing(self):
        """Trata o fechamento seguro da janela e cancela processos pendentes."""
        if self._is_closing:
            return

        # Verifica se o Whisper está em execução
        if hasattr(self, "view_whisper") and self.view_whisper.is_running:
            if not messagebox.askyesno("Confirmar Saída", "Uma transcrição está em andamento. Deseja cancelar e fechar?"):
                return
            self.view_whisper.stop_event.set()

        self._is_closing = True
        self.destroy()
