"""
AudioStudio IA - Componente Visualizador de Onda Sonora (Waveform)
===================================================================
Renderiza a forma de onda de áudio estilizada com gradiente neon (Ciano -> Violeta -> Magenta),
exatamente como no modelo visual de referência do estúdio.
"""

import math
import tkinter as tk
import customtkinter as ctk
from typing import List, Tuple
from ui.theme import COLORS


def interpolate_rgb(c1: Tuple[int, int, int], c2: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """Interpola linearmente entre duas cores RGB."""
    return (
        int(c1[0] + (c2[0] - c1[0]) * factor),
        int(c1[1] + (c2[1] - c1[1]) * factor),
        int(c1[2] + (c2[2] - c1[2]) * factor)
    )


def get_gradient_color(ratio: float) -> str:
    """
    Gera o gradiente de cores da onda sonora:
    Ciano Neon (#00D2FF) -> Azul (#3B82F6) -> Violeta (#8B5CF6) -> Magenta (#D946EF)
    """
    c_cyan = (0, 210, 255)
    c_blue = (59, 130, 246)
    c_violet = (139, 92, 246)
    c_magenta = (217, 70, 239)

    ratio = max(0.0, min(1.0, ratio))
    if ratio <= 0.33:
        f = ratio / 0.33
        rgb = interpolate_rgb(c_cyan, c_blue, f)
    elif ratio <= 0.66:
        f = (ratio - 0.33) / 0.33
        rgb = interpolate_rgb(c_blue, c_violet, f)
    else:
        f = (ratio - 0.66) / 0.34
        rgb = interpolate_rgb(c_violet, c_magenta, f)

    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


class WaveVisualizer(ctk.CTkFrame):
    """Componente gráfico de onda de áudio neon desenhado em Canvas."""

    def __init__(self, master, height: int = 180, num_bars: int = 68, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.height = height
        self.num_bars = num_bars
        self.is_animating = False
        self._anim_phase = 0.0

        # Canvas nativo para alta performance gráfica e bordas arredondadas
        self.canvas = tk.Canvas(
            self,
            height=self.height,
            bg=COLORS["input_bg"],
            highlightthickness=1,
            highlightbackground=COLORS["card_border"]
        )
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)
        self.canvas.bind("<Configure>", self._on_resize)

        # Dados da forma de onda estática (distribuição senoidal natural)
        self._base_amplitudes: List[float] = self._generate_base_amplitudes()

    def _generate_base_amplitudes(self) -> List[float]:
        """Gera a silhueta da onda de áudio exibida no modelo de referência."""
        amplitudes = []
        for i in range(self.num_bars):
            t = i / float(self.num_bars)
            # Combinação harmônica para formar picos e vales elegantes
            env = math.sin(math.pi * t)
            harmonics = (
                0.5 * math.sin(t * 14.0) +
                0.3 * math.cos(t * 22.0) +
                0.2 * math.sin(t * 7.0)
            )
            amp = env * (0.25 + 0.75 * abs(harmonics))
            amplitudes.append(max(0.08, min(0.95, amp)))
        return amplitudes

    def _on_resize(self, event=None):
        self.redraw()

    def redraw(self, amplitudes: List[float] = None):
        """Redesenha todas as barras de frequência com o gradiente neon."""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 10 or height <= 10:
            width = 600
            height = self.height

        amps = amplitudes or self._base_amplitudes
        total_bars = len(amps)
        spacing = width / float(total_bars)
        bar_width = max(2.5, spacing * 0.45)
        center_y = height / 2.0

        for i, amp in enumerate(amps):
            x = (i + 0.5) * spacing
            bar_h = amp * (height * 0.42)
            y1 = center_y - bar_h
            y2 = center_y + bar_h
            color = get_gradient_color(i / float(total_bars))

            # Desenha barra vertical com pontas arredondadas
            self.canvas.create_line(
                x, y1, x, y2,
                fill=color,
                width=bar_width,
                capstyle=tk.ROUND
            )

    def start_animation(self):
        """Inicia animação dinâmica de ondas (durante reprodução/transcrição)."""
        if not self.is_animating:
            self.is_animating = True
            self._animate_step()

    def stop_animation(self):
        """Interrompe animação e restaura a silhueta da onda estática."""
        self.is_animating = False
        self.redraw()

    def _animate_step(self):
        if not self.is_animating:
            return

        self._anim_phase += 0.22
        dynamic_amps = []
        for i, base in enumerate(self._base_amplitudes):
            # Oscilação senoidal suave baseada no tempo
            mod = 0.5 + 0.5 * math.sin(self._anim_phase + i * 0.3)
            dynamic_amps.append(max(0.06, base * (0.4 + 0.6 * mod)))

        self.redraw(dynamic_amps)
        self.after(45, self._animate_step)
