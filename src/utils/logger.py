"""
Logger centralisé pour l'application
"""
import logging
from datetime import datetime
from typing import List


class FactCheckerLogger:
    """Logger personnalisé pour le fact-checker"""

    def __init__(self, name: str = "FactChecker", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Handler pour la console
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Logs pour export
        self.logs: List[str] = []

    def log(self, message: str, level: str = "INFO"):
        """Ajoute un log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)

        if level == "INFO":
            self.logger.info(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "DEBUG":
            self.logger.debug(message)

    def get_logs(self) -> List[str]:
        """Retourne tous les logs"""
        return self.logs

    def clear_logs(self):
        """Efface les logs"""
        self.logs = []
