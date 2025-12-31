"""Toast notifications Windows pour Folios Extractor."""

import os


def _format_size(size_bytes: int) -> str:
    """Formate une taille en bytes en format lisible."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def toast_success(dest_folder: str, file_count: int = 0, total_size: int = 0):
    """
    Affiche un toast de succès.

    Args:
        dest_folder: Chemin du dossier de destination
        file_count: Nombre de fichiers extraits
        total_size: Taille totale en bytes
    """
    try:
        from winotify import Notification, audio

        folder_name = os.path.basename(dest_folder)

        # Construire le message avec stats
        if file_count > 0 and total_size > 0:
            stats = f"{file_count} fichiers • {_format_size(total_size)}"
            msg = f"✓ Extrait vers {folder_name}/\n{stats}"
        else:
            msg = f"✓ Extrait vers {folder_name}/"

        toast = Notification(
            app_id="Folios Extractor",
            title="Extraction terminée",
            msg=msg,
            duration="short"
        )
        toast.set_audio(audio.Silent, loop=False)
        toast.show()

    except Exception:
        pass  # Ignorer silencieusement si winotify échoue


def toast_error(archive_name: str, error_message: str):
    """
    Affiche un toast d'erreur.

    Args:
        archive_name: Nom de l'archive
        error_message: Message d'erreur court
    """
    try:
        from winotify import Notification, audio

        toast = Notification(
            app_id="Folios Extractor",
            title="Échec de l'extraction",
            msg=f"✗ {error_message}\nVoir {archive_name}.error.txt",
            duration="short"
        )
        toast.set_audio(audio.Silent, loop=False)
        toast.show()

    except Exception:
        pass  # Ignorer silencieusement si winotify échoue
