"""Extracteur pour archives RAR via UnRAR.exe."""

import os
import subprocess
import sys
from typing import Tuple


class RarExtractionError(Exception):
    """Erreur spécifique à l'extraction RAR."""
    pass


def _get_unrar_path() -> str:
    """Retourne le chemin vers UnRAR.exe."""
    # Si on est dans un .exe PyInstaller
    if getattr(sys, 'frozen', False):
        # PyInstaller extrait les fichiers dans _MEIPASS
        base_path = sys._MEIPASS
    else:
        # En développement
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    unrar_path = os.path.join(base_path, 'bin', 'UnRAR.exe')

    if not os.path.exists(unrar_path):
        raise RarExtractionError("UnRAR.exe non trouvé. Extraction RAR impossible.")

    return unrar_path


def _count_extracted_files(dest_folder: str) -> Tuple[int, int]:
    """Compte les fichiers et calcule la taille totale dans un dossier."""
    file_count = 0
    total_size = 0

    for root, dirs, files in os.walk(dest_folder):
        for f in files:
            file_count += 1
            try:
                total_size += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass

    return file_count, total_size


def extract_rar(archive_path: str, dest_folder: str) -> Tuple[bool, int, int]:
    """
    Extrait une archive RAR via UnRAR.exe.

    Args:
        archive_path: Chemin vers l'archive RAR
        dest_folder: Dossier de destination

    Returns:
        Tuple (succès, nombre_fichiers, taille_totale)

    Raises:
        RarExtractionError: Si l'extraction échoue
    """
    try:
        unrar_path = _get_unrar_path()

        # Créer le dossier de destination
        os.makedirs(dest_folder, exist_ok=True)

        # S'assurer que le chemin de destination se termine par un séparateur
        dest_with_sep = dest_folder if dest_folder.endswith(os.sep) else dest_folder + os.sep

        # Commande UnRAR:
        # x = extraire avec chemins complets
        # -o+ = écraser les fichiers existants
        # -y = répondre oui à toutes les questions
        cmd = [
            unrar_path,
            'x',
            '-o+',
            '-y',
            archive_path,
            dest_with_sep
        ]

        # Exécuter UnRAR
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )

        # Analyser le résultat
        stderr = result.stderr.lower() if result.stderr else ""
        stdout = result.stdout.lower() if result.stdout else ""

        # Vérifier les erreurs courantes
        if "password" in stderr or "password" in stdout:
            raise RarExtractionError("Archive protégée par mot de passe")

        if "corrupt" in stderr or "corrupt" in stdout:
            raise RarExtractionError("Archive RAR corrompue")

        if "cannot find" in stderr or "no such file" in stderr:
            raise RarExtractionError("Archive RAR introuvable")

        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else f"Code de retour: {result.returncode}"
            raise RarExtractionError(f"Échec de l'extraction: {error_msg}")

        # Compter les fichiers extraits
        file_count, total_size = _count_extracted_files(dest_folder)

        return True, file_count, total_size

    except subprocess.TimeoutExpired:
        raise RarExtractionError("Extraction interrompue: timeout")
    except PermissionError as e:
        raise RarExtractionError(f"Permission refusée: {e}")
    except OSError as e:
        if "No space left" in str(e) or e.errno == 28:
            raise RarExtractionError("Espace disque insuffisant")
        raise RarExtractionError(f"Erreur système: {e}")
