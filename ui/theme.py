"""
AudioStudio IA - Paleta Visual e Constantes de Tema
=====================================================
Definições de cores e fontes no estilo Cyberpunk / Neon Glassmorphism Dark,
reproduzindo com fidelidade estética o modelo visual de referência do estúdio.
"""

COLORS = {
    # Superfícies e Fundos Deep Midnight
    "bg_dark": "#0B0F19",             # Fundo principal escuro profundo
    "sidebar_bg": "#0E1322",          # Fundo da barra lateral
    "card_bg": "#131828",             # Fundo dos cartões em vidro escuro
    "card_border": "#1E293B",         # Borda sutil dos cartões
    "card_border_glow": "#2A3756",    # Borda em destaque suave
    "input_bg": "#0A0E17",            # Fundo interno das caixas de texto e entradas

    # Cores de Acento Neon (Gradiente Ciano a Violeta)
    "neon_cyan": "#00D2FF",           # Ciano neon elétrico
    "neon_blue": "#38BDF8",           # Azul claro neon
    "neon_violet": "#8B5CF6",         # Violeta neon
    "neon_magenta": "#D946EF",        # Rosa / Magenta neon

    # Botões Específicos do Design
    "btn_preview_bg": "#141A2E",       # Fundo translúcido do botão Ouvir Prévia
    "btn_preview_border": "#8B5CF6",   # Borda violeta brilhante
    "btn_preview_hover": "#1E2745",    # Hover do botão Ouvir Prévia
    "btn_preview_text": "#38BDF8",    # Texto ciano com alto contraste

    "btn_save_bg": "#0284C7",          # Fundo ciano/azul do botão Salvar MP3
    "btn_save_border": "#38BDF8",      # Borda ciano neon
    "btn_save_hover": "#0EA5E9",       # Hover vibrante
    "btn_save_text": "#FFFFFF",        # Texto branco puro

    "btn_upload_bg": "#0284C7",        # Botão Carregar Arquivo
    "btn_upload_hover": "#0EA5E9",
    "btn_clear_bg": "#182035",         # Botão Limpar Texto
    "btn_clear_hover": "#222D4A",
    "btn_clear_border": "#283556",

    # Textos e Legibilidade
    "text_primary": "#FFFFFF",         # Branco puro para títulos
    "text_secondary": "#94A3B8",       # Cinza claro para subtítulos
    "text_muted": "#64748B",           # Cinza escuro para metadados e contadores

    # Alertas e Status
    "accent_green": "#10B981",         # Verde neon para módulo ativo/pronto
    "accent_red": "#EF4444",           # Vermelho para cancelamento
    "accent_red_hover": "#DC2626",
    "accent_gold": "#F59E0B"           # Amarelo/âmbar para avisos
}

FONTS = {
    "app_title": ("Segoe UI", 18, "bold"),
    "page_title": ("Segoe UI", 21, "bold"),
    "subtitle": ("Segoe UI", 12),
    "section_title": ("Segoe UI", 13, "bold"),
    "body": ("Segoe UI", 13),
    "caption": ("Segoe UI", 11),
    "console": ("Consolas", 12)
}
