
from PIL import Image, ImageDraw, ImageFilter
import random, math


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def build_palette(pl):
    colors = []
    for c in pl:
        if isinstance(c, str):
            colors.append(hex_to_rgb(c))
    return colors or [(169, 200, 216), (228, 238, 245), (111, 163, 200)]


def vertical_gradient(size, colors):
    w, h = size
    img = Image.new("RGB", size, colors[0])
    d = ImageDraw.Draw(img)
    n = len(colors) - 1
    for y in range(h):
        t = y / (h - 1)
        idx = min(int(t * n), n - 1)
        c1, c2 = colors[idx], colors[idx + 1]
        lt = t * n - idx
        r = int(c1[0] + (c2[0] - c1[0]) * lt)
        g = int(c1[1] + (c2[1] - c1[1]) * lt)
        b = int(c1[2] + (c2[2] - c1[2]) * lt)
        d.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def add_noise(img, a=0.06):
    w, h = img.size
    px = img.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            n = random.uniform(-a * 255, a * 255)
            px[x, y] = (
                max(0, min(255, int(r + n))),
                max(0, min(255, int(g + n))),
                max(0, min(255, int(b + n))),
            )
    return img


def style_misty(base, intensity):
    img = base.filter(ImageFilter.GaussianBlur(radius=25 * (0.5 + intensity)))
    return add_noise(img, 0.05)


def style_ocean(base, intensity):
    w, h = base.size
    img = base.copy().convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(40):
        y = random.randint(0, h)
        length = random.randint(int(w * 0.4), int(w * 0.9))
        thickness = random.randint(8, 22)
        alpha = int(70 + 120 * intensity)
        d.line([(0, y), (length, y)], fill=(255, 255, 255, alpha), width=thickness)
    img = img.filter(ImageFilter.GaussianBlur(radius=10))
    return add_noise(img.convert("RGB"), 0.07)


def style_flowing(base, intensity):
    w, h = base.size
    img = base.copy().convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(60):
        x = random.randint(0, w)
        width = random.randint(40, 120)
        phase = random.random() * math.pi * 2
        for y in range(h):
            off = int(math.sin(phase + y * 0.01 * (1 + intensity * 2)) * width * 0.4)
            alpha = int(30 + 120 * (1 - y / h))
            d.line([(x + off, y), (x + off + width, y)], fill=(255, 255, 255, alpha), width=1)
    img = img.filter(ImageFilter.GaussianBlur(radius=6))
    return add_noise(img.convert("RGB"), 0.06)


def style_clean(base, intensity):
    img = base.filter(ImageFilter.GaussianBlur(radius=6 * (1 - intensity)))
    return add_noise(img, 0.03)


def draw_typography(img, title, subtitle, focus="balanced"):
    w, h = img.size
    img = img.convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)

    if focus == "text_on_bottom":
        ty = int(h * 0.66)
        sy = int(h * 0.76)
    else:
        ty = int(h * 0.18)
        sy = int(h * 0.28)

    mx = int(w * 0.08)
    box_h = int((sy - ty) * 1.8)
    box_top = int(ty - box_h * 0.3)

    od.rectangle([mx - 30, box_top, w - mx + 30, box_top + box_h], fill=(0, 0, 0, 70))
    img = Image.alpha_composite(img, overlay)
    d = ImageDraw.Draw(img)

    d.text((mx, ty), title, fill=(255, 255, 255))
    d.text((mx, sy), subtitle, fill=(240, 240, 240))

    return img.convert("RGB")


def generate_poster(analysis, seed=42, size=(1080, 1920)):
    random.seed(seed)

    pal = build_palette(analysis.get("palette", []))
    base = vertical_gradient(size, pal)

    style = analysis.get("style_mode", "misty_gradient")
    intensity = float(analysis.get("intensity", 0.5))

    if style == "ocean_motion":
        img = style_ocean(base, intensity)
    elif style == "flowing_paint":
        img = style_flowing(base, intensity)
    elif style == "clean_minimal":
        img = style_clean(base, intensity)
    else:
        img = style_misty(base, intensity)

    img = draw_typography(
        img,
        analysis.get("title", "城市的记忆"),
        analysis.get("subtitle", "关于城市的一段情绪片段"),
        analysis.get("typography_focus", "balanced"),
    )
    return img
