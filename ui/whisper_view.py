"""
AudioStudio IA - Aba 2: Transcritor Whisper em Lote (STT)
===========================================================
Interface profissional de transcrição em lote totalmente redesenhada no estilo
Cyberpunk / Neon Glassmorphism, com console em tempo real à esquerda, barra de progresso
fluida, cronômetro de tempo decorrido ao vivo (segundo a segundo) e cálculo dinâmico
imediato de tempo restante estimado (ETA).
"""

import os
import time
import datetime
import threading
from pathlib import Path
from typing import List
from tkinter import filedialog, messagebox
import customtkinter as ctk

from ui.theme import COLORS
from ui.wave_visualizer import WaveVisualizer
from core.whisper_engine import WhisperEngine
from utils.audio_utils import scan_audio_files, format_time, get_audio_duration


class WhisperView(ctk.CTkFrame):
    """View do Transcritor Whisper com estilo Cyberpunk Glassmorphism."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.stop_event = threading.Event()
        self.is_running = False
        self.selected_files: List[str] = []

        # Variáveis do cronômetro fluido e estimador de tempo (ETA)
        self._start_time: float = 0.0
        self._total_audio_duration: float = 1.0
        self._estimated_remaining_seconds: float = 0.0
        self._current_progress_ratio: float = 0.0

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_left_panel()
        self._build_right_panel()

    def _build_header(self):
        """Cabeçalho superior com título, subtítulo e insígnia neon."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, padx=24, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        text_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        text_box.grid(row=0, column=0, sticky="w")

        title = ctk.CTkLabel(
            text_box,
            text="AudioStudio IA - Áudio para Texto (Whisper STT)",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            text_box,
            text="Transcreva arquivos de áudio e vídeo em lote com alta precisão utilizando IA neural Whisper.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        subtitle.pack(anchor="w", pady=(3, 0))

        wave_badge = ctk.CTkLabel(
            header_frame,
            text="🎙️⚡",
            font=ctk.CTkFont(size=22),
            text_color=COLORS["neon_violet"]
        )
        wave_badge.grid(row=0, column=1, sticky="e", padx=(10, 0))

    def _build_left_panel(self):
        """Painel esquerdo contendo o console de logs, visualizador e barra de progresso com cronômetro fluido."""
        left_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["card_bg"],
            corner_radius=16,
            border_width=1,
            border_color=COLORS["card_border"]
        )
        left_card.grid(row=1, column=0, padx=(24, 10), pady=(0, 20), sticky="nsew")
        left_card.grid_rowconfigure(2, weight=1)
        left_card.grid_columnconfigure(0, weight=1)

        # Cabeçalho do console
        top_bar = ctk.CTkFrame(left_card, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=18, pady=(16, 6), sticky="ew")

        lbl_log = ctk.CTkLabel(
            top_bar,
            text="🖥️  Console de Processamento & Logs:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        lbl_log.pack(side="left")

        # Mini visualizador de onda
        self.mini_wave = WaveVisualizer(left_card, height=65, num_bars=50)
        self.mini_wave.grid(row=1, column=0, padx=18, pady=(0, 8), sticky="ew")

        # Console de texto grande (Consolas)
        self.log_box = ctk.CTkTextbox(
            left_card,
            fg_color=COLORS["input_bg"],
            border_width=1,
            border_color=COLORS["card_border"],
            corner_radius=10,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word"
        )
        self.log_box.grid(row=2, column=0, padx=18, pady=4, sticky="nsew")
        self.append_log("Sistema pronto para processar.", level="PADRAO")

        # Barra de Progresso com Tempo Estimado (ETA) e Porcentagem
        prog_bar_frame = ctk.CTkFrame(left_card, fg_color="transparent")
        prog_bar_frame.grid(row=3, column=0, padx=18, pady=(10, 16), sticky="ew")
        prog_bar_frame.grid_columnconfigure(0, weight=1)

        # Linha superior: Tempo Restante à esquerda e Porcentagem à direita
        info_row = ctk.CTkFrame(prog_bar_frame, fg_color="transparent")
        info_row.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        info_row.grid_columnconfigure(0, weight=1)

        self.lbl_eta = ctk.CTkLabel(
            info_row,
            text="⏱️ Tempo Restante: Aguardando início...",
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

        # Barra de Progresso CustomTkinter
        self.progress_bar = ctk.CTkProgressBar(
            prog_bar_frame,
            fg_color="#0A0E17",
            progress_color=COLORS["neon_cyan"],
            height=12,
            corner_radius=6
        )
        self.progress_bar.grid(row=1, column=0, sticky="ew")
        self.progress_bar.set(0.0)

    def _build_right_panel(self):
        """Painel direito contendo todas as opções de configuração 100% em português."""
        right_panel = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["card_bg"],
            border_width=1,
            border_color=COLORS["card_border"],
            corner_radius=16
        )
        right_panel.grid(row=1, column=1, padx=(10, 24), pady=(0, 20), sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)

        # 1. Seção Arquivos / Pastas
        lbl_files = ctk.CTkLabel(
            right_panel,
            text="Arquivos / Pastas Selecionados:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        lbl_files.pack(anchor="w", pady=(6, 4))

        self.box_files = ctk.CTkTextbox(
            right_panel,
            height=80,
            fg_color=COLORS["input_bg"],
            border_width=1,
            border_color=COLORS["card_border"],
            corner_radius=8,
            font=ctk.CTkFont(size=11)
        )
        self.box_files.pack(fill="x", pady=(0, 8))
        self.box_files.configure(state="disabled")

        # Botões de Adicionar
        btn_row = ctk.CTkFrame(right_panel, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 6))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        self.btn_add_files = ctk.CTkButton(
            btn_row,
            text="➕  Adicionar Arquivos",
            height=34,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS["btn_upload_bg"],
            hover_color=COLORS["btn_upload_hover"],
            command=self._on_add_files
        )
        self.btn_add_files.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.btn_add_folder = ctk.CTkButton(
            btn_row,
            text="📁  Adicionar Pasta",
            height=34,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#5B21B6",
            hover_color=COLORS["neon_violet"],
            command=self._on_add_folder
        )
        self.btn_add_folder.grid(row=0, column=1, padx=(4, 0), sticky="ew")

        # Botão Limpar lista
        self.btn_clear_list = ctk.CTkButton(
            right_panel,
            text="🗑️  Limpar Lista",
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["btn_clear_bg"],
            hover_color=COLORS["btn_clear_hover"],
            border_width=1,
            border_color=COLORS["btn_clear_border"],
            text_color=COLORS["text_secondary"],
            command=self._on_clear_files
        )
        self.btn_clear_list.pack(fill="x", pady=(0, 14))

        # 2. Idioma
        lbl_lang = ctk.CTkLabel(right_panel, text="Idioma do Áudio (vazio = automático):", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_lang.pack(anchor="w", pady=(0, 3))

        self.entry_lang = ctk.CTkEntry(
            right_panel,
            placeholder_text="pt, en, es... (deixe vazio para auto-detecção)",
            fg_color=COLORS["input_bg"],
            border_color=COLORS["card_border"],
            height=34,
            corner_radius=8
        )
        self.entry_lang.pack(fill="x", pady=(0, 12))

        # 3. Modelo do Whisper
        lbl_model = ctk.CTkLabel(right_panel, text="Modelo do Whisper:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_model.pack(anchor="w", pady=(0, 3))

        self.combo_model = ctk.CTkOptionMenu(
            right_panel,
            values=[
                "base (Padrão - Rápido)",
                "tiny (Ultra-Rápido)",
                "small (Equilibrado)",
                "medium (Alta Precisão)",
                "large-v3 (Máxima Precisão)"
            ],
            fg_color=COLORS["input_bg"],
            button_color="#1E293B",
            button_hover_color=COLORS["neon_blue"],
            height=34,
            corner_radius=8
        )
        self.combo_model.pack(fill="x", pady=(0, 12))
        self.combo_model.set("base (Padrão - Rápido)")

        # 4. Dispositivo de Processamento
        lbl_dev = ctk.CTkLabel(right_panel, text="Dispositivo de Processamento:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_dev.pack(anchor="w", pady=(0, 3))

        self.combo_device = ctk.CTkOptionMenu(
            right_panel,
            values=[
                "Automático (Recomendado)",
                "Placa de Vídeo (CUDA / GPU)",
                "Processador (CPU)"
            ],
            fg_color=COLORS["input_bg"],
            button_color="#1E293B",
            button_hover_color=COLORS["neon_blue"],
            height=34,
            corner_radius=8
        )
        self.combo_device.pack(fill="x", pady=(0, 12))
        self.combo_device.set("Automático (Recomendado)")

        # 5. Precisão Numérica
        lbl_prec = ctk.CTkLabel(right_panel, text="Precisão de Cálculo:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_prec.pack(anchor="w", pady=(0, 3))

        self.combo_precision = ctk.CTkOptionMenu(
            right_panel,
            values=["int8 (Rápido e Leve)", "float16 (Equilibrado)", "float32 (Máxima Fidelidade)"],
            fg_color=COLORS["input_bg"],
            button_color="#1E293B",
            button_hover_color=COLORS["neon_blue"],
            height=34,
            corner_radius=8
        )
        self.combo_precision.pack(fill="x", pady=(0, 12))
        self.combo_precision.set("int8 (Rápido e Leve)")

        # 6. Checkbox Gerar SRT
        self.chk_srt = ctk.CTkCheckBox(
            right_panel,
            text="Gerar arquivo de legendas sincronizadas (.SRT)",
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["neon_blue"],
            hover_color=COLORS["neon_cyan"]
        )
        self.chk_srt.pack(anchor="w", pady=(0, 14))
        self.chk_srt.select()

        # 7. Pasta de saída
        lbl_out = ctk.CTkLabel(right_panel, text="Pasta de Saída dos Arquivos:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_out.pack(anchor="w", pady=(0, 3))

        out_row = ctk.CTkFrame(right_panel, fg_color="transparent")
        out_row.pack(fill="x", pady=(0, 12))
        out_row.grid_columnconfigure(0, weight=1)

        default_dir = str(Path.home() / "Documents")
        self.entry_out_dir = ctk.CTkEntry(
            out_row,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["card_border"],
            height=34,
            corner_radius=8
        )
        self.entry_out_dir.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.entry_out_dir.insert(0, default_dir)

        self.btn_browse = ctk.CTkButton(
            out_row,
            text="Escolher",
            width=80,
            height=34,
            corner_radius=8,
            fg_color=COLORS["btn_upload_bg"],
            hover_color=COLORS["btn_upload_hover"],
            command=self._on_browse_output
        )
        self.btn_browse.grid(row=0, column=1)

        # 8. Nome do arquivo TXT
        lbl_name = ctk.CTkLabel(right_panel, text="Nome do Arquivo TXT (sem extensão):", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_name.pack(anchor="w", pady=(0, 3))

        default_txt_name = f"Transcricao_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.entry_filename = ctk.CTkEntry(
            right_panel,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["card_border"],
            height=34,
            corner_radius=8
        )
        self.entry_filename.pack(fill="x", pady=(0, 18))
        self.entry_filename.insert(0, default_txt_name)

        # 9. Botões de Ação Final
        act_row = ctk.CTkFrame(right_panel, fg_color="transparent")
        act_row.pack(fill="x", pady=(0, 8))
        act_row.grid_columnconfigure((0, 1), weight=1)

        self.btn_transcribe = ctk.CTkButton(
            act_row,
            text="🎙️  Iniciar Transcrição",
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["btn_save_bg"],
            hover_color=COLORS["btn_save_hover"],
            border_width=1,
            border_color=COLORS["neon_blue"],
            command=self._start_transcription
        )
        self.btn_transcribe.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.btn_cancel = ctk.CTkButton(
            act_row,
            text="⏹️  Cancelar",
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["btn_clear_bg"],
            hover_color=COLORS["accent_red_hover"],
            state="disabled",
            command=self._cancel_transcription
        )
        self.btn_cancel.grid(row=0, column=1, padx=(4, 0), sticky="ew")

        self.btn_exit = ctk.CTkButton(
            right_panel,
            text="🚪  Sair do Aplicativo",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color="#1E263D",
            border_width=1,
            border_color=COLORS["card_border"],
            text_color=COLORS["text_secondary"],
            command=self._on_exit
        )
        self.btn_exit.pack(fill="x", pady=(0, 8))

    # Funções de Manipulação da Lista de Arquivos
    def _on_add_files(self):
        tipos = [
            ("Arquivos de Áudio e Vídeo", "*.mp3 *.wav *.m4a *.mp4 *.flac *.ogg *.aac *.wma"),
            ("Todos os Arquivos", "*.*")
        ]
        files = filedialog.askopenfilenames(title="Selecionar Áudios para Transcrição", filetypes=tipos)
        if files:
            for f in files:
                if f not in self.selected_files:
                    self.selected_files.append(f)
            self._refresh_files_box()

    def _on_add_folder(self):
        folder = filedialog.askdirectory(title="Selecionar Pasta com Arquivos de Áudio")
        if folder:
            scanned = scan_audio_files(folder)
            for f in scanned:
                if f not in self.selected_files:
                    self.selected_files.append(f)
            self._refresh_files_box()

    def _on_clear_files(self):
        self.selected_files.clear()
        self._refresh_files_box()

    def _refresh_files_box(self):
        self.box_files.configure(state="normal")
        self.box_files.delete("1.0", "end")
        if self.selected_files:
            summary = f"Total: {len(self.selected_files)} arquivo(s)\n" + "\n".join(self.selected_files)
            self.box_files.insert("1.0", summary)
        self.box_files.configure(state="disabled")

    def _on_browse_output(self):
        d = filedialog.askdirectory(title="Selecionar Pasta de Saída")
        if d:
            self.entry_out_dir.delete(0, "end")
            self.entry_out_dir.insert(0, d)

    def append_log(self, message: str, level: str = "INFO"):
        """Adiciona uma mensagem formatada ao console."""
        if level == "PADRAO":
            line = f"{message}\n"
        else:
            now = datetime.datetime.now().strftime("%H:%M:%S")
            line = f"[{now}] [{level}] {message}\n"

        self.log_box.insert("end", line)
        self.log_box.see("end")

    def _tick_live_timer(self):
        """Cronômetro fluido executado a cada 250ms na thread principal (tempo decorrido ao vivo segundo a segundo)."""
        if not self.is_running:
            return

        elapsed = time.time() - self._start_time

        # Contagem regressiva fluida do tempo restante
        rem_sec = max(1.0, self._estimated_remaining_seconds - elapsed)
        rem_mins, rem_secs = divmod(int(rem_sec), 60)

        # Interpolação suave do progresso visual para nunca congelar
        current_disp = max(self._current_progress_ratio, min(0.98, elapsed / max(1.0, elapsed + rem_sec)))
        self.progress_bar.set(current_disp)
        self.lbl_percent.configure(text=f"{int(current_disp * 100)}%")

        self.lbl_eta.configure(
            text=f"⏱️ Tempo Restante: ~{rem_mins:02d}:{rem_secs:02d}  (Decorrido: {format_time(elapsed)})",
            text_color=COLORS["neon_blue"]
        )

        self.after(250, self._tick_live_timer)

    def _cancel_transcription(self):
        if self.is_running:
            self.stop_event.set()
            self.append_log("Solicitação de cancelamento enviada. Aguardando finalização...", "AVISO")
            self.lbl_eta.configure(text="⏹️ Cancelamento em andamento...", text_color=COLORS["accent_red"])
            self.btn_cancel.configure(state="disabled")

    def _on_exit(self):
        if self.is_running:
            if not messagebox.askyesno("Confirmar Saída", "Uma transcrição está em andamento. Deseja realmente sair?"):
                return
            self.stop_event.set()
        self.winfo_toplevel().destroy()

    def _start_transcription(self):
        if not self.selected_files:
            messagebox.showwarning("Lista Vazia", "Por favor, adicione ao menos um arquivo ou pasta para transcrever.")
            return

        out_dir = self.entry_out_dir.get().strip()
        if not out_dir:
            messagebox.showwarning("Pasta Obrigatória", "Por favor, selecione uma pasta de saída válida.")
            return

        self.is_running = True
        self.stop_event.clear()
        self.btn_transcribe.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.mini_wave.start_animation()

        # Mapeamento de Opções em Português para valores técnicos
        model_raw = self.combo_model.get().split()[0].lower()
        dev_raw = self.combo_device.get()
        device = "cuda" if "Placa" in dev_raw else "cpu" if "Processador" in dev_raw else "auto"
        prec_raw = self.combo_precision.get().split()[0].lower()
        lang = self.entry_lang.get().strip() or None
        gen_srt = bool(self.chk_srt.get())
        custom_txt = self.entry_filename.get().strip() or None

        files_to_process = list(self.selected_files)
        total_files = len(files_to_process)

        # 1. Medição imediata da duração de todos os arquivos antes de iniciar
        self.append_log(f"Analisando duração de {total_files} arquivo(s)...", "INFO")
        file_durations = [get_audio_duration(p) for p in files_to_process]
        self._total_audio_duration = max(1.0, sum(file_durations))

        # 2. Estimativa inicial calculada imediatamente (GPU processa a ~5x real-time; CPU a ~1x real-time)
        speed_factor = 5.0 if device == "cuda" else 1.1
        self._estimated_remaining_seconds = max(3.0, self._total_audio_duration / speed_factor + 1.5)
        self._current_progress_ratio = 0.0
        self._start_time = time.time()

        # Inicia o cronômetro fluido ao vivo
        self._tick_live_timer()

        self.append_log(f"Iniciando transcrição de {format_time(self._total_audio_duration)} de áudio total...", "INFO")

        def worker():
            completed_files = 0
            completed_audio_sec = 0.0

            for idx, file_path in enumerate(files_to_process, 1):
                if self.stop_event.is_set():
                    self.after(0, lambda: self.append_log("Processo cancelado pelo usuário.", "AVISO"))
                    break

                curr_file_dur = file_durations[idx - 1]
                self.after(0, lambda p=file_path, i=idx: self.append_log(f"Processando [{i}/{total_files}]: {os.path.basename(p)} ({format_time(curr_file_dur)})", "INFO"))

                def log_cb(msg, lvl):
                    self.after(0, lambda m=msg, l=lvl: self.append_log(m, l))

                # Callback a cada segmento processado
                def seg_cb(curr_sec: float, dur_sec: float, file_ratio: float):
                    nonlocal completed_audio_sec
                    total_processed = completed_audio_sec + curr_sec
                    elapsed = time.time() - self._start_time

                    self._current_progress_ratio = min(0.99, total_processed / self._total_audio_duration)

                    # Recalibra o tempo estimado em tempo real com base na velocidade medida
                    if total_processed > 1.0 and elapsed > 1.0:
                        measured_speed = total_processed / elapsed
                        rem_audio = max(0.0, self._total_audio_duration - total_processed)
                        rec_remaining = rem_audio / max(0.1, measured_speed)
                        self._estimated_remaining_seconds = elapsed + rec_remaining

                res = WhisperEngine.transcribe(
                    audio_path=file_path,
                    output_dir=out_dir,
                    model_name=model_raw,
                    device=device,
                    compute_type=prec_raw,
                    language=lang,
                    generate_srt=gen_srt,
                    custom_txt_name=custom_txt if total_files == 1 else None,
                    stop_event=self.stop_event,
                    progress_callback=log_cb,
                    segment_progress_callback=seg_cb
                )

                if res.get("cancelled"):
                    break

                completed_audio_sec += curr_file_dur
                completed_files += 1

            total_elapsed = time.time() - self._start_time

            def finish():
                self.is_running = False
                self.mini_wave.stop_animation()
                self.btn_transcribe.configure(state="normal")
                self.btn_cancel.configure(state="disabled")

                if self.stop_event.is_set():
                    self.lbl_eta.configure(text=f"⏹️ Transcrição Cancelada (Decorrido: {format_time(total_elapsed)})", text_color=COLORS["accent_red"])
                    self.append_log("Transcrição cancelada.", "AVISO")
                else:
                    self.progress_bar.set(1.0)
                    self.lbl_percent.configure(text="100%")
                    self.lbl_eta.configure(text=f"✅ Concluído em {format_time(total_elapsed)}!", text_color=COLORS["accent_green"])
                    self.append_log("Processo concluído com êxito!", "SUCESSO")
                    messagebox.showinfo("Sucesso", f"Transcrição concluída ({completed_files} arquivo(s)) em {format_time(total_elapsed)}.\nSalvo em:\n{out_dir}")

            self.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()
