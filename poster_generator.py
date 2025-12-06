from PIL import Image, ImageDraw, ImageFilter
import random
import math


def hex_to_rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def build_palette(pl):
    colors = []
    for c in pl:
        if isinstance(c, str):
            colors.append(hex_to_rgb(c))
        elif isinstance(c, (list, tuple)) and len(c) == 3:
            if all(v <= 1.0 for v in c):
                colors.append(tuple(int(v * 255) for v in c))
            else:
                colors.append(tuple(int(v) for v in c))
    if not colors:
        colors = [(169, 200, 216), (228, 238, 245), (111, 163, 200)]
    return colors


def vertical_gradient(size, colors):
    """多段纵向渐变背景。"""
    w, h = size
    img = Image.new("RGB", size, colors[0])
    draw = ImageDraw.Draw(img)
    n = len(colors) - 1
    for y in range(h):
        t = y / max(1, h - 1)
        idx = min(int(t * n), n - 1)
        c1, c2 = colors[idx], colors[idx + 1]
        lt = t * n - idx
        r = int(c1[0] + (c2[0] - c1[0]) * lt)
        g = int(c1[1] + (c2[1] - c1[1]) * lt)
        b = int(c1[2] + (c2[2] - c1[2]) * lt)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def add_soft_noise(img, amount=0.08):
    """给整张图加一点颗粒质感。"""
    w, h = img.size
    px = img.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            n = random.uniform(-amount * 255, amount * 255)
            r = max(0, min(255, int(r + n)))
            g = max(0, min(255, int(g + n)))
            b = max(0, min(255, int(b + n)))
            px[x, y] = (r, g, b)
    return img


def style_misty_gradient(base, intensity):
    """雾气山峦感：大模糊 + 轻颗粒。"""
    img = base.filter(ImageFilter.GaussianBlur(radius=20 * (0.5 + intensity)))
    return add_soft_noise(img, amount=0.06)


def style_ocean_motion(base, intensity):
    """海面流动：水平光带 + 模糊。"""
    w, h = base.size
    img = base.copy().convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")

    for _ in range(45):
        y = random.randint(0, h)
        length = random.randint(int(w * 0.4), int(w * 0.9))
        thickness = random.randint(8, 26)
        alpha = int(60 + 140 * intensity)
        d.line([(0, y), (length, y)], fill=(255, 255, 255, alpha), width=thickness)

    img = img.filter(ImageFilter.GaussianBlur(radius=10))
    img = add_soft_noise(img.convert("RGB"), amount=0.08)
    return img


def style_flowing_paint(base, intensity):
    """油彩/水纹：竖向流线 + 轻模糊。"""
    w, h = base.size
    img = base.copy().convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")

    for _ in range(60):
        x = random.randint(0, w)
        width = random.randint(40, 120)
        phase = random.random() * math.pi * 2
        for y in range(h):
            off = int(math.sin(phase + y * 0.01 * (1 + intensity * 2)) * width * 0.35)
            alpha = int(30 + 120 * (1 - y / h))
            d.line(
                [(x + off, y), (x + off + width, y)],
                fill=(255, 255, 255, alpha),
                width=1,
            )

    img = img.filter(ImageFilter.GaussianBlur(radius=6))
    img = add_soft_noise(img.convert("RGB"), amount=0.06)
    return img


def style_clean_minimal(base, intensity):
    """干净留白风：轻模糊 + 极少颗粒。"""
    img = base.filter(ImageFilter.GaussianBlur(radius=6 * (1 - intensity)))
    return add_soft_noise(img, amount=0.03)


def draw_typography(img, title, subtitle, focus="balanced"):
    """在图上加标题/副标题 + 半透明文字底。"""
    w, h = img.size
    img = img.convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)

    # 布局
    if focus == "text_on_bottom":
        title_y = int(h * 0.66)
        sub_y = int(h * 0.76)
    else:
        title_y = int(h * 0.18)
        sub_y = int(h * 0.28)

    margin_x = int(w * 0.08)
    box_h = int((sub_y - title_y) * 1.8)
    box_top = int(title_y - box_h * 0.3)

    # 半透明条
    od.rectangle(
        [margin_x - 30, box_top, w - margin_x + 30, box_top + box_h],
        fill=(0, 0, 0, 70),
    )
    img = Image.alpha_composite(img, overlay)
    d = ImageDraw.Draw(img)

    # 简单用默认字体（为了兼容环境）
    d.text((margin_x, title_y), title, fill=(255, 255, 255))
    d.text((margin_x, sub_y), subtitle, fill=(235, 235, 235))
    return img.convert("RGB")


def generate_poster(analysis: dict, seed: int = 42, size=(1080, 1920)):
    random.seed(seed)

    palette = build_palette(analysis.get("palette", []))
    intensity = float(analysis.get("intensity", 0.5))
    style_mode = analysis.get("style_mode", "misty_gradient")
    title = analysis.get("title", "城市的记忆")
    subtitle = analysis.get("subtitle", "关于你和这座城市的一个瞬间。")
    typ_focus = analysis.get("typography_focus", "balanced")

    base = vertical_gradient(size, palette)

    if style_mode == "ocean_motion":
        img = style_ocean_motion(base, intensity)
    elif style_mode == "flowing_paint":
        img = style_flowing_paint(base, intensity)
    elif style_mode == "clean_minimal":
        img = style_clean_minimal(base, intensity)
    else:
        img = style_misty_gradient(base, intensity)

    img = draw_typography(img, title, subtitle, typ_focus)
    return img
