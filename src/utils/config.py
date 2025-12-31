"""Gestion de la configuration de Folios Extractor."""

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Configuration de l'extracteur."""
    open_folder_after: bool = True
    delete_archive_after: bool = False
    play_sound: bool = True


def _get_config_path() -> str:
    """Retourne le chemin du fichier de configuration."""
    # Si on est dans un .exe PyInstaller
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        # En développement, chercher à la racine du projet
        exe_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    return os.path.join(exe_dir, 'folios-extractor.conf')


def load_config() -> Config:
    """
    Charge la configuration depuis le fichier .conf.
    Retourne les valeurs par défaut si le fichier n'existe pas ou est invalide.
    """
    config = Config()
    config_path = _get_config_path()

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if 'open_folder_after' in data:
                config.open_folder_after = bool(data['open_folder_after'])
            if 'delete_archive_after' in data:
                config.delete_archive_after = bool(data['delete_archive_after'])
            if 'play_sound' in data:
                config.play_sound = bool(data['play_sound'])
    except Exception:
        pass  # Utiliser les defaults en cas d'erreur

    return config
