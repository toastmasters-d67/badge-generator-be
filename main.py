import csv
import os
import shutil
import time
import zipfile
from typing import Union

from badge_generator_be.add_text_to_pic import generate_images
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


UPLOAD_DIR = "./upload_files"
OUTPUT_DIR = "./generated_images"


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    temp_file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with open(temp_file_path, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            if not row:  # Skip empty rows
                continue
            try:
                division, name, club, ticket_type, name_en, club_en, remark = row
                generate_images(division, name, club, ticket_type, name_en, club_en, remark, OUTPUT_DIR)
            except ValueError as e:
                print(f"Error processing row {row}: {e}")
                continue
        # For checking the upload file content, save the file temporarily
        # os.remove(temp_file_path)

    return {"detail": "Badges generated successfully"}


@app.get("/download/")
async def download_image():

    timestamp = int(time.time())
    formatted_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(timestamp))
    zip_file_name = f"generated_images_{formatted_time}.zip"

    zip_file_path = f"./{zip_file_name}"
    with zipfile.ZipFile(zip_file_path, "w") as zipf:
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, OUTPUT_DIR))

    return FileResponse(zip_file_path, media_type="application/zip", filename=zip_file_name)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
