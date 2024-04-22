import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def generate_images(
    food_type, ticket_type, division, name_1, club, name_2=None, output_folder=None
):
    output_folder = (
        Path(output_folder)
        if output_folder
        else Path(__file__).parent / "generated_images"
    )
    output_folder.mkdir(parents=True, exist_ok=True)

    ticket_type_clean = ticket_type.replace(" ", "_")
    output_image_path = output_folder / f"{division}_{name_1}.png"

    image_template_path = find_image_template_path(food_type, ticket_type)
    if image_template_path:
        add_text_to_image(
            image_template_path, output_image_path, division, name_1, name_2, club
        )


def find_image_template_path(food_type, ticket_type):
    ticket_options = {
        "veggie": "source_image/badge_veggie",
        "non-veggie": "source_image/badge_non_veggie",
    }
    template_path = Path(ticket_options.get(food_type, "")) / f"{ticket_type}.png"
    if not template_path.exists():
        logging.error(
            f"Template not found for food type {food_type} and ticket type {ticket_type}"
        )
        return None
    return template_path


def add_text_to_image(template_path, output_path, division, name_1, name_2, club):
    with Image.open(template_path) as img:
        draw = ImageDraw.Draw(img)
        font_path = "/path/to/your/fonts/Arial.ttf"  # Update this path
        font_sizes = {"division": 85, "name": 110, "club": 75}
        fonts = {
            key: ImageFont.truetype(font_path, size) for key, size in font_sizes.items()
        }

        text_positions = {
            "division": (img.width / 2, 520, fonts["division"]),
            "name_1": (img.width / 2, 720, fonts["name"]),
            "name_2": (img.width / 2, 850, fonts["name"]) if name_2 else None,
            "club": (img.width / 2, 1050, fonts["club"]),
        }

        for key, (x, y, font) in text_positions.items():
            if text := getattr(locals(), key):
                draw.text((x, y), text, font=font, fill=(0, 0, 0), anchor="mm")

        img.save(output_path)
