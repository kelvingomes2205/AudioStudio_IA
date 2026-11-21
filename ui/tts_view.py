"""
AudioStudio IA - Aba 1: Conversor de Texto para Áudio (TTS)
============================================================
Interface modernizada em conformidade estrita com o modelo visual de referência:
estilo Cyberpunk / Neon Glassmorphism, visualizador de onda sonora neon integrado,
barra de progresso com cronômetro de tempo decorrido ao vivo (segundo a segundo),
tempo estimado (ETA) contínuo e porcentagem em tempo real.
"""

import os
import time
import datetime
from tkinter import filedialog, messagebox
import customtkinter as ctk

from ui.theme import COLORS
from ui.wave_visualizer import WaveVisualizer
from core.tts_engine import TTSEngine
from utils.thread_manager import run_in_thread
from utils.audio_utils import format_time


class TTSView(ctk.CTkFrame):
    """View do Conversor de Texto para Áudio com cronômetro e progresso fluidos."""

    def __init__(self, master, tts_engine: TTSEngine):
        super().__init__(master, fg_color="transparent")
        self.tts = tts_engine
        self.temp_preview_path = os.path.join(os.environ.get("TEMP", "."), "audiostudio_preview.wav")
        self._tts_running = False
        self._tts_start_time: float = 0.0
        self._tts_estimated_duration: float = 3.0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_main_card()
        self._build_settings_card()
        self._build_action_buttons()

    def _build_header(self):
        """Cabeçalho com título, subtítulo e indicador de frequência sonora neon."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=24, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        text_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        text_box.grid(row=0, column=0, sticky="w")

        title = ctk.CTkLabel(
            text_box,
            text="AudioStudio IA - Texto para Áudio (TTS)",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            text_box,
            text="Sintetize narrações naturais em alta fidelidade a partir de textos digitados ou importados.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        subtitle.pack(anchor="w", pady=(3, 0))

        wave_badge = ctk.CTkLabel(
            header_frame,
            text="〰️⚡",
            font=ctk.CTkFont(size=22),
            text_color=COLORS["neon_cyan"]
        )
        wave_badge.grid(row=0, column=1, sticky="e", padx=(10, 0))

    def _build_main_card(self):
        """Card principal com área de texto, visualizador de onda e botões de ação."""
        self.main_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["card_bg"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["card_border"]
        )
        self.main_card.grid(row=1, column=0, padx=24, pady=(5, 10), sticky="nsew")
        self.main_card.grid_columnconfigure(0, weight=1)
        self.main_card.grid_rowconfigure(1, weight=1)

        # 1. Barra de ferramentas superior
        top_bar = ctk.CTkFrame(self.main_card, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=20, pady=(16, 8), sticky="ew")

        lbl_section = ctk.CTkLabel(
            top_bar,
            text="✍️  Cole o texto abaixo:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        lbl_section.pack(side="left")

        # Botão Carregar Arquivo
        self.btn_upload = ctk.CTkButton(
            top_bar,
            text="⬆️  Carregar Arquivo (.txt)",
            height=34,
            corner_radius=10,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["btn_upload_bg"],
            hover_color=COLORS["btn_upload_hover"],
            border_width=1,
            border_color=COLORS["neon_blue"],
            command=self._load_text_file
        )
        self.btn_upload.pack(side="right", padx=(10, 0))

        # Botão Limpar Texto
        self.btn_clear = ctk.CTkButton(
            top_bar,
            text="🗑️  Limpar",
            width=85,
            height=34,
            corner_radius=10,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["btn_clear_bg"],
            hover_color=COLORS["btn_clear_hover"],
            border_width=1,
            border_color=COLORS["btn_clear_border"],
            text_color=COLORS["text_secondary"],
            command=self._clear_text
        )
        self.btn_clear.pack(side="right", padx=(8, 0))

        # Seletor de Modo de Exibição
        self.view_switch = ctk.CTkSegmentedButton(
            top_bar,
            values=["Editor de Texto", "Visualizador de Onda"],
            height=30,
            corner_radius=8,
            font=ctk.CTkFont(size=11),
            selected_color="#1E293B",
            selected_hover_color="#27354D",
            unselected_color="#0A0E17",
            unselected_hover_color="#141B2D",
            command=self._on_view_switch
        )
        self.view_switch.pack(side="right", padx=(0, 10))
        self.view_switch.set("Editor de Texto")

        # 2. Container Central Dinâmico (Textbox + WaveVisualizer)
        self.center_container = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.center_container.grid(row=1, column=0, padx=20, pady=4, sticky="nsew")
        self.center_container.grid_columnconfigure(0, weight=1)
        self.center_container.grid_rowconfigure(0, weight=1)

        # Área de Texto principal
        self.textbox = ctk.CTkTextbox(
            self.center_container,
            fg_color=COLORS["input_bg"],
            border_width=1,
            border_color=COLORS["card_border"],
            corner_radius=12,
            font=ctk.CTkFont(size=14),
            wrap="word"
        )
        self.textbox.grid(row=0, column=0, sticky="nsew")
        self.textbox.bind("<KeyRelease>", self._update_counter)

        # Visualizador de Onda Neon
        self.wave_visualizer = WaveVisualizer(self.center_container, height=190)

        # 3. Rodapé do Card com Contador de Caracteres e Palavras
        footer_bar = ctk.CTkFrame(self.main_card, fg_color="transparent")
        footer_bar.grid(row=2, column=0, padx=20, pady=(6, 14), sticky="ew")

        self.counter_label = ctk.CTkLabel(
            footer_bar,
            text="0 caracteres  |  0 palavras",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"]
        )
        self.counter_label.pack(side="left")

    def _build_settings_card(self):
        """Card inferior com Seletor de Voz, Velocidade e Volume."""
        settings_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["card_bg"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["card_border"]
        )
        settings_card.grid(row=2, column=0, padx=24, pady=(0, 10), sticky="ew")
        settings_card.grid_columnconfigure((0, 1, 2), weight=1)

        # 1. Seletor de Voz com rótulo
        voice_box = ctk.CTkFrame(settings_card, fg_color="transparent")
        voice_box.grid(row=0, column=0, padx=18, pady=16, sticky="ew")

        lbl_v = ctk.CTkLabel(
            voice_box,
            text="Seletor de Voz:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        lbl_v.pack(anchor="w", pady=(0, 6))

        voice_options = [v["label"] for v in self.tts.get_available_voices()]
        self.combo_voices = ctk.CTkOptionMenu(
            voice_box,
            values=voice_options,
            height=36,
            corner_radius=10,
            fg_color="#0A0E17",
            button_color="#1E293B",
            button_hover_color=COLORS["neon_blue"],
            text_color=COLORS["text_primary"],
            dropdown_fg_color="#131828",
            dropdown_hover_color="#1E293B"
        )
        self.combo_voices.pack(fill="x")
        self.combo_voices.set(voice_options[0])

        # 2. Velocidade da Fala
        rate_box = ctk.CTkFrame(settings_card, fg_color="transparent")
        rate_box.grid(row=0, column=1, padx=18, pady=16, sticky="ew")

        self.lbl_rate = ctk.CTkLabel(
            rate_box,
            text="Velocidade (1.0x):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.lbl_rate.pack(anchor="w", pady=(0, 6))

        self.slider_rate = ctk.CTkSlider(
            rate_box,
            from_=0.5,
            to=2.0,
            number_of_steps=15,
            progress_color=COLORS["neon_cyan"],
            button_color=COLORS["neon_blue"],
            button_hover_color=COLORS["neon_violet"],
            command=self._on_rate_change
        )
        self.slider_rate.set(1.0)
        self.slider_rate.pack(fill="x")

        # 3. Volume
        vol_box = ctk.CTkFrame(settings_card, fg_color="transparent")
        vol_box.grid(row=0, column=2, padx=18, pady=16, sticky="ew")

        self.lbl_vol = ctk.CTkLabel(
            vol_box,
            text="Volume (100%):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.lbl_vol.pack(anchor="w", pady=(0, 6))

        self.slider_vol = ctk.CTkSlider(
            vol_box,
            from_=0.0,
            to=1.0,
            number_of_steps=10,
            progress_color=COLORS["neon_cyan"],
            button_color=COLORS["neon_blue"],
            button_hover_color=COLORS["neon_violet"],
            command=self._on_vol_change
        )
        self.slider_vol.set(1.0)
        self.slider_vol.pack(fill="x")

    def _build_action_buttons(self):
        """Botões de ação e Barra de Progresso com Estimativa de Tempo (ETA)."""
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=3, column=0, padx=24, pady=(0, 10), sticky="ew")
        actions_frame.grid_columnconfigure((0, 1), weight=1)

        # Botão 1: Ouvir Prévia da Voz
        self.btn_preview = ctk.CTkButton(
            actions_frame,
            text="🔊  Ouvir Prévia da Voz",
            height=46,
            corner_radius=14,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["btn_preview_bg"],
            hover_color=COLORS["btn_preview_hover"],
            border_width=1.5,
            border_color=COLORS["btn_preview_border"],
            text_color=COLORS["btn_preview_text"],
            command=self._on_preview_clicked
        )
        self.btn_preview.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        # Botão 2: Salvar como MP3
        self.btn_save = ctk.CTkButton(
            actions_frame,
            text="💾  Salvar como MP3",
            height=46,
            corner_radius=14,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["btn_save_bg"],
            hover_color=COLORS["btn_save_hover"],
            border_width=1,
            border_color=COLORS["btn_save_border"],
            text_color=COLORS["btn_save_text"],
            command=self._on_save_clicked
        )
        self.btn_save.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        # Barra de Progresso com Tempo Estimado (ETA) e Porcentagem
        self.prog_container = ctk.CTkFrame(self, fg_color="transparent")
        self.prog_container.grid(row=4, column=0, padx=24, pady=(0, 16), sticky="ew")
        self.prog_container.grid_columnconfigure(0, weight=1)

        info_row = ctk.CTkFrame(self.prog_container, fg_color="transparent")
        info_row.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        info_row.grid_columnconfigure(0, weight=1)

        self.lbl_eta = ctk.CTkLabel(
            info_row,
            text="⏱️ Tempo Restante: Aguardando comando...",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_secondary"]
        )
        self.lbl_eta.grid(row=0, column=0, sticky="w")

        self.lbl_percent = ctk.CTkLabel(
            info_row,
            text="0%",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["neon_blue"]
        )
        self.lbl_percent.grid(row=0, column=1, sticky="e")

        self.progress_bar = ctk.CTkProgressBar(
            self.prog_container,
            fg_color="#0A0E17",
            progress_color=COLORS["neon_cyan"],
            height=12,
            corner_radius=6
        )
        self.progress_bar.grid(row=1, column=0, sticky="ew")
        self.progress_bar.set(0.0)

    # Controles de Interface e Alternância de Telas
    def _on_view_switch(self, mode: str):
        if mode == "Visualizador de Onda":
            self.textbox.grid_forget()
            self.wave_visualizer.grid(row=0, column=0, sticky="nsew")
            self.wave_visualizer.redraw()
        else:
            self.wave_visualizer.grid_forget()
            self.textbox.grid(row=0, column=0, sticky="nsew")

    def _update_counter(self, event=None):
        content = self.textbox.get("1.0", "end-1c")
        chars = len(content)
        words = len(content.split())
        self.counter_label.configure(text=f"{chars:,} caracteres  |  {words:,} palavras".replace(",", "."))

    def _on_rate_change(self, value):
        self.lbl_rate.configure(text=f"Velocidade ({value:.2f}x):")

    def _on_vol_change(self, value):
        self.lbl_vol.configure(text=f"Volume ({int(value * 100)}%):")

    def _clear_text(self):
        self.textbox.delete("1.0", "end")
        self._update_counter()

    def _load_text_file(self):
        path = filedialog.askopenfilename(
            title="Selecionar Arquivo de Texto",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        if path and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.textbox.delete("1.0", "end")
                self.textbox.insert("1.0", content)
                self._update_counter()
                self.lbl_eta.configure(text=f"Arquivo carregado com sucesso: {os.path.basename(path)}", text_color=COLORS["neon_cyan"])
            except Exception as e:
                messagebox.showerror("Erro de Leitura", f"Não foi possível abrir o arquivo:\n{e}")

    def _tick_tts_live_timer(self):
        """Cronômetro ao vivo segundo a segundo para a síntese TTS."""
        if not self._tts_running:
            return

        elapsed = time.time() - self._tts_start_time
        rem_sec = max(0.4, self._tts_estimated_duration - elapsed)
        rem_m, rem_s = divmod(int(rem_sec), 60)

        # Interpolação contínua da barra de progresso (avança fluidamente de 0% a 95%)
        ratio = min(0.95, elapsed / max(1.0, elapsed + rem_sec))
        self.progress_bar.set(ratio)
        self.lbl_percent.configure(text=f"{int(ratio * 100)}%")
        self.lbl_eta.configure(
            text=f"⏱️ Tempo Estimado: ~{rem_m:02d}:{rem_s:02d}  (Decorrido: {format_time(elapsed)})",
            text_color=COLORS["neon_blue"]
        )

        self.after(200, self._tick_tts_live_timer)

    # Processamento Multithread Não-Bloqueante
    def _on_preview_clicked(self):
        text = self.textbox.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Texto Vazio", "Por favor, digite ou cole um texto antes de ouvir a prévia.")
            return

        self._tts_running = True
        self.btn_preview.configure(state="disabled", text="⏳ Sintetizando Prévia...")

        # Estimativa imediata com base no número de palavras
        word_count = len(text.split())
        self._tts_estimated_duration = max(2.0, min(16.0, word_count * 0.045 + 1.2))
        self._tts_start_time = time.time()

        # Ativa visualizador e inicia cronômetro ao vivo
        self.view_switch.set("Visualizador de Onda")
        self._on_view_switch("Visualizador de Onda")
        self.wave_visualizer.start_animation()
        self._tick_tts_live_timer()

        rate = self.slider_rate.get()
        vol = self.slider_vol.get()
        voice_label = self.combo_voices.get()
        voice_id = "pt_br_antonio" if "Masculina" in voice_label else "pt_br_leticia"

        def task():
            return self.tts.generate_speech(text, self.temp_preview_path, voice_id, rate, vol)

        def on_done(success: bool, result):
            self._tts_running = False
            total_elapsed = time.time() - self._tts_start_time

            def ui_update():
                self.btn_preview.configure(state="normal", text="🔊  Ouvir Prévia da Voz")
                if success and os.path.exists(self.temp_preview_path):
                    self.progress_bar.set(1.0)
                    self.lbl_percent.configure(text="100%")
                    self.lbl_eta.configure(text=f"✅ Áudio Concluído em {format_time(total_elapsed)}! Reproduzindo...", text_color=COLORS["accent_green"])
                    self.tts.play_audio(self.temp_preview_path)
                    self.after(3500, self.wave_visualizer.stop_animation)
                else:
                    self.wave_visualizer.stop_animation()
                    self.lbl_eta.configure(text="Falha ao gerar prévia de áudio.", text_color=COLORS["accent_red"])

            self.after(0, ui_update)

        run_in_thread(task, on_done)

    def _on_save_clicked(self):
        text = self.textbox.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Texto Vazio", "Por favor, digite ou cole um texto antes de salvar.")
            return

        default_name = f"Audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        save_path = filedialog.asksaveasfilename(
            title="Salvar Áudio Sintetizado",
            initialfile=default_name,
            defaultextension=".mp3",
            filetypes=[("Arquivo MP3", "*.mp3"), ("Arquivo WAV", "*.wav")]
        )
        if not save_path:
            return

        self._tts_running = True
        self.btn_save.configure(state="disabled", text="⏳ Exportando MP3...")

        word_count = len(text.split())
        self._tts_estimated_duration = max(2.5, min(20.0, word_count * 0.05 + 1.5))
        self._tts_start_time = time.time()

        self._tick_tts_live_timer()

        rate = self.slider_rate.get()
        vol = self.slider_vol.get()
        voice_label = self.combo_voices.get()
        voice_id = "pt_br_antonio" if "Masculina" in voice_label else "pt_br_leticia"

        def task():
            return self.tts.generate_speech(text, save_path, voice_id, rate, vol)

        def on_done(success: bool, result):
            self._tts_running = False
            total_elapsed = time.time() - self._tts_start_time

            def ui_update():
                self.btn_save.configure(state="normal", text="💾  Salvar como MP3")
                if success and os.path.exists(save_path):
                    self.progress_bar.set(1.0)
                    self.lbl_percent.configure(text="100%")
                    self.lbl_eta.configure(text=f"✅ Arquivo salvo em {format_time(total_elapsed)}: {os.path.basename(save_path)}", text_color=COLORS["accent_green"])
                    messagebox.showinfo("Sucesso", f"Áudio gerado e salvo com sucesso em {format_time(total_elapsed)} em:\n{save_path}")
                else:
                    self.lbl_eta.configure(text="Falha ao exportar arquivo de áudio.", text_color=COLORS["accent_red"])

            self.after(0, ui_update)

        run_in_thread(task, on_done)
