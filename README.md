# Folios Extractor

Extracteur d'archives Windows ultra-léger. Double-cliquez sur une archive, c'est extrait. Zéro UI, zéro prise de tête.

## Formats supportés

| Format | Extension | Méthode |
|--------|-----------|---------|
| ZIP | `.zip` | zipfile (stdlib) |
| 7-Zip | `.7z` | py7zr |
| RAR | `.rar` | UnRAR.exe (binaire embarqué) |
| TAR/GZ/BZ2/XZ | `.tar`, `.tar.gz`, `.tgz`, `.tar.bz2`, `.tar.xz` | tarfile (stdlib) |

## Téléchargement

Les releases compilées sont disponibles dans la section [Releases](../../releases).  
Téléchargez `FoliosExtractor.exe` — c'est tout.

## Utilisation

### Méthode 1 — Double-clic (après installation)
Associez vos archives à Folios Extractor (clic-droit → "Ouvrir avec" → sélectionner `FoliosExtractor.exe`, cocher "Toujours utiliser cette app").

### Méthode 2 — Ligne de commande
```bash
FoliosExtractor.exe mon-archive.zip
```

### Méthode 3 — Menu contextuel (installation requise)
Exécutez `Installer-FoliosExtractor.exe` pour ajouter l'option "Extraire avec Folios" au clic-droit.

## Comportement

1. Crée un dossier du même nom que l'archive (ex: `projet.zip` → `projet/`)
2. Si le dossier existe déjà, utilise `projet_1/`, `projet_2/`, etc.
3. Extrait tout le contenu dedans
4. (Optionnel) Ouvre le dossier dans l'Explorateur
5. (Optionnel) Joue un son de succès
6. (Optionnel) Envoie l'archive à la corbeille

Aucune fenêtre ne s'ouvre pendant l'extraction. Un toast Windows apparaît à la fin.

## Configuration

Fichier `folios-extractor.conf` à placer à côté de l'exécutable :

```json
{
  "open_folder_after": true,
  "delete_archive_after": false,
  "play_sound": true
}
```

| Option | Défaut | Description |
|--------|--------|-------------|
| `open_folder_after` | `true` | Ouvre le dossier extrait dans l'Explorateur |
| `delete_archive_after` | `false` | Envoie l'archive à la corbeille après extraction |
| `play_sound` | `true` | Joue le son Windows "ding" de succès |

## Installation (optionnel)

Lancez `Installer-FoliosExtractor.exe` en tant qu'administrateur. Cela :
- Copie `FoliosExtractor.exe` dans `C:\Program Files\FoliosExtractor\`
- Ajoute "Extraire avec Folios" au menu contextuel (clic-droit) pour les archives ZIP, 7z, RAR, TAR
- Enregistre Folios Extractor comme programme par défaut pour ces formats

Pour **désinstaller** : exécutez `install/uninstall-context-menu.reg`, puis supprimez le dossier `C:\Program Files\FoliosExtractor\`.

## Build depuis les sources

### Prérequis
- Python 3.11+
- [pyinstaller](https://pyinstaller.org/)
- [UnRAR](https://www.rarlab.com/rar_add.htm) (gratuit pour extraction)

### Étapes
```bash
# Installer les dépendances
pip install -r requirements.txt

# Placer UnRAR.exe dans src/bin/
# Télécharger depuis https://www.rarlab.com/rar/unrar-x64-700.exe
# Renommer en UnRAR.exe

# Build
pyinstaller --clean build.spec

# Output: dist/FoliosExtractor.exe
```

## Développement

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer les tests
python -m pytest tests/ -v
```

## Licence

MIT — voir le fichier [LICENSE](LICENSE).

## Dépendances

- [py7zr](https://github.com/miurahr/py7zr) — support 7z natif Python
- [winotify](https://github.com/Blusolvento/winotify) — toast notifications Windows
- [send2trash](https://github.com/hsoft/send2trash) — envoi à la corbeille