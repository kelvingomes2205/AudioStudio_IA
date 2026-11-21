"""
AudioStudio IA - Ponto de Entrada da Aplicação
================================================
Inicializador do AudioStudio IA estruturado sob arquitetura modular limpa.
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao sys.path para garantir importações relativas confiáveis
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from ui.app import AudioStudioApp
except ImportError as exc:
    print(f"[ERRO DE INICIALIZAÇÃO] Falha ao carregar dependências: {exc}")
    print("Certifique-se de executar 'pip install -r requirements.txt'")
    sys.exit(1)


def main():
    """Inicializa a janela principal do AudioStudio IA."""
    app = AudioStudioApp()
    app.mainloop()


if __name__ == "__main__":
    main()
