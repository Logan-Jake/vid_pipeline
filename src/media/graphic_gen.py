from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap
import requests
from io import BytesIO
import unicodedata
import sys


def clean_text(text):
    return ''.join(c for c in text if unicodedata.category(c)[0] != 'C')
def generate_post_bubble(title, author, score, profile_pic_url=None, awards=[], filename="reddit_bubble.png"):
    title = clean_text(title)
    author = clean_text(author)
    WIDTH, HEIGHT = 1080, 400
    BG_COLOUR = (255, 255, 255, 230)
    TEXT_COLOUR = (0, 0, 0)
    ACCENT = (0, 121, 211)

    output_path = Path("output") / filename
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fonts
    def safe_font(font_name, size):
        try:
            return ImageFont.truetype(font_name, size)
        except Exception as e:
            print(f"⚠️ Font fallback: {font_name} failed ({e}), using default.")
            return ImageFont.load_default()

    font_user = safe_font("arial.ttf", 36)
    font_title = safe_font("arial.ttf", 48)
    font_meta = safe_font("arial.ttf", 28)

    # Rounded rectangle background
    radius = 40
    draw.rounded_rectangle([0, 0, WIDTH, HEIGHT], radius=radius, fill=BG_COLOUR)

    def round_image(img, radius):
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, img.size[0], img.size[1]], radius=radius, fill=255)
        rounded = Image.new("RGBA", img.size)
        rounded.paste(img, (0, 0), mask=mask)
        return rounded

    # Profile Picture
    pfp_x, pfp_y = 40, 30
    if profile_pic_url:
        try:
            headers = {"User-Agent": "vid_pipeline (by u/your_username)"}
            response = requests.get(profile_pic_url, headers=headers, timeout=5)
            response.raise_for_status()

            print("🔽 Downloading profile picture:", profile_pic_url)
            print("📦 Content-Length:", len(response.content))
            print("📄 Content-Type:", response.headers.get("Content-Type"))

            content_type = response.headers.get("Content-Type", "")
            if "image" in content_type:
                #pfp = Image.open(BytesIO(response.content)).resize((64, 64)).convert("RGBA")
                try:
                    image_data = BytesIO(response.content)
                    test_img = Image.open(image_data)
                    test_img.verify()  # Validate
                    image_data.seek(0)  # Rewind for actual use

                    pfp = Image.open(image_data).convert("RGBA").resize((64, 64))

                    rounded_pfp = round_image(pfp, radius=60)
                    img.paste(rounded_pfp, (pfp_x, pfp_y), mask=rounded_pfp)

                except Exception as e:
                    print("🚫 Failed to load profile pic (safe mode):", e)

                # rounded_pfp = round_image(pfp, radius=60)
                # img.paste(rounded_pfp, (pfp_x, pfp_y), mask=rounded_pfp)
            else:
                print("⚠️ Profile URL didn't return an image:", content_type)

        except Exception as e:
            print("🚫 Failed to load profile pic:", e)
    # Username + Blue Tick
    name_x = pfp_x + 80
    try:
        draw.text((name_x, pfp_y + 10), f"u/{author}", fill=ACCENT, font=font_user)
        print("✅ Username drawn")
    except Exception as e:
        print("🚫 Failed to draw username:", e)
        sys.stdout.flush()

    # Blue tick
    tick_path = Path(__file__).parent.parent / "assets" / "blue_tick.png"
    if tick_path.exists():
        tick_icon = Image.open(tick_path).resize((24, 24)).convert("RGBA")
        tick_x = name_x + len(author) * 18 + 16
        img.paste(tick_icon, (tick_x, pfp_y + 12), mask=tick_icon)
    else:
        print("⚠️ Blue tick icon missing:", tick_path)

    # Title text (wrapped)
    wrapped = textwrap.fill(title, width=40)
    draw.text((40, 120), wrapped, fill=TEXT_COLOUR, font=font_title)

    # Awards
    x = 40
    y = HEIGHT - 100
    for award in awards[:5]:
        try:
            icon_url = award.get("icon_url")
            if not icon_url:
                continue
            r = requests.get(icon_url)
            r.raise_for_status()
            icon = Image.open(BytesIO(r.content)).resize((48, 48)).convert("RGBA")
            img.paste(icon, (x, y), mask=icon)
            x += 56
        except Exception as e:
            print(f"⚠️ Failed to load award icon: {e}")

    # Likes / Comments / Shares
    meta_text = "❤️ 999+    💬 999+    🔁 999+"
    draw.text((40, HEIGHT - 50), meta_text, fill=TEXT_COLOUR, font=font_meta)

    # Audio bar (optional)
    draw.text((WIDTH - 180, 40), "🔊 ▂▃▄▅▆▇", fill=ACCENT, font=font_meta)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return output_path.as_posix()