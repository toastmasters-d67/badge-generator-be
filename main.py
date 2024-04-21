import csv
import os
import pathlib
import shutil
import zipfile
from os.path import isdir, isfile, join

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from badge_generator_be.add_text_to_pic import generate_images
from badge_generator_be.merge_pic_to_file import generate_pdf

app = FastAPI()

UPLOAD_DIR = "./upload_files"
OUTPUT_DIR = "./generated_images"


def main():
    pathlib.Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    pathlib.Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)


@app.post("/upload_csv")
async def upload_csv_file(file: UploadFile = File(...)):
    csv_file = pathlib.Path(UPLOAD_DIR) / file.filename

    with csv_file.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    for root, dirs, files in os.walk(OUTPUT_DIR, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))

    with open(csv_file, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            if not row:
                continue
            try:
                food_type, ticket_type, division, name_1, name_2, club = [
                    value.strip() for value in row
                ]
                generate_images(
                    food_type,
                    ticket_type,
                    division,
                    name_1,
                    club,
                    name_2,
                    output_folder=OUTPUT_DIR,
                )
            except ValueError as e:
                print(f"Error processing row {row}: {e}")
                continue

    return "Badges generated successfully"


@app.get("/combine_images_to_pdf")
async def combine_images_to_pdf():
    try:
        files_and_folders = [
            f for f in os.listdir(OUTPUT_DIR) if os.path.join(OUTPUT_DIR, f)
        ]
        folders = [f for f in files_and_folders if isdir(join(OUTPUT_DIR, f))]

        image_files = []

        for folder in folders:
            folder_path = join(OUTPUT_DIR, folder)
            files_in_folder = [
                f for f in os.listdir(folder_path) if isfile(join(folder_path, f))
            ]
            image_files.extend(
                [
                    join(folder_path, f)
                    for f in files_in_folder
                    if f.lower().endswith((".png"))
                ]
            )
        if not image_files:
            return

        output_pdf = os.path.join(OUTPUT_DIR, "badges.pdf")
        generate_pdf(image_files, output_pdf)

        return FileResponse(
            output_pdf, media_type="application/pdf", filename="badges.pdf"
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/download_zip")
async def download_zip():
    zip_file_name = "generated_images.zip"

    with zipfile.ZipFile(zip_file_name, "w") as zipf:
        for root, _, files in os.walk(OUTPUT_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, OUTPUT_DIR))

    return FileResponse(
        zip_file_name, media_type="application/zip", filename=zip_file_name
    )


if __name__ == "__main__":
    main()
