"""The shared palette (swatches never move; unused ones get replaced, so existing UVs stay valid): 128x128 px, 8x8 grid of 16 px flat swatches (64 colours), nearest filtering.

Rows (top to bottom in the image):
  0 fur      1 cave stone + water   2 wood + rope   3 cloth + leather
  4 iron/rust junk          5 treasure (gold + gems)
  6 guild teal + moss/mushrooms             7 torchlight + dragon

Every model colours its faces by collapsing their UVs onto a swatch centre: set_swatch(obj, "stone_mid").

Run:  python3 tools/palette.py      -> textures/palette.png, palette_labeled.png, palette.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CELL, GRID = 16, 8

ROWS = [
    ("Fur", [("fur_mask", "231c1a"), ("fur_charcoal", "3d3836"), ("fur_dark", "5a5452"), ("fur_mid", "807a76"),
             ("fur_light", "aaa5a0"), ("fur_brown", "7a5c48"), ("fur_tan", "b08f6e"), ("fur_cream", "e8dcc6")]),
    ("Stone + water", [("stone_deep", "1d2433"), ("water_deep", "245a85"), ("stone_dark", "3d4859"), ("stone_mid", "52607a"),
                    ("stone_light", "6c7b93"), ("stone_pale", "8e9bb0"), ("stone_frost", "b8c3d3"), ("water", "4c9cc8")]),
    ("Wood + rope", [("wood_bark", "3b2a20"), ("wood_dark", "5a3d2a"), ("wood_mid", "7d5637"), ("wood_light", "a3754a"),
                     ("wood_cut", "d2a36c"), ("wood_weathered", "8a7f72"), ("rope_dark", "8f7650"), ("rope", "c4a874")]),
    ("Cloth + leather", [("burlap", "a48b62"), ("cloth_cream", "e4d7b8"), ("cloth_red", "a8392f"), ("cloth_blue", "3f5f8c"),
                         ("cloth_mustard", "c89a35"), ("leather", "7a4a2c"), ("leather_dark", "4a2c1c"), ("soot", "2a2626")]),
    ("Iron + junk", [("iron_dark", "33363c"), ("iron", "555b64"), ("iron_light", "8a919b"), ("rust_dark", "6e3420"),
                     ("rust", "a6532c"), ("copper", "c27a46"), ("verdigris", "5fa594"), ("pewter", "a9a59a")]),
    ("Treasure", [("gold_dark", "a36a1c"), ("gold", "e0a32e"), ("gold_light", "f6cb52"), ("gold_glint", "fff1b0"),
                  ("silver", "c9d0d8"), ("ruby", "c4203a"), ("sapphire", "2d5fd0"), ("emerald", "1fa66a")]),
    ("Guild + nature", [("teal_dark", "0f4a4c"), ("teal", "1a7a78"), ("teal_light", "3fb3a8"), ("amethyst", "8a4fc4"),
                        ("moss_dark", "35502c"), ("moss", "5a8a3a"), ("moss_light", "92b955"), ("mushroom_glow", "7fe0d8")]),
    ("Torch + dragon", [("ember", "8c2a14"), ("torch_orange", "f07a1e"), ("flame_yellow", "ffc73a"), ("flame_white", "fff4d6"),
                        ("dragon_dark", "5c1418"), ("dragon_red", "a8242a"), ("dragon_light", "e0503a"), ("bone", "e2d6b4")]),
]

SWATCH = {}
for r, (_, sw) in enumerate(ROWS):
    for c, (name, hx) in enumerate(sw):
        SWATCH[name] = (r, c, hx)


def uv_of(name):
    """UV centre of a swatch (Blender UVs: v up, image row 0 is the TOP)."""
    r, c, _ = SWATCH[name]
    return ((c + 0.5) / GRID, 1 - (r + 0.5) / GRID)


def set_swatch(ob, name, faces=None):
    """Collapse the UVs of `faces` (indices, default all) of mesh object `ob` onto swatch `name`."""
    me = ob.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers.active.data
    u, v = uv_of(name)
    for p in (me.polygons if faces is None else (me.polygons[i] for i in faces)):
        for li in p.loop_indices:
            uv[li].uv = (u, v)


def rgb(hx):
    return tuple(int(hx[i:i + 2], 16) for i in (0, 2, 4))


def build():
    from PIL import Image, ImageDraw, ImageFont
    tex = ROOT / "textures"
    tex.mkdir(exist_ok=True)
    im = Image.new("RGB", (CELL * GRID, CELL * GRID))
    d = ImageDraw.Draw(im)
    for name, (r, c, hx) in SWATCH.items():
        d.rectangle([c * CELL, r * CELL, c * CELL + CELL - 1, r * CELL + CELL - 1], fill=rgb(hx))
    im.save(tex / "palette.png")
    # labeled sheet
    S, pad, lw = 120, 14, 170
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    ft = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    W, H = lw + GRID * (S + pad) + pad, 90 + GRID * (S + 34 + pad)
    sheet = Image.new("RGB", (W, H), (24, 26, 32))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 22), "PALETTE  128 x 128 px, 8 x 8 swatches of 16 px, nearest filtering", font=ft, fill=(240, 240, 245))
    d.text((pad, 58), "Row / column = position in palette.png.  Name = what set_swatch() calls it.", font=f, fill=(160, 165, 180))
    for r, (title, sw) in enumerate(ROWS):
        y = 90 + r * (S + 34 + pad)
        d.text((pad, y + S // 2 - 18), f"Row {r}", font=f, fill=(150, 155, 170))
        d.text((pad, y + S // 2), title, font=fb, fill=(240, 240, 245))
        for c, (name, hx) in enumerate(sw):
            x = lw + c * (S + pad)
            d.rectangle([x, y, x + S, y + S], fill=rgb(hx))
            d.text((x, y + S + 4), name, font=f, fill=(225, 228, 235))
            d.text((x, y + S + 19), f"#{hx}  ({r},{c})", font=f, fill=(140, 145, 160))
    sheet.save(ROOT / "textures" / "palette_labeled.png")
    data = {name: {"row": r, "col": c, "hex": "#" + hx, "uv": [round(x, 4) for x in uv_of(name)]}
            for name, (r, c, hx) in SWATCH.items()}
    (tex / "palette.json").write_text(json.dumps(data, indent=1))
    print(f"{len(SWATCH)} swatches")


if __name__ == "__main__":
    build()
