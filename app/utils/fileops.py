# app/utils/fileops.py
import tempfile, os, shutil
from typing import BinaryIO

TMP_ROOT = tempfile.gettempdir()

def save_upload_file(upload_file, dest_path: str):
    """
    upload_file is a Starlette UploadFile or a file-like object with .read()
    """
    with open(dest_path, "wb") as f:
        while True:
            chunk = upload_file.read(1024*64)
            if not chunk:
                break
            f.write(chunk)
    return dest_path

def create_temp_dir(prefix="tda_"):
    return tempfile.mkdtemp(prefix=prefix)

def cleanup_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
