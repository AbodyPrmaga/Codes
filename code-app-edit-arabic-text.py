import os

from PIL import Image, ImageDraw, ImageFont


image = Image.open(os.path.join(os.path.dirname(__file__), "nature.jpg"))

font = ImageFont.truetype(
    os.path.join(
        os.path.dirname(__file__), "Vazirmatn-Regular.ttf"
    ),
    100,
)
text = "سلام عليكم"
canvas = ImageDraw.Draw(image)
canvas.text((0, 0), text, (255, 255, 255), font=font, direction="rtl",stroke_width=2,stroke_fill=(0,0,0))
image.save(os.path.join(os.path.dirname(__file__), "result.jpg"))
