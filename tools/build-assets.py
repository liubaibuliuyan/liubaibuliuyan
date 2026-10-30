"""Regenerate the profile banner and avatar. Needs Noto Sans CJK + DejaVu on the system."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "assets"

NOTO = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

THEMES = {
    "light": dict(canvas="#F3F0E9", ink="#14110F", acc="#FF3D1F", dim="#6B615A", on_accent="#14110F"),
    "dark": dict(canvas="#0D1117", ink="#F0EDE6", acc="#FF5A3C", dim="#8B929C", on_accent="#0D1117"),
}

W, H, PAD = 1600, 460, 60


def f(path, px):
    return ImageFont.truetype(path, px, index=2 if path == NOTO else 0)


def cap_height(font):
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    return -d.textbbox((0, 0), "H", font=font, anchor="ls")[1]


def tracked(d, x, y, text, font, fill, sp=0.0):
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill, anchor="ls")
        x += d.textlength(ch, font=font) + sp
    return x


def right(d, x_edge, y, text, font, fill):
    d.text((x_edge - d.textlength(text, font=font), y), text, font=font, fill=fill, anchor="ls")


def line(d, y, x0, x1, w, fill):
    d.rectangle([x0, y, x1, y + w], fill=fill)


def banner(theme):
    t = THEMES[theme]
    img = Image.new("RGB", (W, H), t["canvas"])
    d = ImageDraw.Draw(img)

    band_top, rule_y, caption_base = 388, 348, 374
    cap_top, cap_bottom, gap = 92, 322, 22

    size = 150
    while cap_height(f(NOTO, size)) * 2 + gap > cap_bottom - cap_top and size > 40:
        size -= 2
    ch = cap_height(f(NOTO, size))
    base2 = cap_bottom
    base1 = base2 - ch - gap

    line(d, 0, 0, W, 5, t["ink"])

    lab, sm = f(MONOB, 20), f(MONO, 20)
    x = tracked(d, PAD, 48, "GITHUB PROFILE", lab, t["ink"], 5)
    d.text((x + 16, 48), "/", font=sm, fill=t["acc"], anchor="ls")
    tracked(d, x + 44, 48, "ENGINEERING LOG", lab, t["dim"], 5)
    right(d, W - PAD, 48, "2026", lab, t["acc"])

    big = f(NOTO, size)
    tracked(d, PAD - 6, base1, "LIUBAIBU", big, t["ink"], -7)
    tracked(d, PAD - 6, base2, "LIUYAN", big, t["acc"], -7)

    step = f(MONOB, 21)
    col_x = W - PAD - 250
    for i, (n, s) in enumerate([("01", "PROBLEM"), ("02", "CONSTRAINT"), ("03", "RESULT")]):
        y = base1 - ch + 38 + i * 75
        tracked(d, col_x, y, n, step, t["acc"], 2)
        right(d, W - PAD, y, s, step, t["ink"])
        line(d, y - 8, col_x + 52, W - PAD - d.textlength(s, font=step) - 16, 2, t["dim"])

    tracked(
        d,
        PAD,
        caption_base,
        "EVERY PROJECT ENDS WITH A NUMBER OR IT DOES NOT GET PUBLISHED",
        f(MONOB, 19),
        t["dim"],
        2,
    )

    line(d, rule_y, PAD, W - PAD, 2, t["ink"])
    d.rectangle([0, band_top, W, H], fill=t["acc"])
    band = f(MONOB, 21)
    x = tracked(d, PAD, band_top + 46, "01 NOW", band, t["on_accent"], 3)
    x = tracked(d, x + 34, band_top + 46, "02 WRITE-UPS", band, t["on_accent"], 3)
    tracked(d, x + 34, band_top + 46, "03 METHOD", band, t["on_accent"], 3)
    right(d, W - PAD, band_top + 46, "@liubaibuliuyan", band, t["on_accent"])

    img.save(OUT / f"banner-{theme}.png")
    return img.size, size


def avatar(theme, size=500):
    t = THEMES[theme]
    img = Image.new("RGB", (size, size), t["canvas"])
    d = ImageDraw.Draw(img)

    # GitHub crops the avatar to a circle: keep the monogram inside the middle band
    px = 300
    while d.textlength("LB", font=f(NOTO, px)) > 370 and px > 40:
        px -= 4
    big = f(NOTO, px)
    ch = cap_height(big)

    w_l = d.textlength("L", font=big)
    w_b = d.textlength("B", font=big)
    x0 = (size - (w_l + w_b - 6)) / 2
    base = size / 2 + ch / 2
    tracked(d, x0, base, "L", big, t["ink"], -6)
    tracked(d, x0 + w_l - 6, base, "B", big, t["acc"], -6)

    img.save(OUT / f"avatar-{theme}.png")
    return img.size, px


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        print(theme, banner(theme), avatar(theme))
