import time

class CodeTimer:
    def __init__(self, name="Code Block"):
        """
        Initialisiert den Timer.
        :param name: Optionaler Name für den Codeblock, dessen Laufzeit gemessen wird.
        """
        self.name = name
        self.start_time = None
        self.end_time = None

    def start(self) -> float:
        """Startet den Timer."""
        self.start_time = time.time()
        print(f"[{self.name}] Timer gestartet...")
        return self.start_time

    def stop(self) -> float:
        """Stoppt den Timer und gibt die verstrichene Zeit aus."""
        self.end_time = time.time()
        elapsed_time = self.end_time - self.start_time
        print(f"[{self.name}] Ausführungszeit: {elapsed_time:.4f} Sekunden")
        return elapsed_time

    def __enter__(self):
        """Ermöglicht die Verwendung der Klasse mit dem 'with'-Statement."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Stoppt den Timer bei Verlassen des 'with'-Blocks."""
        return self.stop()
