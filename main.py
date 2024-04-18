import csv
import os
import shutil
import time
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
output_pdf = os.path.join(OUTPUT_DIR, "badges.pdf")


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


def clear_output_directory():
    for root, dirs, files in os.walk(OUTPUT_DIR, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))


def combine_images_to_pdf():
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

    generate_pdf(image_files, output_pdf)


@app.get("/combine_images_to_pdf")
async def combine_images_to_pdf_endpoint():
    try:
        if not os.path.exists(OUTPUT_DIR):
            raise FileNotFoundError("Generated images folder not found")

        return FileResponse(
            output_pdf, media_type="application/pdf", filename="badges.pdf"
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/download_images_and_pdf/")
async def upload_csv_file(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    temp_file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    clear_output_directory()

    with open(temp_file_path, "r", encoding="utf-8") as csvfile:
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

    combine_images_to_pdf()

    timestamp = int(time.time())
    formatted_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(timestamp))
    zip_file_name = f"generated_images_{formatted_time}.zip"
    zip_file_path = f"./{zip_file_name}"
    with zipfile.ZipFile(zip_file_path, "w") as zipf:
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, OUTPUT_DIR))

    zip_download_link = f"/download_zip/{zip_file_name}"
    pdf_download_link = "/combine_images_to_pdf"

    return {
        "detail": "Badges generated successfully",
        "images.zip_download_link": zip_download_link,
        "pdf_download_link": pdf_download_link,
    }


@app.get("/download_zip/{zip_file_name}")
async def download_zip(zip_file_name: str):
    zip_file_path = f"./{zip_file_name}"
    return FileResponse(
        zip_file_path, media_type="application/zip", filename=zip_file_name
    )


if __name__ == "__main__":
    main()
