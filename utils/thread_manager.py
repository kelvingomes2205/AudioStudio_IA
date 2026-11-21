"""
AudioStudio IA - Gerenciador de Threads e Concorrência Segura
==============================================================
Classes e utilitários para despacho de tarefas assíncronas em segundo plano,
comunicação segura com a thread principal do CustomTkinter e controle de cancelamento.
"""

import threading
import queue
from typing import Callable, Any, Optional


class ThreadSafeDispatcher:
    """
    Gerenciador thread-safe baseado em queue.Queue para encaminhar
    mensagens e atualizações de background para a thread da interface CustomTkinter.
    """

    def __init__(self, root_widget, poll_interval_ms: int = 50):
        self.root = root_widget
        self.poll_interval_ms = poll_interval_ms
        self.msg_queue: queue.Queue = queue.Queue()
        self._is_polling = False

    def start_polling(self):
        """Inicia a verificação periódica da fila na thread principal."""
        if not self._is_polling:
            self._is_polling = True
            self._poll()

    def stop_polling(self):
        """Interrompe a verificação da fila."""
        self._is_polling = False

    def dispatch(self, callback: Callable[..., Any], *args, **kwargs):
        """Insere uma ação na fila para execução atômica na thread da UI."""
        self.msg_queue.put((callback, args, kwargs))

    def _poll(self):
        """Consome todos os eventos pendentes da fila e agenda o próximo ciclo."""
        if not self._is_polling:
            return

        try:
            while not self.msg_queue.empty():
                callback, args, kwargs = self.msg_queue.get_nowait()
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"[ThreadSafeDispatcher] Erro ao executar callback: {e}")
                finally:
                    self.msg_queue.task_done()
        except queue.Empty:
            pass

        try:
            self.root.after(self.poll_interval_ms, self._poll)
        except Exception:
            self._is_polling = False


def run_in_thread(target_func: Callable, on_complete: Optional[Callable] = None, *args, **kwargs) -> threading.Thread:
    """
    Executa uma função em thread daemon com tratamento de conclusão seguro.
    """
    def wrapper():
        try:
            result = target_func(*args, **kwargs)
            if on_complete:
                on_complete(True, result)
        except Exception as e:
            print(f"[ThreadWorker] Exceção na thread de fundo: {e}")
            if on_complete:
                on_complete(False, e)

    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()
    return thread
