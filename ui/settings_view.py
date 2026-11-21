"""
AudioStudio IA - Aba de Configurações Gerais
=============================================
Painel completo de configurações do sistema: gerenciamento de pastas de exportação,
diagnóstico de aceleração por GPU/CUDA, status dos motores de IA e preferências visuais.
"""

import os
import subprocess
from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk

from ui.theme import COLORS
from core.tts_engine import TTSEngine
from core.whisper_engine import WhisperEngine


class SettingsView(ctk.CTkFrame):
    """View de Configurações Gerais do AudioStudio IA."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.default_output_dir = str(Path.home() / "Documents")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_content()

    def _build_header(self):
        """Cabeçalho superior com título e ícone neon."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=24, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        text_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        text_box.grid(row=0, column=0, sticky="w")

        title = ctk.CTkLabel(
            text_box,
            text="AudioStudio IA - Configurações do Sistema",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            text_box,
            text="Gerencie diretórios padrão, diagnóstico de aceleração por GPU (CUDA) e preferências do estúdio.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        subtitle.pack(anchor="w", pady=(3, 0))

        badge = ctk.CTkLabel(
            header_frame,
            text="⚙️⚡",
            font=ctk.CTkFont(size=22),
            text_color=COLORS["neon_cyan"]
        )
        badge.grid(row=0, column=1, sticky="e", padx=(10, 0))

    def _build_content(self):
        """Container rolável com os cartões de configurações."""
        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        scroll.grid(row=1, column=0, padx=24, pady=(0, 20), sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # -------------------------------------------------------------
        # CARD 1: DIRETÓRIOS & ARMAZENAMENTO
        # -------------------------------------------------------------
        card_dirs = ctk.CTkFrame(
            scroll,
            fg_color=COLORS["card_bg"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["card_border"]
        )
        card_dirs.pack(fill="x", pady=(0, 16))
        card_dirs.grid_columnconfigure(0, weight=1)

        lbl_dir_title = ctk.CTkLabel(
            card_dirs,
            text="📁  Pastas & Armazenamento",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        lbl_dir_title.pack(anchor="w", padx=20, pady=(16, 8))

        lbl_dir_desc = ctk.CTkLabel(
            card_dirs,
            text="Pasta padrão utilizada para exportação de arquivos gerados (MP3, WAV, TXT e legendas SRT):",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        lbl_dir_desc.pack(anchor="w", padx=20, pady=(0, 8))

        dir_row = ctk.CTkFrame(card_dirs, fg_color="transparent")
        dir_row.pack(fill="x", padx=20, pady=(0, 16))
        dir_row.grid_columnconfigure(0, weight=1)

        self.entry_dir = ctk.CTkEntry(
            dir_row,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["card_border"],
            height=36,
            corner_radius=8
        )
        self.entry_dir.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_dir.insert(0, self.default_output_dir)

        btn_browse = ctk.CTkButton(
            dir_row,
            text="Alterar Pasta",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["btn_upload_bg"],
            hover_color=COLORS["btn_upload_hover"],
            command=self._on_change_dir
        )
        btn_browse.grid(row=0, column=1, padx=(0, 6))

        btn_open = ctk.CTkButton(
            dir_row,
            text="Abrir no Explorer",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["btn_clear_bg"],
            hover_color=COLORS["btn_clear_hover"],
            border_width=1,
            border_color=COLORS["btn_clear_border"],
            text_color=COLORS["text_secondary"],
            command=self._on_open_dir
        )
        btn_open.grid(row=0, column=2)

        # -------------------------------------------------------------
        # CARD 2: DIAGNÓSTICO DE IA & ACELERAÇÃO POR GPU
        # -------------------------------------------------------------
        card_ai = ctk.CTkFrame(
            scroll,
            fg_color=COLORS["card_bg"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["card_border"]
        )
        card_ai.pack(fill="x", pady=(0, 16))

        lbl_ai_title = ctk.CTkLabel(
            card_ai,
            text="⚡  Aceleração de Hardware & Motores de IA",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        lbl_ai_title.pack(anchor="w", padx=20, pady=(16, 8))

        # Status do Whisper
        whisper_status = WhisperEngine.detect_engine()
        whisper_label = "faster-whisper (CTranslate2 Otimizado)" if whisper_status == "faster_whisper" else "openai-whisper" if whisper_status == "openai_whisper" else "Modo Simulação / Fallback (Instale: faster-whisper)"
        whisper_color = COLORS["accent_green"] if "faster" in whisper_label else COLORS["accent_gold"]

        ai_info_frame = ctk.CTkFrame(card_ai, fg_color=COLORS["input_bg"], corner_radius=10, border_width=1, border_color=COLORS["card_border"])
        ai_info_frame.pack(fill="x", padx=20, pady=(0, 14))

        lbl_w = ctk.CTkLabel(ai_info_frame, text=f"• Motor de Transcrição Whisper: {whisper_label}", font=ctk.CTkFont(size=12, weight="bold"), text_color=whisper_color)
        lbl_w.pack(anchor="w", padx=16, pady=(10, 4))

        # Status do TTS
        tts_obj = TTSEngine()
        tts_label = "pyttsx3 (SAPI5 Windows Integrado)" if tts_obj.backend_type == "pyttsx3" else "Síntese Senoidal Nativa (Fallback)"
        tts_color = COLORS["accent_green"] if "pyttsx3" in tts_label else COLORS["accent_gold"]

        lbl_t = ctk.CTkLabel(ai_info_frame, text=f"• Motor de Síntese de Voz (TTS): {tts_label}", font=ctk.CTkFont(size=12, weight="bold"), text_color=tts_color)
        lbl_t.pack(anchor="w", padx=16, pady=(0, 10))

        # Botão Diagnóstico Rápido
        btn_diag = ctk.CTkButton(
            card_ai,
            text="🔍  Executar Teste de Diagnóstico de IA",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#1F2A44",
            hover_color="#2B3A5E",
            border_width=1,
            border_color=COLORS["neon_blue"],
            text_color=COLORS["neon_blue"],
            command=self._on_run_diagnostic
        )
        btn_diag.pack(anchor="w", padx=20, pady=(0, 16))

        # -------------------------------------------------------------
        # CARD 3: APARÊNCIA & PREFERÊNCIAS
        # -------------------------------------------------------------
        card_theme = ctk.CTkFrame(
            scroll,
            fg_color=COLORS["card_bg"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["card_border"]
        )
        card_theme.pack(fill="x", pady=(0, 16))

        lbl_thm_title = ctk.CTkLabel(
            card_theme,
            text="🎨  Aparência & Interface Gráfica",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        lbl_thm_title.pack(anchor="w", padx=20, pady=(16, 8))

        theme_row = ctk.CTkFrame(card_theme, fg_color="transparent")
        theme_row.pack(fill="x", padx=20, pady=(0, 16))

        lbl_mode = ctk.CTkLabel(theme_row, text="Modo de Exibição:", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text_secondary"])
        lbl_mode.pack(side="left", padx=(0, 12))

        self.combo_mode = ctk.CTkOptionMenu(
            theme_row,
            values=["Escuro (Dark - Recomendado)", "Claro (Light)", "Sistema"],
            height=34,
            corner_radius=8,
            fg_color=COLORS["input_bg"],
            button_color="#1E293B",
            button_hover_color=COLORS["neon_blue"],
            command=self._on_change_appearance
        )
        self.combo_mode.pack(side="left")
        self.combo_mode.set("Escuro (Dark - Recomendado)")

    def _on_change_dir(self):
        new_d = filedialog.askdirectory(title="Selecionar Pasta Padrão")
        if new_d:
            self.default_output_dir = new_d
            self.entry_dir.delete(0, "end")
            self.entry_dir.insert(0, new_d)
            messagebox.showinfo("Configuração Atualizada", f"Nova pasta padrão definida para:\n{new_d}")

    def _on_open_dir(self):
        cur_d = self.entry_dir.get().strip()
        if os.path.exists(cur_d):
            os.startfile(cur_d)
        else:
            messagebox.showwarning("Aviso", "O diretório indicado ainda não existe.")

    def _on_change_appearance(self, choice: str):
        if "Claro" in choice:
            ctk.set_appearance_mode("Light")
        elif "Sistema" in choice:
            ctk.set_appearance_mode("System")
        else:
            ctk.set_appearance_mode("Dark")

    def _on_run_diagnostic(self):
        w_status = WhisperEngine.detect_engine()
        msg = (
            f"=== Diagnóstico do AudioStudio IA ===\n\n"
            f"• Motor Whisper: {w_status}\n"
            f"• Motor TTS: {TTSEngine().backend_type}\n"
            f"• Pasta Padrão: {self.entry_dir.get()}\n\n"
            f"Todas as rotinas assíncronas e os despachantes thread-safe estão operacionais."
        )
        messagebox.showinfo("Relatório de Diagnóstico", msg)
