import tempfile
import zipfile


TEMP_DIR = tempfile.mkdtemp()


def import_experiment(zip_path):
    with zipfile.ZipFile(zip_path) as f:
        f.extractall(TEMP_DIR)
