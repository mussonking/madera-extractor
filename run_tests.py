"""Tests autonomes pour Folios Extractor - stdlib uniquement."""
import os, sys, tempfile, zipfile, tarfile, inspect

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

passed = 0
failed = 0
errors = []

def test(name, ok, msg=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"  OK {name}")
    else:
        failed += 1
        s = f" -- {msg}" if msg else ""
        print(f"  FAIL {name}{s}")
        errors.append(name)

def eq(a, b, label=""):
    test(label or "eq", a == b, f"{a!r} != {b!r}")

def is_true(v, label=""):
    test(label or "true", v is True)

def is_false(v, label=""):
    test(label or "false", v is False)

def raises(exc, fn, *a, **kw):
    try:
        fn(*a, **kw)
        return False
    except exc:
        return True

# NAMING
print("\n=== Naming ===")
from utils.naming import get_archive_base_name, get_destination_folder
eq(get_archive_base_name("archive.zip"), "archive", "simple zip")
eq(get_archive_base_name("projet.7z"), "projet", "simple 7z")
eq(get_archive_base_name("backup.tar.gz"), "backup", "tar.gz")
eq(get_archive_base_name("data.tgz"), "data", "tgz")
eq(get_archive_base_name("files.tar.bz2"), "files", "tar.bz2")

with tempfile.TemporaryDirectory() as d:
    eq(get_destination_folder(os.path.join(d, "test.zip")), os.path.join(d, "test"), "new dir")
with tempfile.TemporaryDirectory() as d:
    os.makedirs(os.path.join(d, "test"))
    eq(get_destination_folder(os.path.join(d, "test.zip")), os.path.join(d, "test_1"), "conflict 1")
with tempfile.TemporaryDirectory() as d:
    os.makedirs(os.path.join(d, "test"))
    os.makedirs(os.path.join(d, "test_1"))
    os.makedirs(os.path.join(d, "test_2"))
    eq(get_destination_folder(os.path.join(d, "test.zip")), os.path.join(d, "test_3"), "conflict 3")

# ZIP
print("\n=== Zip Extractor ===")
from extractors.zip_extractor import extract_zip, ZipExtractionError
with tempfile.TemporaryDirectory() as d:
    zp = os.path.join(d, "t.zip"); dest = os.path.join(d, "out")
    with zipfile.ZipFile(zp, 'w') as zf:
        zf.writestr("f1.txt", "H")
        zf.writestr("s/f2.txt", "N")
    s, c, _ = extract_zip(zp, dest)
    is_true(s, "extract ok"); eq(c, 2, "count")
    is_true(os.path.exists(os.path.join(dest, "f1.txt")), "f1")
    is_true(os.path.exists(os.path.join(dest, "s", "f2.txt")), "f2")
with tempfile.TemporaryDirectory() as d:
    zp = os.path.join(d, "e.zip"); dest = os.path.join(d, "out")
    with zipfile.ZipFile(zp, 'w'): pass
    s, c, _ = extract_zip(zp, dest)
    is_true(s, "empty ok"); eq(c, 0, "empty cnt")
with tempfile.TemporaryDirectory() as d:
    zp = os.path.join(d, "c.zip"); dest = os.path.join(d, "out")
    with open(zp, 'wb') as f: f.write(b"PK\x03\x04corrupt")
    test("corrupt raises", raises(ZipExtractionError, extract_zip, zp, dest))

# TAR
print("\n=== Tar Extractor ===")
from extractors.tar_extractor import extract_tar, TarExtractionError
with tempfile.TemporaryDirectory() as d:
    tp = os.path.join(d, "t.tar"); src = os.path.join(d, "s.txt"); dest = os.path.join(d, "out")
    with open(src, 'w') as f: f.write("hello")
    with tarfile.open(tp, 'w') as tf: tf.add(src, arcname="s.txt")
    s, c, _ = extract_tar(tp, dest)
    is_true(s, "tar ok"); eq(c, 1, "tar cnt")
with tempfile.TemporaryDirectory() as d:
    tp = os.path.join(d, "t.tar.gz"); src = os.path.join(d, "s.txt"); dest = os.path.join(d, "out")
    with open(src, 'w') as f: f.write("gz")
    with tarfile.open(tp, 'w:gz') as tf: tf.add(src, arcname="s.txt")
    s, c, _ = extract_tar(tp, dest)
    is_true(s, "targz ok")
with tempfile.TemporaryDirectory() as d:
    tp = os.path.join(d, "e.tar"); src = os.path.join(d, "s.txt"); dest = os.path.join(d, "out")
    with open(src, 'w') as f: f.write("safe")
    with tarfile.open(tp, 'w') as tf: tf.add(src, arcname="../outside/evil.txt")
    s, c, _ = extract_tar(tp, dest)
    is_true(s, "traversal blocked")
    is_false(os.path.exists(os.path.join(d, "outside")), "no outside")
with tempfile.TemporaryDirectory() as d:
    tp = os.path.join(d, "c.tar"); dest = os.path.join(d, "out")
    with open(tp, 'wb') as f: f.write(b"not tar")
    test("corrupt tar raises", raises(TarExtractionError, extract_tar, tp, dest))

# CONFIG
print("\n=== Config ===")
from utils.config import Config
cfg = Config()
is_true(cfg.open_folder_after, "def open")
is_false(cfg.delete_archive_after, "def del")
is_true(cfg.play_sound, "def sound")

# RAR
print("\n=== Rar ===")
from extractors.rar_extractor import extract_rar, RarExtractionError
sig = inspect.signature(extract_rar)
test("rar params", list(sig.parameters.keys()) == ["archive_path", "dest_folder"])

# LOGGER
print("\n=== Logger ===")
from utils.logger import log_success, create_error_file
lf = os.path.join(os.environ.get('TEMP', '/tmp'), 'folios-extractor.log')
if os.path.exists(lf): os.remove(lf)
log_success("/p/a.zip", "/p/a", 5, 10240)
is_true(os.path.exists(lf), "log exists")
c = open(lf).read()
is_true("SUCCESS" in c, "log success")
is_true("5 fichiers" in c, "log count")
with tempfile.TemporaryDirectory() as d:
    ar = os.path.join(d, "t.zip"); open(ar, 'w').close()
    create_error_file(ar, "test error")
    ef = ar + ".error.txt"
    is_true(os.path.exists(ef), "err file exists")
    is_true("test error" in open(ef).read(), "err msg")

# VERSION
print("\n=== Version ===")
import src as mod
is_true(hasattr(mod, '__version__'), "has __version__")
eq(mod.__version__, "0.1.0", "version value")

# GITIGNORE
print("\n=== Gitignore ===")
g = open('.gitignore').read()
test("has __pycache__", "__pycache__" in g)
test("has .pytest_cache", ".pytest_cache" in g)
test("has *.pyc", "*.pyc" in g)
test("has *.egg-info", "*.egg-info" in g)
test("has .DS_Store", ".DS_Store" in g)

# SUMMARY
print(f"\n{'='*50}")
print(f"Result: {passed} passed, {failed} failed")
if errors:
    print(f"FAILURES: {', '.join(errors)}")
    sys.exit(1)
else:
    print("ALL TESTS PASSED")
    sys.exit(0)
