import logging
import sys
from pathlib import Path
import unicodedata
import textwrap
from PIL import Image, ImageDraw, ImageFont

# set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def clean_text(text):
    return ''.join(c for c in text if unicodedata.category(c)[0] != "C")

def safe_font(font_name, size):
    try:
        return ImageFont.truetype(font_name, size)
    except Exception as e:
        logging.warning(f"Could not load '{font_name}' @ {size}px: {e}. Using default.")
        return ImageFont.load_default()

def generate_post_bubble(image_path, title, output_path=None):
    # Loads reddit_card PNG, draws the title to fill & centre the available area,
    # then saves as `titled_<original>.png` (or to output_path if given).

    image_path = Path(image_path)
    if not image_path.is_file():
        raise FileNotFoundError(f"Bubble image not found at: {image_path}")

    title = clean_text(title)

    # open & convert
    try:
        img = Image.open(image_path).convert("RGBA")
    except Exception as e:
        raise RuntimeError(f"Failed to open/convert image '{image_path}': {e}")

    draw = ImageDraw.Draw(img)
    W, H = img.size
    text_colour = (0, 0, 0, 255)

    # — Hard-coded styling options —
    CORNER_RADIUS = 40 # pixels for rounded corners
    CROP_TO_MASK = False  # whether to auto-crop to rounded mask
    CROP_LEFT = 110
    CROP_TOP = 40
    CROP_RIGHT = 110
    CROP_BOTTOM = 40
    M_L, M_T, M_R, M_B = 10, 180, 10, 130  # padding for text from png edges

    inner_w = W - M_L - M_R
    inner_h = H - M_T - M_B

    # — choose font size that fits —
    font = None
    wrapped = None
    for size in range(200, 10, -2):
        f = safe_font("arial.ttf", size)
        x0, y0, x1, y1 = draw.textbbox((0, 0), "A", font=f)
        avg_w = x1 - x0
        chars_per_line = max(1, inner_w // avg_w)
        lines = textwrap.wrap(title, width=chars_per_line)
        candidate = "\n".join(lines)
        bbox = draw.multiline_textbbox((0, 0), candidate, font=f)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if w <= inner_w and h <= inner_h:
            font, wrapped = f, candidate
            break

    # — fallback font if none found —
    if font is None:
        font = safe_font("arial.ttf", 16)
        x0, y0, x1, y1 = draw.textbbox((0, 0), "A", font=font)
        char_w = x1 - x0
        chars_per_line = max(1, inner_w // char_w)
        wrapped = textwrap.fill(title, width=chars_per_line)

    # measure text
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # centre within the inset area
    x = M_L + (inner_w - tw) // 2
    y = M_T + (inner_h - th) // 2

    # — draw text —
    try:
        draw.multiline_text((x, y), wrapped, fill=text_colour, font=font, align="center")
    except Exception as e:
        raise RuntimeError(f"Failed while drawing text: {e}")

    # apply manual crop
    w, h = img.size
    img = img.crop((CROP_LEFT, CROP_TOP, w - CROP_RIGHT, h - CROP_BOTTOM))

    # apply rounded-corner mask
    if CORNER_RADIUS > 0:
        mask = Image.new("L", img.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle([(0,0), img.size], radius=CORNER_RADIUS, fill=255)
        rounded = Image.new("RGBA", img.size)
        rounded.paste(img, (0,0), mask=mask)
        img = rounded
        if CROP_TO_MASK:
            bbox = mask.getbbox()
            img = img.crop(bbox)

    # — decide output filename —
    if output_path:
        out = Path(output_path)
    else:
        out = image_path.with_name(f"titled_{image_path.name}")

    # — save —
    try:
        img.save(out)
    except Exception as e:
        raise RuntimeError(f"Could not save image to '{out}': {e}")

    return str(out)


from reddit.fetcher import fetch_top_story

# if __name__ == "__main__":
#     story = fetch_top_story()
#
#     if not story:
#         print("No suitable story found.")
#         exit()
#
#     print("🎉 Story Fetched:")
#     print(f"Title: {story['title']}")
#     print(f"By: u/{story['author']} ({story['score']} upvotes)")
#     print("-----")
#     print(story['text'])
#     #print("🖼 Profile Pic URL:", story['profile_pic_url'])
#
#     bubble_template = Path(__file__).parent.parent / "assets" / "Reddit_card.png"  # ← set this to your local template
#
#     try:
#         graphic_path = generate_post_bubble(
#             image_path=bubble_template,
#             title=story["title"],
#             # output_path="out/my_titled_image.png"  # optionally override
#         )
#         logging.info(f"🖼  Graphic saved to: {graphic_path}")
#     except Exception as e:
#         logging.error("❌ Error generating graphic", exc_info=True)
#         sys.exit(1)
