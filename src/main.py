"""
Folios Extractor - Point d'entrée principal.

Extracteur d'archives Windows minimaliste.
Usage: FoliosExtractor.exe <chemin_archive>
"""

import os
import sys
import winsound
import shutil

from utils.naming import get_destination_folder
from utils.logger import log_success, log_error, create_error_file
from utils.config import load_config
from utils.toaster import toast_success, toast_error
from extractors.zip_extractor import extract_zip, ZipExtractionError
from extractors.sevenz_extractor import extract_7z, SevenZExtractionError
from extractors.rar_extractor import extract_rar, RarExtractionError
from extractors.tar_extractor import extract_tar, TarExtractionError

# Mapping extensions -> extracteurs
EXTENSION_MAP = {
    '.zip': ('zip', extract_zip),
    '.7z': ('7z', extract_7z),
    '.rar': ('rar', extract_rar),
    '.tar': ('tar', extract_tar),
    '.tar.gz': ('tar', extract_tar),
    '.tgz': ('tar', extract_tar),
    '.tar.bz2': ('tar', extract_tar),
    '.tar.xz': ('tar', extract_tar),
}


def get_archive_type(archive_path: str):
    """
    Détermine le type d'archive et retourne l'extracteur approprié.

    Returns:
        Tuple (type_name, extractor_function) ou (None, None) si non supporté
    """
    name_lower = archive_path.lower()

    # Vérifier les extensions doubles d'abord
    for ext in ['.tar.gz', '.tar.bz2', '.tar.xz']:
        if name_lower.endswith(ext):
            return EXTENSION_MAP[ext]

    # Puis les extensions simples
    _, ext = os.path.splitext(name_lower)
    if ext in EXTENSION_MAP:
        return EXTENSION_MAP[ext]

    return None, None


def play_success_sound():
    """Joue le son Windows de succès."""
    try:
        winsound.MessageBeep(winsound.MB_OK)
    except Exception:
        pass


def open_folder(folder_path: str):
    """Ouvre le dossier dans l'explorateur Windows."""
    try:
        os.startfile(folder_path)
    except Exception:
        pass


def delete_archive(archive_path: str):
    """Envoie l'archive à la corbeille Windows."""
    try:
        from send2trash import send2trash
        send2trash(archive_path)
    except ImportError:
        # Fallback: suppression permanente si send2trash non disponible
        try:
            os.remove(archive_path)
        except Exception:
            pass
    except Exception:
        pass


def main():
    """Point d'entrée principal."""
    # Vérifier les arguments
    if len(sys.argv) < 2:
        log_error("N/A", "Aucun fichier spécifié")
        sys.exit(1)

    archive_path = sys.argv[1]

    # Vérifier que le fichier existe
    if not os.path.exists(archive_path):
        log_error(archive_path, "Fichier introuvable")
        sys.exit(1)

    if not os.path.isfile(archive_path):
        log_error(archive_path, "Ce n'est pas un fichier")
        sys.exit(1)

    # Déterminer le type d'archive
    archive_type, extractor = get_archive_type(archive_path)

    if extractor is None:
        log_error(archive_path, "Format d'archive non supporté")
        create_error_file(archive_path, "Format d'archive non supporté")
        toast_error(os.path.basename(archive_path), "Format non supporté")
        sys.exit(1)

    # Charger la configuration
    config = load_config()

    # Déterminer le dossier de destination
    dest_folder = get_destination_folder(archive_path)

    try:
        # Extraire l'archive
        success, file_count, total_size = extractor(archive_path, dest_folder)

        if success:
            # Log succès
            log_success(archive_path, dest_folder, file_count, total_size)

            # Toast de succès
            toast_success(dest_folder, file_count, total_size)

            # Son de succès
            if config.play_sound:
                play_success_sound()

            # Ouvrir le dossier
            if config.open_folder_after:
                open_folder(dest_folder)

            # Supprimer l'archive si configuré
            if config.delete_archive_after:
                delete_archive(archive_path)

            sys.exit(0)

    except (ZipExtractionError, SevenZExtractionError, RarExtractionError, TarExtractionError) as e:
        error_msg = str(e)
        log_error(archive_path, error_msg)
        create_error_file(archive_path, error_msg)
        toast_error(os.path.basename(archive_path), error_msg[:50])

        # Nettoyer le dossier de destination partiel si créé
        if os.path.exists(dest_folder):
            try:
                shutil.rmtree(dest_folder)
            except Exception:
                pass

        sys.exit(1)

    except Exception as e:
        error_msg = f"Erreur inattendue: {e}"
        log_error(archive_path, error_msg)
        create_error_file(archive_path, error_msg)
        toast_error(os.path.basename(archive_path), "Erreur inattendue")

        # Nettoyer le dossier de destination partiel si créé
        if os.path.exists(dest_folder):
            try:
                shutil.rmtree(dest_folder)
            except Exception:
                pass

        sys.exit(1)


if __name__ == '__main__':
    main()
