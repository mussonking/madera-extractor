"""Logging minimaliste pour Folios Extractor."""

import os
from datetime import datetime
from pathlib import Path

# Fichier log dans %TEMP%
LOG_FILE = os.path.join(os.environ.get('TEMP', '/tmp'), 'folios-extractor.log')
MAX_LOG_LINES = 100


def _rotate_log():
    """Garde seulement les MAX_LOG_LINES dernières lignes du log."""
    try:
        if not os.path.exists(LOG_FILE):
            return

        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if len(lines) > MAX_LOG_LINES:
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                f.writelines(lines[-MAX_LOG_LINES:])
    except Exception:
        pass  # Ignorer les erreurs de rotation


def _write_log(level: str, message: str):
    """Écrit une entrée dans le fichier log."""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"{timestamp} | {level} | {message}\n"

        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)

        _rotate_log()
    except Exception:
        pass  # Jamais de popup, jamais d'erreur visible


def log_success(archive_path: str, dest_folder: str, file_count: int = 0, total_size: int = 0):
    """Log une extraction réussie."""
    size_mb = total_size / (1024 * 1024) if total_size > 0 else 0
    stats = f"{file_count} fichiers, {size_mb:.1f} MB" if file_count > 0 else ""
    message = f"{archive_path} -> {dest_folder}"
    if stats:
        message += f" | {stats}"
    _write_log("SUCCESS", message)


def log_error(archive_path: str, error_message: str):
    """Log une erreur d'extraction."""
    _write_log("ERROR", f"{archive_path} | {error_message}")


def create_error_file(archive_path: str, error_message: str):
    """Crée un fichier .error.txt à côté de l'archive en cas d'échec."""
    try:
        error_file = f"{archive_path}.error.txt"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        content = f"""Folios Extractor - Erreur d'extraction
========================================
Date: {timestamp}
Archive: {archive_path}
Erreur: {error_message}
"""

        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception:
        pass  # Ignorer si on ne peut pas créer le fichier
