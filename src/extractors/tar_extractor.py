"""Extracteur pour archives TAR (et variantes gzip, bzip2, xz)."""

import os
import tarfile
from typing import Tuple


class TarExtractionError(Exception):
    """Erreur spécifique à l'extraction TAR."""
    pass


def extract_tar(archive_path: str, dest_folder: str) -> Tuple[bool, int, int]:
    """
    Extrait une archive TAR (ou tar.gz, tar.bz2, tar.xz, tgz).

    Args:
        archive_path: Chemin vers l'archive TAR
        dest_folder: Dossier de destination

    Returns:
        Tuple (succès, nombre_fichiers, taille_totale)

    Raises:
        TarExtractionError: Si l'extraction échoue
    """
    try:
        # Créer le dossier de destination
        os.makedirs(dest_folder, exist_ok=True)

        file_count = 0
        total_size = 0

        # tarfile détecte automatiquement la compression (gz, bz2, xz)
        with tarfile.open(archive_path, 'r:*') as tar:
            # Sécurité: filtrer les chemins dangereux (path traversal)
            members = []
            for member in tar.getmembers():
                # Vérifier les chemins absolus ou avec ../
                if member.name.startswith('/') or '..' in member.name:
                    continue  # Skip fichiers dangereux

                members.append(member)

                if member.isfile():
                    file_count += 1
                    total_size += member.size

            # Extraire les fichiers sécurisés
            tar.extractall(path=dest_folder, members=members)

        return True, file_count, total_size

    except tarfile.ReadError as e:
        raise TarExtractionError(f"Archive TAR invalide ou corrompue: {e}")
    except tarfile.CompressionError as e:
        raise TarExtractionError(f"Erreur de décompression: {e}")
    except PermissionError as e:
        raise TarExtractionError(f"Permission refusée: {e}")
    except OSError as e:
        if "No space left" in str(e) or e.errno == 28:
            raise TarExtractionError("Espace disque insuffisant")
        raise TarExtractionError(f"Erreur système: {e}")
