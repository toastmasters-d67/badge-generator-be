import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class ImageGenerator:
    FONT_PATH = Path(__file__).parent.parent / "fonts" / "NotoSansTC-Regular.ttf"
    TEMPLATES_BASE_PATH = Path(__file__).parent / "source_image"
    FONTS_SIZES = {
        "division": 85,
        "name_1": 110,
        "name_2": 110,
        "club": 75,
    }

    def __init__(self, output_path=None):
        self.output_path = Path(
            output_path or Path(__file__).parent / "generated_images"
        )
        self.output_path.mkdir(parents=True, exist_ok=True)

    def find_image_template_path(self, food_type, ticket_type):
        """構造並驗證模板圖片的路徑"""
        template_path = self.TEMPLATES_BASE_PATH / food_type / f"{ticket_type}.png"
        if not template_path.exists():
            logger.error(f"Template not found: {template_path}")
            return None
        return template_path

    def generate_images(
        self, food_type, ticket_type, division, name_1, club, name_2=None
    ):
        output_image_path = self.output_path / f"{division}_{name_1}.png"
        image_template_path = self.find_image_template_path(
            food_type, ticket_type.replace(" ", "_")
        )

        if image_template_path:
            self.add_text_to_image(
                image_template_path, output_image_path, division, name_1, name_2, club
            )
        else:
            logger.error(
                f"Template not found for food type {food_type} and ticket type {ticket_type}"
            )

    def add_text_to_image(
        self, template_path, output_path, division, name_1, name_2, club
    ):
        try:
            with Image.open(template_path) as img:
                draw = ImageDraw.Draw(img)
                text_positions = {
                    "division": (img.width / 2, 520, division),
                    "name_1": (img.width / 2, 720, name_1),
                    "club": (img.width / 2, 1050, club),
                }

                if name_2:
                    text_positions["name_2"] = (img.width / 2, 850, name_2)

                for key, (x, y, text) in text_positions.items():
                    if text and key in self.FONTS_SIZES:
                        font_size = self.FONTS_SIZES[key]
                        if len(text) > 25:
                            font_size = max(10, int(112.5 - len(text) * 1.5))
                        draw.text(
                            (x, y),
                            text,
                            font=ImageFont.truetype(str(self.FONT_PATH), font_size),
                            fill=(0, 0, 0),
                            anchor="mm",
                        )

                img.save(output_path)
                logger.info(f"Image saved: {output_path}")
        except Exception as e:
            logger.error(f"Failed to add text to image: {e}")
