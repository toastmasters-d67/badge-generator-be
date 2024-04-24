import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 設定日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# 定義字體路徑
FONT_PATH = Path(__file__).parent.parent / "fonts" / "NotoSansTC-Regular.ttf"
# 定義模板基礎路徑
TEMPLATES_BASE_PATH = Path(__file__).parent / "source_image"

# 加載字體
FONTS_SIZES = {
    "division": 85,
    "name_1": 110,
    "name_2": 110,
    "club": 75,
}

# 確保輸出目錄存在
OUTPUT_PATH = Path(__file__).parent / "generated_images"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


def find_image_template_path(food_type, ticket_type):
    """構造並驗證模板圖片的路徑"""
    template_path = TEMPLATES_BASE_PATH / food_type / f"{ticket_type}.png"
    if not template_path.exists():
        logging.error(f"Template not found: {template_path}")
        return None
    return template_path


def generate_images(
    food_type, ticket_type, division, name_1, club, name_2=None, output_folder=None
):
    if output_folder is None:
        output_folder = OUTPUT_PATH  # 使用預設的輸出路徑
    else:
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)  # 確保輸出目錄存在

    output_image_path = output_folder / f"{division}_{name_1}.png"
    image_template_path = find_image_template_path(
        food_type, ticket_type.replace(" ", "_")
    )

    if image_template_path:
        add_text_to_image(
            image_template_path, output_image_path, division, name_1, name_2, club
        )
    else:
        logging.error(
            f"Template not found for food type {food_type} and ticket type {ticket_type}"
        )


def add_text_to_image(template_path, output_path, division, name_1, name_2, club):
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
            if text and key in FONTS_SIZES:
                font_size = FONTS_SIZES[key]
                if len(text) > 25:
                    font_size = int(112.5 - len(text) * 1.5)
                print(font_size)
                draw.text(
                    (x, y),
                    text,
                    font=ImageFont.truetype(str(FONT_PATH), font_size),
                    fill=(0, 0, 0),
                    anchor="mm",
                )

        img.save(output_path)
