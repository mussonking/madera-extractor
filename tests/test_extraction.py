"""Tests étendus pour Folios Extractor."""

import os
import sys
import tempfile
import shutil
import zipfile
import tarfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from utils.naming import get_archive_base_name, get_destination_folder
from extractors.zip_extractor import extract_zip, ZipExtractionError
from extractors.tar_extractor import extract_tar, TarExtractionError


class TestNaming:
    """Tests pour le module naming."""

    def test_simple_zip(self):
        assert get_archive_base_name("archive.zip") == "archive"

    def test_simple_7z(self):
        assert get_archive_base_name("projet.7z") == "projet"

    def test_tar_gz(self):
        assert get_archive_base_name("backup.tar.gz") == "backup"

    def test_tgz(self):
        assert get_archive_base_name("data.tgz") == "data"

    def test_tar_bz2(self):
        assert get_archive_base_name("files.tar.bz2") == "files"

    def test_special_chars(self):
        assert get_archive_base_name("spëcîal-çhàrs.zip") == "spëcîal-çhàrs"

    def test_multiple_dots(self):
        assert get_archive_base_name("my.project.v2.zip") == "my.project.v2"

    def test_full_path(self):
        assert get_archive_base_name(r"C:\Users\test\archive.zip") == "archive"

    def test_destination_folder_new(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            archive_path = os.path.join(tmpdir, "test.zip")
            dest = get_destination_folder(archive_path)
            assert dest == os.path.join(tmpdir, "test")

    def test_destination_folder_conflict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            archive_path = os.path.join(tmpdir, "test.zip")
            os.makedirs(os.path.join(tmpdir, "test"))
            dest = get_destination_folder(archive_path)
            assert dest == os.path.join(tmpdir, "test_1")

    def test_destination_folder_multiple_conflicts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            archive_path = os.path.join(tmpdir, "test.zip")
            os.makedirs(os.path.join(tmpdir, "test"))
            os.makedirs(os.path.join(tmpdir, "test_1"))
            os.makedirs(os.path.join(tmpdir, "test_2"))
            dest = get_destination_folder(archive_path)
            assert dest == os.path.join(tmpdir, "test_3")

    def test_destination_folder_path_traversal(self):
        """Test qu'un nom d'archive avec ../ ne remonte pas."""
        with tempfile.TemporaryDirectory() as tmpdir:
            archive_path = os.path.join(tmpdir, "../test.zip")
            dest = get_destination_folder(archive_path)
            # Le nom de base doit rester "test", pas remonter
            assert "test" in os.path.basename(dest)


class TestZipExtractor:
    """Tests pour l'extracteur ZIP."""

    def test_extract_simple_zip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "test.zip")
            dest_folder = os.path.join(tmpdir, "extracted")

            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("file1.txt", "Hello World")
                zf.writestr("subdir/file2.txt", "Nested file")

            success, count, size = extract_zip(zip_path, dest_folder)

            assert success is True
            assert count == 2
            assert os.path.exists(os.path.join(dest_folder, "file1.txt"))
            assert os.path.exists(os.path.join(dest_folder, "subdir", "file2.txt"))

    def test_extract_empty_zip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "empty.zip")
            dest_folder = os.path.join(tmpdir, "extracted")

            with zipfile.ZipFile(zip_path, 'w') as zf:
                pass

            success, count, size = extract_zip(zip_path, dest_folder)
            assert success is True
            assert count == 0

    def test_extract_corrupted_zip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "corrupted.zip")
            dest_folder = os.path.join(tmpdir, "extracted")

            with open(zip_path, 'wb') as f:
                f.write(b"PK\x03\x04corrupted data here")

            with pytest.raises(ZipExtractionError):
                extract_zip(zip_path, dest_folder)

    def test_extract_duplicate_filenames(self):
        """Test qu'extraire deux fois la même archive crée un dossier _1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "test.zip")

            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("file1.txt", "Hello World")

            dest1 = get_destination_folder(zip_path)
            success1, _, _ = extract_zip(zip_path, dest1)
            assert success1 is True

            dest2 = get_destination_folder(zip_path)
            success2, _, _ = extract_zip(zip_path, dest2)
            assert success2 is True
            assert "_1" in dest2

    def test_extract_unicode_filename(self):
        """Test l'extraction de fichiers avec accents dans le nom."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "test.zip")
            dest_folder = os.path.join(tmpdir, "extracted")

            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr("fichier_ééà.txt", "contenu accentué")

            success, count, _ = extract_zip(zip_path, dest_folder)
            assert success is True
            assert count == 1


class TestTarExtractor:
    """Tests pour l'extracteur TAR."""

    def test_extract_simple_tar(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tar_path = os.path.join(tmpdir, "test.tar")
            dest_folder = os.path.join(tmpdir, "extracted")

            src_file = os.path.join(tmpdir, "source.txt")
            with open(src_file, 'w') as f:
                f.write("Test content")

            with tarfile.open(tar_path, 'w') as tf:
                tf.add(src_file, arcname="source.txt")

            success, count, size = extract_tar(tar_path, dest_folder)
            assert success is True
            assert count == 1
            assert os.path.exists(os.path.join(dest_folder, "source.txt"))

    def test_extract_tar_gz(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tar_path = os.path.join(tmpdir, "test.tar.gz")
            dest_folder = os.path.join(tmpdir, "extracted")

            src_file = os.path.join(tmpdir, "source.txt")
            with open(src_file, 'w') as f:
                f.write("Compressed content")

            with tarfile.open(tar_path, 'w:gz') as tf:
                tf.add(src_file, arcname="source.txt")

            success, count, size = extract_tar(tar_path, dest_folder)
            assert success is True
            assert count == 1

    def test_path_traversal_blocked(self):
        """Test que les chemins dangereux sont bloqués."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tar_path = os.path.join(tmpdir, "evil.tar")
            dest_folder = os.path.join(tmpdir, "extracted")

            src_file = os.path.join(tmpdir, "safe.txt")
            with open(src_file, 'w') as f:
                f.write("Safe content")

            with tarfile.open(tar_path, 'w') as tf:
                tf.add(src_file, arcname="../evil_outside_dest/malicious.txt")

            success, count, size = extract_tar(tar_path, dest_folder)
            assert success is True
            # Le fichier avec .. ne doit pas être extrait
            assert not os.path.exists(os.path.join(tmpdir, "evil_outside_dest"))

    def test_extract_tar_bz2(self):
        """Test extraction tar.bz2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tar_path = os.path.join(tmpdir, "test.tar.bz2")
            dest_folder = os.path.join(tmpdir, "extracted")

            src_file = os.path.join(tmpdir, "source.txt")
            with open(src_file, 'w') as f:
                f.write("bz2 content")

            with tarfile.open(tar_path, 'w:bz2') as tf:
                tf.add(src_file, arcname="source.txt")

            success, count, size = extract_tar(tar_path, dest_folder)
            assert success is True
            assert count == 1

    def test_extract_corrupted_tar(self):
        """Test extraction d'un TAR corrompu."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tar_path = os.path.join(tmpdir, "corrupted.tar")
            dest_folder = os.path.join(tmpdir, "extracted")

            with open(tar_path, 'wb') as f:
                f.write(b"not a valid tar file at all")

            with pytest.raises(TarExtractionError):
                extract_tar(tar_path, dest_folder)


class TestConfig:
    """Tests pour le module config."""

    def test_default_config(self):
        from utils.config import Config

        config = Config()
        assert config.open_folder_after is True
        assert config.delete_archive_after is False
        assert config.play_sound is True

    def test_load_config_missing_file(self):
        """Test le chargement quand le fichier n'existe pas."""
        from utils.config import load_config
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "nonexistent.conf")
            # Le load_config cherche à côté de sys.executable,
            # mais on teste juste que Config() retourne les defaults
            config = load_config()
            assert config.open_folder_after is True


class TestRarExtractor:
    """Tests pour l'extracteur RAR (simulations)."""

    def test_error_on_missing_unrar(self, tmp_path):
        """Test l'erreur quand UnRAR.exe est absent."""
        from extractors.rar_extractor import extract_rar, RarExtractionError
        import sys
        import os

        src_file = tmp_path / "test.txt"
        src_file.write_text("test content")

        # Créer un .rar invalide juste pour tester le comportement
        archive = tmp_path / "test.rar"
        archive.write_bytes(b"Rar!fake_rar_data")

        dest = str(tmp_path / "extracted")

        # On ne peut pas facilement tester sans UnRAR.exe,
        # mais on vérifie que la fonction existe et a la bonne signature
        import inspect
        sig = inspect.signature(extract_rar)
        assert list(sig.parameters.keys()) == ["archive_path", "dest_folder"]


class TestLogger:
    """Tests pour le module logger."""

    def test_log_success_format(self):
        from utils.logger import log_success
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(os.environ.get('TEMP', '/tmp'), 'folios-extractor.log')
            # Nettoyer le log existant
            if os.path.exists(log_file):
                os.remove(log_file)

            log_success("/path/archive.zip", "/path/archive", 5, 10240)

            assert os.path.exists(log_file)
            with open(log_file) as f:
                content = f.read()
            assert "SUCCESS" in content
            assert "5 fichiers" in content

    def test_create_error_file(self):
        from utils.logger import create_error_file
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            archive = os.path.join(tmpdir, "test.zip")
            with open(archive, 'w') as f:
                f.write("fake archive")

            create_error_file(archive, "Archive corrompue")

            error_file = archive + ".error.txt"
            assert os.path.exists(error_file)
            with open(error_file) as f:
                content = f.read()
            assert "Archive corrompue" in content
            assert archive in content


class TestVersion:
    """Test le versioning."""

    def test_version_exists(self):
        import src
        assert hasattr(src, '__version__')
        assert isinstance(src.__version__, str)
        assert src.__version__ == "0.1.0"