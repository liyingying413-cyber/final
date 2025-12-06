
from PIL import Image, ImageDraw
import random

def generate_poster_image(result, style, seed):
    random.seed(seed)

    width, height = 1080, 1920
    img = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(img)

    palette = result["color_palette"]

    for c in palette:
        color = tuple(int(v * 255) for v in c)
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(200, 400)
        draw.ellipse((x-r, y-r, x+r, y+r), fill=color)

    if style == "Cyberpunk":
        for x in range(0, width, 40):
            draw.line((x, 0, x, height), fill=(255,0,200), width=3)
    elif style == "Film mood":
        draw.rectangle((0,0,width,height), outline=(80,60,40), width=80)
    elif style == "Shimmer":
        for _ in range(80):
            sx = random.randint(0,width)
            sy = random.randint(0,height)
            draw.ellipse((sx-8,sy-8,sx+8,sy+8), fill=(255,255,255))
    elif style == "Brutalist grid":
        for y in range(0,height,120):
            draw.line((0,y,width,y), fill=(170,170,170), width=4)
        for x in range(0,width,120):
            draw.line((x,0,x,height), fill=(170,170,170), width=4)

    return img
