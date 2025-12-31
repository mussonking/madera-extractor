"""Extracteur pour archives ZIP."""

import os
import zipfile
from typing import Tuple


class ZipExtractionError(Exception):
    """Erreur spécifique à l'extraction ZIP."""
    pass


def extract_zip(archive_path: str, dest_folder: str) -> Tuple[bool, int, int]:
    """
    Extrait une archive ZIP.

    Args:
        archive_path: Chemin vers l'archive ZIP
        dest_folder: Dossier de destination

    Returns:
        Tuple (succès, nombre_fichiers, taille_totale)

    Raises:
        ZipExtractionError: Si l'extraction échoue
    """
    try:
        # Créer le dossier de destination
        os.makedirs(dest_folder, exist_ok=True)

        file_count = 0
        total_size = 0

        with zipfile.ZipFile(archive_path, 'r') as zf:
            # Vérifier l'intégrité
            bad_file = zf.testzip()
            if bad_file is not None:
                raise ZipExtractionError(f"Archive corrompue: fichier '{bad_file}' invalide")

            # Extraire tous les fichiers
            for member in zf.infolist():
                # Gérer l'encoding des noms de fichiers (UTF-8 ou CP437)
                try:
                    # Essayer d'abord avec l'encoding par défaut
                    filename = member.filename
                except UnicodeDecodeError:
                    # Fallback sur CP437 pour les vieux ZIP Windows
                    filename = member.filename.encode('cp437').decode('utf-8', errors='replace')

                # Extraire le fichier
                zf.extract(member, dest_folder)

                # Compter seulement les fichiers, pas les dossiers
                if not member.is_dir():
                    file_count += 1
                    total_size += member.file_size

        return True, file_count, total_size

    except zipfile.BadZipFile as e:
        raise ZipExtractionError(f"Archive ZIP invalide ou corrompue: {e}")
    except PermissionError as e:
        raise ZipExtractionError(f"Permission refusée: {e}")
    except OSError as e:
        if "No space left" in str(e) or e.errno == 28:
            raise ZipExtractionError("Espace disque insuffisant")
        raise ZipExtractionError(f"Erreur système: {e}")
