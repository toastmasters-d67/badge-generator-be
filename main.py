from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from dependencies import save_upload_file, clean_directory, ensure_directory_exists
from config import settings
from pathlib import Path
import csv
import logging

from badge_generator_be.add_text_to_pic import ImageGenerator
from badge_generator_be.merge_pic_to_file import generate_pdf

logging.basicConfig(
    filename="app.log",
    format="%(asctime)s: %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_directory_exists(Path(settings.upload_dir))
    ensure_directory_exists(Path(settings.output_dir))
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
    try:
        with csv_file.open("r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            for row in reader:
                if not row:
                    logger.warning(f"Empty row in {csv_file}")
                    continue
                food_type, ticket_type, division, name_1, name_2, club = [
                    value.strip() for value in row
                ]
                generator = ImageGenerator(output_path=settings.output_dir)
                generator.generate_images(
                    food_type,
                    ticket_type,
                    division,
                    name_1,
                    club,
                    name_2,
                )
        logger.info("Badges generated successfully")
    except Exception as e:
        logger.error(f"Failed to process CSV file {csv_file}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process CSV file")


@app.get("/combine_images_to_pdf")
async def combine_images_to_pdf():
    image_files = list(Path(settings.output_dir).rglob("*.png"))
    if not image_files:
        raise HTTPException(
            status_code=404, detail="No images found to combine into PDF"
        )
    output_pdf = Path(settings.output_dir) / "badges.pdf"
    try:
        generate_pdf([str(f) for f in image_files], str(output_pdf))
        logger.info("PDF generated successfully")
        return FileResponse(
            output_pdf, media_type="application/pdf", filename="badges.pdf"
        )
    except Exception as e:
        logger.error(f"Failed to generate PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")


@app.get("/download_zip")
async def download_zip():
    import zipfile

    zip_file_path = Path(settings.output_dir) / "generated_images.zip"
    try:
        with zipfile.ZipFile(zip_file_path, "w") as zipf:
            for file_path in Path(settings.output_dir).rglob("*"):
                zipf.write(
                    file_path, file_path.relative_to(Path(settings.output_dir).parent)
                )
        logger.info("ZIP file created successfully")
        return FileResponse(
            zip_file_path, media_type="application/zip", filename="generated_images.zip"
        )
    except Exception as e:
        logger.error(f"Failed to create ZIP file: {e}")
        raise HTTPException(status_code=500, detail="Failed to create ZIP file")
