"""Extracteur pour archives 7z."""

import os
from typing import Tuple


class SevenZExtractionError(Exception):
    """Erreur spécifique à l'extraction 7z."""
    pass


def extract_7z(archive_path: str, dest_folder: str) -> Tuple[bool, int, int]:
    """
    Extrait une archive 7z.

    Args:
        archive_path: Chemin vers l'archive 7z
        dest_folder: Dossier de destination

    Returns:
        Tuple (succès, nombre_fichiers, taille_totale)

    Raises:
        SevenZExtractionError: Si l'extraction échoue
    """
    try:
        import py7zr
    except ImportError:
        raise SevenZExtractionError("Module py7zr non installé")

    try:
        # Créer le dossier de destination
        os.makedirs(dest_folder, exist_ok=True)

        file_count = 0
        total_size = 0

        with py7zr.SevenZipFile(archive_path, mode='r') as archive:
            # Vérifier si l'archive est protégée par mot de passe
            if archive.needs_password():
                raise SevenZExtractionError("Archive protégée par mot de passe")

            # Récupérer les infos avant extraction
            for entry in archive.list():
                if not entry.is_directory:
                    file_count += 1
                    total_size += entry.uncompressed if hasattr(entry, 'uncompressed') else 0

            # Extraire tous les fichiers
            archive.extractall(path=dest_folder)

        return True, file_count, total_size

    except py7zr.exceptions.PasswordRequired:
        raise SevenZExtractionError("Archive protégée par mot de passe")
    except py7zr.exceptions.Bad7zFile as e:
        raise SevenZExtractionError(f"Archive 7z invalide ou corrompue: {e}")
    except PermissionError as e:
        raise SevenZExtractionError(f"Permission refusée: {e}")
    except OSError as e:
        if "No space left" in str(e) or e.errno == 28:
            raise SevenZExtractionError("Espace disque insuffisant")
        raise SevenZExtractionError(f"Erreur système: {e}")
    except Exception as e:
        raise SevenZExtractionError(f"Erreur d'extraction: {e}")
