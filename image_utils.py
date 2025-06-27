from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests
import os

# Đảm bảo bạn đã tải font Roboto-Bold.ttf vào thư mục project
FONT_PATH = "Roboto-Bold.ttf"


def create_collage_with_numbers(image_urls, max_per_row=3, target_height=400):
    images = []
    for url in image_urls:
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content)).convert("RGB")
            aspect = img.width / img.height
            new_width = int(target_height * aspect)
            img = img.resize((new_width, target_height))
            images.append(img)
        except:
            continue

    if not images:
        return None

    rows = [
        images[i:i + max_per_row] for i in range(0, len(images), max_per_row)
    ]
    collage_width = max(sum(img.width for img in row) for row in rows)
    collage_height = sum(max(img.height for img in row) for row in rows)
    collage = Image.new("RGB", (collage_width, collage_height),
                        color=(30, 30, 30))

    draw = ImageDraw.Draw(collage)
    font_size = 24
    try:
        font = ImageFont.truetype(FONT_PATH, font_size)
    except:
        font = ImageFont.load_default()

    y_offset = 0
    counter = 1
    for row in rows:
        x_offset = 0
        max_height = max(img.height for img in row)
        for img in row:
            collage.paste(img, (x_offset, y_offset))
            label = str(counter)
            text_position = (x_offset + 8,
                             y_offset + img.height - font_size - 6)
            draw.text(text_position,
                      label,
                      font=font,
                      fill="white",
                      stroke_width=2,
                      stroke_fill="black")
            counter += 1
            x_offset += img.width
        y_offset += max_height

    result = BytesIO()
    collage.save(result, format="JPEG")
    result.seek(0)
    return result
