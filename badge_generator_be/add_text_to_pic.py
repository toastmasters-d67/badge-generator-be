import logging
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(
    filename='skipped_name.log',
    format='%(asctime)s: %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %z',
    level=logging.INFO,
)


def generate_images(food_type, ticket_type, division, name_1, club, name_2=None, output_folder=None):
    output_folder_path = Path(output_folder) if output_folder else Path(__file__).parent / "generated_images"
    # output_folder_path = Path(output_folder) if output_folder else Path(__file__).parent
    add_text_to_image(
        food_type,
        ticket_type,
        division,
        name_1,
        name_2,
        club,
        output_folder_path,
    )


def add_text_to_image(
        food_type,
        ticket_type,
        division,
        name_1,
        name_2,
        club,
        output_folder_path,
):
    output_folder_path = Path(output_folder_path) / ticket_type.replace(" ", "_")  # Create subfolder based on ticket type
    os.makedirs(output_folder_path, exist_ok=True)
    output_image_path = output_folder_path / f"{division+name_1}.png"

    ticket_option_mapping = {
        'veggie': {
            'only_dinner': 'badge_veggie/only_dinner.png',
            '1st_day_with_dinner': 'badge_veggie/1st_day_with_dinner.png',
            '2nd_day_with_dinner': 'badge_veggie/2nd_day_with_dinner.png',
            'two_days_with_dinner': 'badge_veggie/two_days_with_dinner.png',
            '1st_day_without_dinner': 'badge_veggie/1st_day_without_dinner.png',
            '2nd_day_without_dinner': 'badge_veggie/2nd_day_without_dinner.png',
            'two_days_without_dinner': 'badge_veggie/two_days_without_dinner.png',
        },
        'non-veggie': {
            'only_dinner': 'badge_non_veggie/only_dinner.png',
            '1st_day_with_dinner': 'badge_non_veggie/1st_day_with_dinner.png',
            '2nd_day_with_dinner': 'badge_non_veggie/2nd_day_with_dinner.png',
            'two_days_with_dinner': 'badge_non_veggie/two_days_with_dinner.png',
            '1st_day_without_dinner': 'badge_non_veggie/1st_day_without_dinner.jpg',
            '2nd_day_without_dinner': 'badge_non_veggie/2nd_day_without_dinner.png',
            'two_days_without_dinner': 'badge_non_veggie/two_days_without_dinner.png',
        },
    }
    food_type = food_type.strip()
    ticket_type = ticket_type.strip()

    if food_type not in ticket_option_mapping:
        logging.error(f"Invalid food type: {food_type}")
        return

    food_mapping = ticket_option_mapping[food_type]

    if ticket_type not in food_mapping:
        logging.error(f"Invalid ticket type for user {name_1}: {ticket_type}")
        return

    image_path = food_mapping[ticket_type]

    with Image.open(image_path) as image:
        image = image.convert("RGB")

        draw = ImageDraw.Draw(image)
        font_path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
        division_font = ImageFont.truetype(font_path, 85)
        name_font = ImageFont.truetype(font_path, 100)
        club_font = ImageFont.truetype(font_path, 60)

        text_positions = [
            (520, str(division), division_font),
            (700, str(name_1), name_font),
            (850, str(name_2) if name_2 else '', name_font),  # If name_2 is None, use empty string
            (1050, str(club), club_font),
        ]

        for y, text, font, in text_positions:
            x = (image.width - 1) / 2
            draw.text((x, y - 1 / 2), text, font=font, fill=(0, 0, 0), anchor="mm")

        image.save(output_image_path)
