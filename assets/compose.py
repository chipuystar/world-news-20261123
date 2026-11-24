#!/usr/bin/env python3
"""Compose entry.png: a newspaper front page summing up 23 November 2026.

Crops the six generated vignette panels out of the two triptych strips in
this folder and lays them out with PIL so every letter is crisp.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

CREAM = (247, 242, 231)
INK = (26, 24, 20)
ACCENT = (146, 32, 24)

STRIPS = {
    "a": os.path.join(HERE, "media-generation-vignettes-a-0-42768b12-adf4-4f25-85ee-e812d1b27eb9.webp"),
    "b": os.path.join(HERE, "media-generation-vignettes-b-0-a61ca65f-fe05-4557-a8c7-6ab52b588fb2.webp"),
}


def panel_boxes(img):
    """Split a triptych strip into its three panel images.

    Finds the two cream gutters (columns that are light for almost the
    whole height), splits there, then trims each piece to its content.
    """
    g = img.convert("L")
    w, h = g.size
    px = g.load()
    light = []
    for x in range(w):
        n = sum(1 for y in range(0, h, 7) if px[x, y] > 232)
        light.append(n / (h // 7 + 1))
    # gutter candidate columns: >92% light
    runs, start = [], None
    for x, f in enumerate(light):
        if f > 0.92 and start is None:
            start = x
        elif f <= 0.92 and start is not None:
            runs.append((start, x - 1))
            start = None
    if start is not None:
        runs.append((start, w - 1))
    # ignore the outer edge runs; take the two widest inner runs
    inner = [r for r in runs if r[0] > w * 0.05 and r[1] < w * 0.95]
    inner.sort(key=lambda r: r[1] - r[0], reverse=True)
    cuts = sorted((a + b) // 2 for a, b in inner[:2])
    if len(cuts) != 2:
        cuts = [w // 3, 2 * w // 3]
    spans = [(0, cuts[0]), (cuts[0], cuts[1]), (cuts[1], w)]
    panels = []
    for x0, x1 in spans:
        piece = img.crop((x0, 0, x1, h))
        # trim to content bounding box (anything clearly not cream)
        mask = piece.convert("L").point(lambda v: 255 if v < 238 else 0)
        bbox = mask.getbbox()
        if bbox:
            piece = piece.crop(bbox)
        # step just inside any printed frame line
        pw, ph = piece.size
        ix, iy = int(pw * 0.012), int(ph * 0.012)
        piece = piece.crop((ix, iy, pw - ix, ph - iy))
        panels.append(piece)
    return panels


def square_crop(img, focus_y):
    """Center square crop of img, centred vertically at focus_y (0..1)."""
    w, h = img.size
    side = min(w, h)
    x0 = (w - side) // 2
    cy = int(h * focus_y)
    y0 = max(0, min(h - side, cy - side // 2))
    return img.crop((x0, y0, x0 + side, y0 + side))


def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


STORIES = [
    # (strip, panel index, focus_y, kicker, label, caption)
    ("a", 0, 0.42, "CLIMATE · ANTALYA",
     "NO DEAL AT COP31",
     "Talks end without agreement after the EU rejects a text silent on fossil fuels."),
    ("a", 1, 0.30, "POLITICS · WASHINGTON",
     "DEMOCRATS TAKE THE HOUSE",
     "258 seats — biggest House majority since 1992 — sealed by a North Carolina recount."),
    ("a", 2, 0.55, "WAR · MEDITERRANEAN",
     "DRONE SINKS RUSSIAN WARSHIP",
     "Kyiv says its drones sank a Russian corvette off the Libyan coast."),
    ("b", 0, 0.45, "MARKETS · WORLDWIDE",
     "MARKETS BOUNCE BACK",
     "Stocks rebound as Asia props up markets after Friday's AI sell-off."),
    ("b", 1, 0.50, "DISASTER · INDONESIA",
     "FACTORY FIRE KILLS 24",
     "A blaze at a Banten candy factory leaves about 30 people still unaccounted for."),
    ("b", 2, 0.32, "SPORT · TURIN",
     "ALCARAZ WINS ATP FINALS",
     "Beats Zverev in straight sets to lift his first ATP Finals trophy and end the year on top."),
]


def main():
    panels = {}
    for key, path in STRIPS.items():
        panels[key] = panel_boxes(Image.open(path).convert("RGB"))

    W = H = 1024
    page = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(page)

    # ---- masthead ----
    mast = ImageFont.truetype(SERIF_B, 86)
    title = "THE WORLD TODAY"
    tw = d.textlength(title, font=mast)
    d.text(((W - tw) / 2, 26), title, font=mast, fill=INK)
    d.line([(36, 138), (W - 36, 138)], fill=INK, width=5)
    d.line([(36, 148), (W - 36, 148)], fill=INK, width=2)
    date_f = ImageFont.truetype(SERIF_B, 45)
    date = "Monday 23 November 2026"
    dw = d.textlength(date, font=date_f)
    d.text(((W - dw) / 2, 162), date, font=date_f, fill=ACCENT)
    d.line([(36, 232), (W - 36, 232)], fill=INK, width=2)

    # ---- story grid: 2 columns x 3 rows ----
    margin, gap = 36, 24
    col_w = (W - 2 * margin - gap) // 2          # 464
    top, bottom = 252, 968
    row_h = (bottom - top - 2 * gap) // 3        # 222
    img_side = 196
    kick_f = ImageFont.truetype(SANS_B, 19)
    lab_f = ImageFont.truetype(SANS_B, 28)
    cap_f = ImageFont.truetype(SERIF, 20)

    for i, (strip, idx, focus, kicker, label, caption) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = margin + col * (col_w + gap)
        y = top + row * (row_h + gap)
        art = square_crop(panels[strip][idx], focus).resize((img_side, img_side))
        page.paste(art, (x, y + 8))
        d.rectangle([x, y + 8, x + img_side, y + 8 + img_side], outline=INK, width=2)
        tx = x + img_side + 16
        t_w = col_w - img_side - 16
        d.text((tx, y + 2), kicker, font=kick_f, fill=ACCENT)
        ly = y + 30
        for line in wrap(d, label, lab_f, t_w):
            d.text((tx, ly), line, font=lab_f, fill=INK)
            ly += 34
        cy = ly + 4
        for line in wrap(d, caption, cap_f, t_w):
            d.text((tx, cy), line, font=cap_f, fill=INK)
            cy += 25
        if row < 2:
            d.line([(x, y + row_h + gap // 2), (x + col_w, y + row_h + gap // 2)],
                   fill=(190, 180, 158), width=1)

    # ---- footer ----
    d.line([(36, 978), (W - 36, 978)], fill=INK, width=2)
    foot_f = ImageFont.truetype(SANS, 19)
    foot = "The whole day on one page · Compiled from the day's wire reports"
    fw = d.textlength(foot, font=foot_f)
    d.text(((W - fw) / 2, 988), foot, font=foot_f, fill=INK)

    out = os.path.join(ROOT, "entry.png")
    page.save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
