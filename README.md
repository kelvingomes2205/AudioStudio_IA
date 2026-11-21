# 🎧 AudioStudio IA — Estúdio de Voz & Transcrição

O **AudioStudio IA** é um aplicativo desktop moderno desenvolvido em Python com **CustomTkinter**, inspirado em uma estética **Cyberpunk / Neon Midnight Glassmorphism** de última geração:

1. **Conversor de Texto em Áudio (TTS):** Síntese de voz com área de texto responsiva, visualizador gráfico de onda sonora neon com gradiente suave (Ciano -> Violeta -> Magenta), seletores de voz em português, ajuste fino de velocidade e volume, e botões de ação vibrantes ("Ouvir Prévia da Voz" e "Salvar como MP3").
2. **Transcritor Whisper em Lote (STT):** Painel profissional baseado no modelo Whisper da OpenAI (`faster-whisper`), com console em tempo real à esquerda, barra de progresso neon, seleção em lote de arquivos e pastas, seleção de modelos (`tiny`, `base`, `small`, `medium`, `large-v3`), suporte a GPU/CUDA ou CPU, precisão (`int8`, `float16`, `float32`) e geração automática de legendas `.srt` e arquivos `.txt`.

---

## 🏛️ Arquitetura Modular Limpa

```
AudioStudio_IA/
│
├── main.py                  # Ponto de entrada leve (bootstrap)
├── requirements.txt         # Dependências essenciais em texto puro UTF-8
├── README.md                # Documentação do projeto
│
├── core/                    # Motores de IA e processamento pesado
│   ├── __init__.py
│   ├── tts_engine.py        # Síntese de fala (pyttsx3 com fallback senoidal)
│   └── whisper_engine.py    # Transcrição Whisper (faster-whisper, openai-whisper e SRT)
│
├── ui/                      # Camada de apresentação gráfica CustomTkinter
│   ├── __init__.py
│   ├── theme.py             # Paleta de cores Cyberpunk / Neon Midnight e fontes
│   ├── sidebar.py           # Menu lateral com seletor em pílula [TTS] / [STT]
│   ├── wave_visualizer.py   # Componente visual de onda sonora neon em Canvas
│   ├── tts_view.py          # View do Conversor de Texto em Áudio
│   ├── whisper_view.py      # View do Transcritor Whisper em Lote
│   └── app.py               # Janela raiz CTk e gerenciamento do ciclo de vida
│
└── utils/                   # Utilitários de sistema, concorrência e áudio
    ├── __init__.py
    ├── audio_utils.py       # Varredura de mídias, formatação de tempo e legendas SRT
    └── thread_manager.py    # Despachante atômico thread-safe e workers assíncronos
```

---

## 📦 Instalação das Dependências

Instale as bibliotecas essenciais listadas no [requirements.txt](file:///c:/Users/User/Documents/AudioStudio_IA/requirements.txt):

```bash
pip install -r requirements.txt
```

---

## ▶️ Como Executar

Execute o comando no terminal:

```bash
python main.py
```
