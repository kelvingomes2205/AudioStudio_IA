"""
AudioStudio IA - Barra Lateral de Navegação (Design Atualizado)
==================================================================
Barra lateral com as abas expressas em português claro:
[ Texto para Áudio ] e [ Áudio para Texto ], além das configurações integradas.
"""

from typing import Callable
import customtkinter as ctk
from ui.theme import COLORS


class SidebarFrame(ctk.CTkFrame):
    """Barra lateral moderna com estilo Midnight Glassmorphism."""

    def __init__(self, master, on_navigate_callback: Callable[[str], None], width: int = 275):
        super().__init__(master, width=width, corner_radius=0, fg_color=COLORS["sidebar_bg"])
        self.on_navigate = on_navigate_callback
        self.active_tab = "tts"

        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_widgets()

    def _build_widgets(self):
        # 1. Cabeçalho / Branding
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(24, 16), sticky="w")

        self.logo_label = ctk.CTkLabel(
            header_frame,
            text="🎧 AudioStudio IA",
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.logo_label.pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Estúdio Unificado de Voz & IA",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"]
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))

        # 2. Seletor de Modo Principal [ Texto para Áudio ] | [ Áudio para Texto ]
        self.pill_container = ctk.CTkFrame(
            self,
            fg_color="#0A0E17",
            corner_radius=12,
            border_width=1,
            border_color=COLORS["card_border"]
        )
        self.pill_container.grid(row=1, column=0, padx=14, pady=(0, 20), sticky="ew")
        self.pill_container.grid_columnconfigure((0, 1), weight=1)

        # Botão 1: Texto para Áudio (TTS)
        self.btn_pill_tts = ctk.CTkButton(
            self.pill_container,
            text="Texto p/ Áudio",
            height=38,
            corner_radius=9,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#1B253D",
            border_width=1,
            border_color=COLORS["neon_blue"],
            text_color=COLORS["text_primary"],
            hover_color="#223050",
            command=lambda: self.select_tab("tts")
        )
        self.btn_pill_tts.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        # Botão 2: Áudio para Texto (Whisper STT)
        self.btn_pill_stt = ctk.CTkButton(
            self.pill_container,
            text="Áudio p/ Texto",
            height=38,
            corner_radius=9,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="transparent",
            border_width=0,
            text_color=COLORS["text_secondary"],
            hover_color="#151C2C",
            command=lambda: self.select_tab("stt")
        )
        self.btn_pill_stt.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        # 3. Menu Lateral de Configurações e Seções
        self.nav_menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_menu_frame.grid(row=2, column=0, padx=14, pady=0, sticky="ew")
        self.nav_menu_frame.grid_columnconfigure(0, weight=1)

        self.btn_menu_studio = ctk.CTkButton(
            self.nav_menu_frame,
            text="  🎙️  Estúdio Principal",
            height=38,
            corner_radius=8,
            anchor="w",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#141B2D",
            text_color=COLORS["neon_blue"],
            hover_color="#1A243D",
            border_width=1,
            border_color="#1E2A48",
            command=self._on_click_studio
        )
        self.btn_menu_studio.grid(row=0, column=0, padx=2, pady=4, sticky="ew")

        self.btn_menu_voices = ctk.CTkButton(
            self.nav_menu_frame,
            text="  👤  Vozes & Perfis",
            height=38,
            corner_radius=8,
            anchor="w",
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color="#141B2D",
            command=lambda: self.select_tab("tts")
        )
        self.btn_menu_voices.grid(row=1, column=0, padx=2, pady=4, sticky="ew")

        self.btn_menu_tuning = ctk.CTkButton(
            self.nav_menu_frame,
            text="  📈  Ajustes de Áudio",
            height=38,
            corner_radius=8,
            anchor="w",
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color="#141B2D",
            command=lambda: self.select_tab("tts")
        )
        self.btn_menu_tuning.grid(row=2, column=0, padx=2, pady=4, sticky="ew")

        self.btn_menu_settings = ctk.CTkButton(
            self.nav_menu_frame,
            text="  ⚙️  Configurações",
            height=38,
            corner_radius=8,
            anchor="w",
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color="#141B2D",
            command=lambda: self.select_tab("settings")
        )
        self.btn_menu_settings.grid(row=3, column=0, padx=2, pady=4, sticky="ew")

        # 4. Rodapé da Barra Lateral
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=6, column=0, padx=20, pady=20, sticky="sew")

        self.status_indicator = ctk.CTkLabel(
            footer_frame,
            text="● Texto para Áudio Ativo",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["accent_green"]
        )
        self.status_indicator.pack(anchor="w", pady=(0, 4))

        self.version_label = ctk.CTkLabel(
            footer_frame,
            text="v1.0.0 • CustomTkinter & Python",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_muted"]
        )
        self.version_label.pack(anchor="w")

    def _on_click_studio(self):
        """Retorna ao estúdio da ferramenta ativa."""
        if self.active_tab == "settings":
            self.select_tab("tts")
        else:
            self.select_tab(self.active_tab)

    def select_tab(self, tab_id: str):
        """Alterna a seleção entre Texto para Áudio, Áudio para Texto e Configurações."""
        self.active_tab = tab_id

        # Reseta estilos de botões do menu
        self.btn_menu_studio.configure(fg_color="transparent", text_color=COLORS["text_secondary"], border_width=0)
        self.btn_menu_voices.configure(fg_color="transparent", text_color=COLORS["text_secondary"], border_width=0)
        self.btn_menu_tuning.configure(fg_color="transparent", text_color=COLORS["text_secondary"], border_width=0)
        self.btn_menu_settings.configure(fg_color="transparent", text_color=COLORS["text_secondary"], border_width=0)

        if tab_id == "tts":
            self.btn_pill_tts.configure(
                fg_color="#1B253D",
                border_width=1,
                border_color=COLORS["neon_blue"],
                text_color=COLORS["text_primary"]
            )
            self.btn_pill_stt.configure(
                fg_color="transparent",
                border_width=0,
                text_color=COLORS["text_secondary"]
            )
            self.btn_menu_studio.configure(
                fg_color="#141B2D",
                text_color=COLORS["neon_blue"],
                border_width=1,
                border_color="#1E2A48"
            )
            self.set_system_status("Texto para Áudio Ativo", COLORS["accent_green"])

        elif tab_id in ["stt", "whisper"]:
            self.btn_pill_stt.configure(
                fg_color="#1B253D",
                border_width=1,
                border_color=COLORS["neon_violet"],
                text_color=COLORS["text_primary"]
            )
            self.btn_pill_tts.configure(
                fg_color="transparent",
                border_width=0,
                text_color=COLORS["text_secondary"]
            )
            self.btn_menu_studio.configure(
                fg_color="#141B2D",
                text_color=COLORS["neon_violet"],
                border_width=1,
                border_color="#1E2A48"
            )
            self.set_system_status("Áudio para Texto (Whisper) Ativo", COLORS["neon_blue"])

        elif tab_id == "settings":
            self.btn_pill_tts.configure(fg_color="transparent", border_width=0, text_color=COLORS["text_secondary"])
            self.btn_pill_stt.configure(fg_color="transparent", border_width=0, text_color=COLORS["text_secondary"])
            self.btn_menu_settings.configure(
                fg_color="#141B2D",
                text_color=COLORS["neon_cyan"],
                border_width=1,
                border_color="#1E2A48"
            )
            self.set_system_status("Configurações do Sistema", COLORS["neon_cyan"])

        self.on_navigate(tab_id)

    def set_system_status(self, text: str, color: str = None):
        """Atualiza a mensagem de status da barra lateral."""
        self.status_indicator.configure(text=f"● {text}", text_color=color or COLORS["accent_green"])
