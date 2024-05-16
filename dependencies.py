from fastapi import HTTPException, UploadFile
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def save_upload_file(upload_file: UploadFile, destination: Path):
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        logger.info(f"File {upload_file.filename} saved to {destination}")
    except IOError as e:
        logger.error(f"Failed to save file {upload_file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"File could not be saved: {e}")


def clean_directory(directory: Path):
    try:
        for item in directory.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        logger.info(f"Directory {directory} cleaned")
    except Exception as e:
        logger.error(f"Failed to clean directory {directory}: {e}")


def ensure_directory_exists(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    return directory
