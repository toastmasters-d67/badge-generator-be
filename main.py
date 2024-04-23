from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from dependencies import save_upload_file, clean_directory
from config import settings
from pathlib import Path
import csv

from badge_generator_be.add_text_to_pic import generate_images
from badge_generator_be.merge_pic_to_file import generate_pdf


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
    yield
    clean_directory(Path(settings.upload_dir))


app = FastAPI(lifespan=lifespan)


@app.post("/upload_csv")
async def upload_csv_file(file: UploadFile = File(...)):
    csv_file = Path(settings.upload_dir) / file.filename
    save_upload_file(file, csv_file)
    return await process_csv_file(csv_file)


async def process_csv_file(csv_file: Path):
    clean_directory(Path(settings.output_dir))
    with open(csv_file, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            if not row:
                continue
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
                output_folder=Path(settings.output_dir),
            )
    return "Badges generated successfully"


@app.get("/combine_images_to_pdf")
async def combine_images_to_pdf():
    image_files = list(Path(settings.output_dir).rglob("*.png"))
    if not image_files:
        raise HTTPException(
            status_code=404, detail="No images found to combine into PDF"
        )
    output_pdf = Path(settings.output_dir) / "badges.pdf"
    generate_pdf([str(f) for f in image_files], str(output_pdf))
    return FileResponse(output_pdf, media_type="application/pdf", filename="badges.pdf")


@app.get("/download_zip")
async def download_zip():
    import zipfile

    zip_file_path = Path(settings.output_dir) / "generated_images.zip"
    with zipfile.ZipFile(zip_file_path, "w") as zipf:
        for file_path in Path(settings.output_dir).rglob("*"):
            zipf.write(
                file_path, file_path.relative_to(Path(settings.output_dir).parent)
            )
    return FileResponse(
        zip_file_path, media_type="application/zip", filename="generated_images.zip"
    )
