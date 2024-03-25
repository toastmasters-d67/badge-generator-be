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


def generate_images(division, name, club, ticket_type, name_en=None, club_en=None, remark=None, output_folder=None):
    """
    Generate badge images for users.

    :param division: Information about the division.
    :param name_en: English name of the user.
    :param name: Name of the user.
    :param club_en: English name of the club.
    :param club: Name of the club.
    :param remark: Any remark for the user.
    :param ticket_type: Type of the ticket chosen by the user.
    :param output_folder: Output folder for saving badge images.
    """
    output_folder_path = Path(output_folder) if output_folder else Path(__file__).parent / "generated_images"
    # output_folder_path = Path(output_folder) if output_folder else Path(__file__).parent
    add_text_to_image(
        division,
        name,
        club,
        ticket_type,
        output_folder_path,
        name_en=name_en,
        club_en=club_en,
        remark=remark,
    )


def add_text_to_image(
        division,
        name,
        club,
        ticket_type,
        output_folder_path,
        name_en=None,
        club_en=None,
        remark=None,
):
    """
    Add text to badge image.

    :param division: Information about the division.
    :param name_en: English name of the user.
    :param name: Name of the user.
    :param club_en: English name of the club.
    :param club: Name of the club.
    :param remark: Any remark for the user.
    :param ticket_type: Type of the ticket chosen by the user.
    :param output_folder_path: Path to the output folder.
    :param output_filename: Name of the output file.
    """
    output_folder_path = output_folder_path / ticket_type.replace(" ", "_")  # Create subfolder based on ticket type
    os.makedirs(output_folder_path, exist_ok=True)
    output_image_path = Path(output_folder_path) / f"{division+name}.jpg"

    ticket_option_mapping = {
        'two_day_without_dinner': 'ticket_type/二日.png',
        'two_day_with_dinner': 'ticket_type/二日票+晚宴.png',
        'only_dinner': 'ticket_type/晚宴.png',
        '1st_day_without_dinner': 'ticket_type/optionD.jpg',
        '1st_day_with_dinner': 'ticket_type/optionE.jpg',
        '2nd_day_without_dinner': 'ticket_type/optionF.jpg',
        '2nd_day_with_dinner': 'ticket_type/optionG.jpg',
    }

    ticket_type = ticket_type.strip()
    image_path = ticket_option_mapping.get(ticket_type)
    if not image_path:
        logging.error(f"Invalid ticket type for user {name}: {ticket_type}")
        return

    with Image.open(image_path) as image:
        image = image.convert("RGB")

        draw = ImageDraw.Draw(image)
        font_path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
        font = ImageFont.truetype(font_path, 30)

        text_positions = [

            (480, division),
            (510, name_en),
            (540, name),
            (570, club_en),
            (600, club),
            (630, remark),
        ]

        for y, text in text_positions:
            x = (image.width - 1) / 2
            draw.text((x, y - 1 / 2), text, font=font, fill=(0, 0, 0), anchor="mm")

        image.save(output_image_path)
