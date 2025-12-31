"""Gestion des noms de dossiers de destination."""

import os
from pathlib import Path

# Extensions à double (tar.gz, tar.bz2, etc.)
DOUBLE_EXTENSIONS = {'.tar.gz', '.tar.bz2', '.tar.xz', '.tgz'}


def get_archive_base_name(archive_path: str) -> str:
    """
    Retourne le nom de base de l'archive sans extension.

    Exemples:
        archive.zip -> archive
        archive.tar.gz -> archive
        projet-client.7z -> projet-client
    """
    path = Path(archive_path)
    name = path.name

    # Vérifier les extensions doubles d'abord
    name_lower = name.lower()
    for double_ext in DOUBLE_EXTENSIONS:
        if name_lower.endswith(double_ext):
            return name[:-len(double_ext)]

    # Extension simple
    return path.stem


def get_destination_folder(archive_path: str) -> str:
    """
    Retourne le chemin du dossier de destination pour l'extraction.
    Gère les conflits de noms en ajoutant _1, _2, etc.

    Exemples:
        archive.zip -> archive/
        archive.zip (si archive/ existe) -> archive_1/
    """
    archive_dir = os.path.dirname(archive_path)
    base_name = get_archive_base_name(archive_path)

    dest_folder = os.path.join(archive_dir, base_name)

    # Si le dossier n'existe pas, on le retourne directement
    if not os.path.exists(dest_folder):
        return dest_folder

    # Sinon, on cherche un nom disponible avec suffixe
    counter = 1
    while True:
        suffixed_folder = os.path.join(archive_dir, f"{base_name}_{counter}")
        if not os.path.exists(suffixed_folder):
            return suffixed_folder
        counter += 1
