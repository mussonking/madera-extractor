"""
Folios Extractor - Installateur automatique.

Ce script:
1. Copie FoliosExtractor.exe dans Program Files
2. Ajoute le menu contextuel Windows (clic-droit)
3. Affiche un message de confirmation

Usage: Lancer en tant qu'administrateur
"""

import os
import sys
import shutil
import winreg
import ctypes


def is_admin():
    """Vérifie si on a les droits administrateur."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_install_dir():
    """Retourne le dossier d'installation."""
    return r"C:\Program Files\FoliosExtractor"


def get_exe_source():
    """Retourne le chemin du .exe source (embarqué dans l'installateur)."""
    if getattr(sys, 'frozen', False):
        # Si on est dans un .exe PyInstaller, les fichiers sont dans _MEIPASS
        return os.path.join(sys._MEIPASS, "FoliosExtractor.exe")
    else:
        # En développement
        return os.path.join(os.path.dirname(__file__), "..", "dist", "FoliosExtractor.exe")


def get_conf_source():
    """Retourne le chemin du fichier de config source."""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "folios-extractor.conf")
    else:
        return os.path.join(os.path.dirname(__file__), "..", "folios-extractor.conf")


def install_exe():
    """Copie le .exe dans Program Files."""
    install_dir = get_install_dir()
    exe_source = get_exe_source()
    exe_dest = os.path.join(install_dir, "FoliosExtractor.exe")
    conf_source = get_conf_source()
    conf_dest = os.path.join(install_dir, "folios-extractor.conf")

    # Créer le dossier
    os.makedirs(install_dir, exist_ok=True)

    # Copier le .exe
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, exe_dest)
    else:
        raise FileNotFoundError(f"FoliosExtractor.exe introuvable: {exe_source}")

    # Copier le fichier de config s'il existe
    if os.path.exists(conf_source):
        shutil.copy2(conf_source, conf_dest)
    else:
        # Créer un fichier de config par défaut
        with open(conf_dest, 'w') as f:
            f.write('{\n  "open_folder_after": true,\n  "delete_archive_after": false,\n  "play_sound": true\n}\n')

    return exe_dest


def get_progid_for_extension(ext):
    """Trouve le ProgID associé à une extension (ex: .zip -> CompressedFolder)."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ext)
        progid, _ = winreg.QueryValueEx(key, "")
        winreg.CloseKey(key)
        return progid if progid else None
    except:
        return None


def add_to_key(key_path, exe_path):
    """Ajoute l'entrée de menu contextuel à une clé donnée."""
    try:
        # Créer la clé pour le shell
        shell_path = f"{key_path}\\shell\\FoliosExtract"
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, shell_path)
        winreg.SetValue(key, "", winreg.REG_SZ, "Extraire avec Folios")
        winreg.CloseKey(key)

        # Créer la commande
        cmd_path = f"{shell_path}\\command"
        cmd_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, cmd_path)
        winreg.SetValue(cmd_key, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
        winreg.CloseKey(cmd_key)
        return True
    except Exception as e:
        return False


def register_as_default_handler(exe_path):
    """Enregistre Folios Extractor comme programme par défaut pour les archives."""

    extensions = ['.zip', '.7z', '.rar', '.tar', '.tgz', '.tar.gz', '.tar.bz2', '.gz', '.bz2', '.xz']
    progid = "FoliosExtractor.Archive"

    # 1. Créer notre ProgID
    try:
        # Créer la clé principale du ProgID
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, progid)
        winreg.SetValue(key, "", winreg.REG_SZ, "Archive Folios Extractor")
        winreg.CloseKey(key)

        # Ajouter l'icône (utilise l'icône du .exe)
        icon_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{progid}\\DefaultIcon")
        winreg.SetValue(icon_key, "", winreg.REG_SZ, f'"{exe_path}",0')
        winreg.CloseKey(icon_key)

        # Créer la commande shell\open\command
        shell_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{progid}\\shell\\open")
        winreg.SetValue(shell_key, "", winreg.REG_SZ, "Extraire avec Folios")
        winreg.CloseKey(shell_key)

        cmd_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{progid}\\shell\\open\\command")
        winreg.SetValue(cmd_key, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
        winreg.CloseKey(cmd_key)

    except Exception as e:
        raise Exception(f"Impossible de créer le ProgID: {e}")

    # 2. Associer chaque extension à notre ProgID
    for ext in extensions:
        try:
            # Créer/modifier la clé de l'extension
            ext_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ext)

            # Sauvegarder l'ancien handler (pour désinstallation future)
            try:
                old_progid, _ = winreg.QueryValueEx(ext_key, "")
                if old_progid and old_progid != progid:
                    winreg.SetValueEx(ext_key, "FoliosExtractor_Backup", 0, winreg.REG_SZ, old_progid)
            except:
                pass

            # Définir notre ProgID comme handler par défaut
            winreg.SetValue(ext_key, "", winreg.REG_SZ, progid)
            winreg.CloseKey(ext_key)

        except Exception:
            pass  # Continuer avec les autres extensions

    # 3. Notifier Windows du changement (refresh des icônes)
    try:
        from ctypes import windll
        SHCNE_ASSOCCHANGED = 0x08000000
        SHCNF_IDLIST = 0x0000
        windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)
    except:
        pass


def add_context_menu(exe_path):
    """Ajoute aussi le menu contextuel comme option secondaire."""
    extensions = ['.zip', '.7z', '.rar', '.tar', '.tgz', '.gz', '.bz2', '.xz']

    for ext in extensions:
        # Via SystemFileAssociations (apparaît même si autre programme par défaut)
        add_to_key(f"SystemFileAssociations\\{ext}", exe_path)


def show_message(title, message, icon=0x40):
    """Affiche une boîte de dialogue Windows."""
    ctypes.windll.user32.MessageBoxW(0, message, title, icon)


def main():
    # Vérifier les droits admin
    if not is_admin():
        # Relancer en tant qu'admin
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)

    try:
        # Installer le .exe
        exe_path = install_exe()

        # Enregistrer comme handler par défaut (double-clic = extraction)
        register_as_default_handler(exe_path)

        # Ajouter aussi le menu contextuel
        add_context_menu(exe_path)

        # Message de succès
        show_message(
            "Folios Extractor",
            "Installation terminée !\n\n"
            "Double-cliquez sur n'importe quelle archive\n"
            "(ZIP, 7z, RAR, TAR) pour l'extraire automatiquement.",
            0x40  # MB_ICONINFORMATION
        )

    except Exception as e:
        show_message(
            "Folios Extractor - Erreur",
            f"Erreur lors de l'installation:\n{e}",
            0x10  # MB_ICONERROR
        )
        sys.exit(1)


if __name__ == '__main__':
    main()
