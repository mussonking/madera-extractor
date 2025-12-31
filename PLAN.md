# Folios Extractor - Extracteur d'Archives Windows Standalone

## Vue d'ensemble

Un utilitaire Windows minimaliste qui extrait automatiquement les archives en double-cliquant dessus. Zéro UI, config minimale, juste ça marche.

## Comportement attendu

```
Double-click sur "projet-client.zip"
    ↓
Crée automatiquement "projet-client/" dans le même dossier
    ↓
Extrait tout le contenu dedans
    ↓
Terminé (aucune fenêtre, aucun popup)
```

## Formats supportés

| Format | Extension | Méthode |
|--------|-----------|---------|
| ZIP | .zip | zipfile (stdlib) |
| 7-Zip | .7z | py7zr |
| RAR | .rar | unrar (binaire embedded) |
| TAR | .tar | tarfile (stdlib) |
| GZIP | .tar.gz, .tgz | tarfile (stdlib) |
| BZIP2 | .tar.bz2 | tarfile (stdlib) |

## Architecture technique

### Structure du projet

```
folios-extractor/
├── src/
│   ├── main.py              # Point d'entrée, routing par extension
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── zip_extractor.py
│   │   ├── sevenz_extractor.py
│   │   ├── rar_extractor.py
│   │   └── tar_extractor.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── naming.py        # Gestion noms de dossiers
│   │   ├── logger.py        # Logging minimaliste
│   │   ├── toaster.py       # Toast notifications Windows
│   │   └── config.py        # Lecture config JSON
│   └── bin/
│       └── UnRAR.exe        # Binaire unrar embedded (pour RAR)
├── tests/
│   ├── test_archives/       # Archives de test
│   └── test_extraction.py
├── .github/
│   └── workflows/
│       └── build.yml        # Auto-build Windows .exe
├── install/
│   └── context-menu.reg     # Ajoute "Extraire avec Folios" au clic-droit
├── build.spec               # Config PyInstaller
├── requirements.txt
├── folios-extractor.conf    # Config par défaut (copié avec le .exe)
└── README.md
```

### Dépendances Python

```
py7zr>=0.20.0      # Support 7z natif Python
winotify>=1.1.0    # Toast notifications Windows
send2trash>=1.8.0  # Envoi à la corbeille Windows
pyinstaller>=6.0   # Compilation en .exe
```

**Note RAR:** Utiliser le binaire UnRAR.exe officiel de rarlab.com (gratuit pour extraction). L'embedder dans le .exe via PyInstaller.

## Spécifications détaillées

### 1. Point d'entrée (main.py)

```python
# Pseudo-logique attendue:

1. Récupérer le chemin de l'archive depuis sys.argv[1]
2. Valider que le fichier existe
3. Déterminer le type d'archive par extension
4. Créer le dossier de destination (même nom sans extension)
5. Gérer les conflits de noms (ajouter _1, _2, etc.)
6. Appeler l'extracteur approprié
7. Logger succès ou erreur
8. Exit code 0 (succès) ou 1 (erreur)
```

### 2. Gestion des noms de dossiers (naming.py)

**Règles:**
- `archive.zip` → `archive/`
- `archive.tar.gz` → `archive/`
- Si `archive/` existe déjà → `archive_1/`
- Si `archive_1/` existe → `archive_2/`
- Caractères spéciaux: garder tels quels (Windows les gère)

### 3. Extracteurs

Chaque extracteur doit:
- Accepter: `(archive_path: str, dest_folder: str)`
- Retourner: `bool` (succès/échec)
- Lever des exceptions explicites si problème

**ZIP:**
- Utiliser `zipfile` de la stdlib
- Gérer encoding UTF-8 et CP437 pour les noms de fichiers

**7Z:**
- Utiliser `py7zr`
- Supporter archives protégées par mot de passe → skip avec log

**RAR:**
- Appeler UnRAR.exe via subprocess
- Commande: `UnRAR.exe x -o+ "archive.rar" "dest_folder/"`
- Capturer stderr pour erreurs

**TAR/GZIP/BZIP2:**
- Utiliser `tarfile` de la stdlib
- Détecter automatiquement la compression

### 4. Toast Notifications (Windows)

**Librairie:** `winotify` (légère, pure Python, pas de dépendances)

**Comportement:**
- Succès: Toast vert avec "✓ Extrait vers archive/"
- Erreur: Toast rouge avec message court
- Durée: 3 secondes, auto-dismiss
- Silencieux (pas de son)

**Exemple visuel (avec stats):**
```
┌─────────────────────────────┐
│ Folios Extractor            │
│ ✓ Extrait vers projet/      │
│ 47 fichiers • 12.3 MB       │
└─────────────────────────────┘
```

**En cas d'erreur:**
```
┌─────────────────────────────┐
│ Folios Extractor            │
│ ✗ Échec: archive corrompue  │
│ Voir projet.zip.error.txt   │
└─────────────────────────────┘
```

**Note:** Si winotify échoue (vieux Windows, etc.), ignorer silencieusement. Le toast est un bonus, pas critique.

### 5. Fichier de configuration (config.py)

**Fichier:** `folios-extractor.conf` (même dossier que le .exe)

```json
{
  "open_folder_after": true,
  "delete_archive_after": false,
  "play_sound": true
}
```

**Comportement:**
- `open_folder_after`: Ouvre Explorer sur le dossier extrait après succès
- `delete_archive_after`: Envoie l'archive à la corbeille Windows après succès
- `play_sound`: Joue le son Windows "ding" de succès

**Si fichier absent:** Utiliser les defaults (open=true, delete=false, sound=true)

**Lecture:** Au démarrage, chercher le .conf à côté du .exe. JSON simple, pas de validation complexe.

### 6. Context Menu Windows (context-menu.reg)

Ajoute l'option "Extraire avec Folios" au clic-droit sur les archives.

```reg
Windows Registry Editor Version 5.00

; ZIP
[HKEY_CLASSES_ROOT\.zip\shell\FoliosExtract]
@="Extraire avec Folios"

[HKEY_CLASSES_ROOT\.zip\shell\FoliosExtract\command]
@="\"C:\\Program Files\\FoliosExtractor\\FoliosExtractor.exe\" \"%1\""

; 7Z
[HKEY_CLASSES_ROOT\.7z\shell\FoliosExtract]
@="Extraire avec Folios"

[HKEY_CLASSES_ROOT\.7z\shell\FoliosExtract\command]
@="\"C:\\Program Files\\FoliosExtractor\\FoliosExtractor.exe\" \"%1\""

; RAR
[HKEY_CLASSES_ROOT\.rar\shell\FoliosExtract]
@="Extraire avec Folios"

[HKEY_CLASSES_ROOT\.rar\shell\FoliosExtract\command]
@="\"C:\\Program Files\\FoliosExtractor\\FoliosExtractor.exe\" \"%1\""

; TAR.GZ
[HKEY_CLASSES_ROOT\.tar.gz\shell\FoliosExtract]
@="Extraire avec Folios"

[HKEY_CLASSES_ROOT\.tar.gz\shell\FoliosExtract\command]
@="\"C:\\Program Files\\FoliosExtractor\\FoliosExtractor.exe\" \"%1\""
```

**Note:** L'utilisateur doit éditer le chemin si le .exe est ailleurs. Fournir aussi un `uninstall-context-menu.reg` pour retirer les entrées.

### 7. Logging (logger.py)

**Fichier log:** `%TEMP%/quickextract.log`

**Format:**
```
2024-01-15 14:32:01 | SUCCESS | C:\Users\X\archive.zip → C:\Users\X\archive\
2024-01-15 14:33:15 | ERROR | C:\Users\X\broken.rar | Archive corrompue
```

**Règles:**
- Rotation: garder seulement les 100 dernières lignes
- Pas de popup, jamais
- En cas d'erreur critique: créer `archive.zip.error.txt` à côté de l'archive

### 8. Gestion des erreurs

| Erreur | Comportement |
|--------|--------------|
| Fichier n'existe pas | Log + exit 1 |
| Format non supporté | Log + exit 1 |
| Archive corrompue | Log + créer fichier .error.txt + exit 1 |
| Permissions insuffisantes | Log + exit 1 |
| Espace disque insuffisant | Log + exit 1 |
| Mot de passe requis | Log "password protected, skipped" + exit 1 |

## GitHub Actions - Auto-build

### .github/workflows/build.yml

```yaml
name: Build Windows Executable

on:
  push:
    tags:
      - 'v*'  # Trigger sur les tags de version (v1.0.0, v1.1.0, etc.)
  workflow_dispatch:  # Permet de trigger manuellement

jobs:
  build:
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Download UnRAR
        run: |
          curl -L -o unrar.exe https://www.rarlab.com/rar/unrar-x64-700.exe
          mkdir -p src/bin
          move unrar.exe src/bin/UnRAR.exe

      - name: Build executable
        run: pyinstaller build.spec

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: FoliosExtractor
          path: dist/FoliosExtractor.exe

      - name: Create Release
        if: startsWith(github.ref, 'refs/tags/')
        uses: softprops/action-gh-release@v1
        with:
          files: |
            dist/FoliosExtractor.exe
            install/context-menu.reg
            folios-extractor.conf
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Usage:**
1. Push un tag: `git tag v1.0.0 && git push --tags`
2. GitHub build automatiquement le .exe
3. Release créée avec le .exe + fichiers config

## Build PyInstaller

### build.spec

```python
# Points clés pour le spec file:

- onefile=True (un seul .exe)
- console=False (pas de fenêtre console)
- Inclure UnRAR.exe dans datas
- Inclure folios-extractor.conf dans datas
- UPX compression si disponible
- Icon personnalisé (optionnel)
- Name: "FoliosExtractor"
```

### Commande de build

```bash
pyinstaller --clean build.spec
```

**Output attendu:** `dist/FoliosExtractor.exe` (~15-25 MB)

## Association fichiers Windows

**Option 1 - Manuel:**
1. Clic-droit sur un .zip → "Ouvrir avec"
2. Choisir FoliosExtractor.exe
3. Cocher "Toujours utiliser cette app"

**Option 2 - Context Menu (recommandé):**
1. Double-cliquer sur `context-menu.reg`
2. Accepter l'ajout au registre
3. Clic-droit sur n'importe quelle archive → "Extraire avec Folios"

## Plan de tests

### Archives de test à créer

```
test_archives/
├── simple.zip           # Cas basique
├── simple.7z            # Test py7zr
├── simple.rar           # Test UnRAR
├── nested.tar.gz        # Double compression
├── spëcîal-çhàrs.zip    # Caractères spéciaux
├── corrupted.zip        # Archive cassée (tronquée)
├── password.rar         # Protégée par mot de passe
├── empty.zip            # Archive vide
└── huge_names.zip       # Fichiers avec noms très longs
```

### Cas de test

1. **Happy path:** Extraction normale de chaque format
2. **Conflit de nom:** Extraire 2x la même archive → doit créer `_1`
3. **Caractères spéciaux:** Vérifier que les accents passent
4. **Archive corrompue:** Doit créer .error.txt, pas crasher
5. **Permissions:** Tester dans un dossier read-only
6. **Chemin avec espaces:** `C:\Program Files\test archive.zip`
7. **Chemin réseau:** `\\server\share\archive.zip` (optionnel)

## Checklist finale

### Core
- [ ] Extraction ZIP fonctionne
- [ ] Extraction 7z fonctionne
- [ ] Extraction RAR fonctionne
- [ ] Extraction TAR/GZIP fonctionne
- [ ] Gestion conflits de noms

### UX
- [ ] Toast succès avec stats (fichiers + taille)
- [ ] Toast erreur s'affiche
- [ ] Son Windows "ding" au succès
- [ ] Ouvre le dossier après extraction
- [ ] Context menu "Extraire avec Folios" fonctionne

### Config
- [ ] Lecture folios-extractor.conf fonctionne
- [ ] Defaults si fichier absent
- [ ] Option delete_archive_after fonctionne

### Infra
- [ ] Logging dans %TEMP%
- [ ] Fichier .error.txt créé si échec
- [ ] Build en .exe single-file
- [ ] GitHub Actions build fonctionne
- [ ] Release auto avec .exe + .reg + .conf
- [ ] Taille < 30 MB
- [ ] Testé sur Windows 10/11

## Notes pour le développeur

1. **UnRAR.exe licensing:** C'est gratuit pour extraction seulement. Télécharger depuis rarlab.com/rar_add.htm

2. **py7zr:** Attention, certaines archives 7z avec encryption AES peuvent poser problème. Tester.

3. **Encodings:** Windows utilise souvent CP1252 ou CP437 dans les vieux ZIP. Prévoir fallback.

4. **Antivirus:** Certains AV flag les .exe PyInstaller. Signer le binaire si possible, sinon c'est normal.

5. **Path length:** Windows a une limite de 260 chars. Utiliser le prefix `\\?\` si nécessaire pour les chemins longs.

6. **Son Windows:** Utiliser `winsound.MessageBeep(winsound.MB_OK)` - stdlib, pas de dépendance.

7. **Ouvrir Explorer:** `os.startfile(folder_path)` ou `subprocess.run(['explorer', folder_path])`

8. **Corbeille:** Utiliser `send2trash` (pip) pour envoyer à la corbeille proprement au lieu de delete permanent.

9. **Context menu uninstall:** Fournir `uninstall-context-menu.reg` qui supprime les clés registry ajoutées.
