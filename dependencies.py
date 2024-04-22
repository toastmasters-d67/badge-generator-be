from fastapi import HTTPException, UploadFile
import shutil
from pathlib import Path


def save_upload_file(upload_file: UploadFile, destination: Path):
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"File could not be saved: {e}")


def clean_directory(directory: Path):
    for item in directory.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
