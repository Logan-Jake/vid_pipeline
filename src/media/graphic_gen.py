from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap
import requests
from io import BytesIO

def generate_post_bubble(title, author, score, profile_pic_url=None, awards=[], filename="reddit_bubble.png"):
    WIDTH, HEIGHT = 1080, 400
    BG_COLOUR = (255, 255, 255, 230)
    TEXT_COLOUR = (0, 0, 0)
    ACCENT = (0, 121, 211)

    output_path = Path("output") / filename
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fonts
    font_user = ImageFont.truetype("arial.ttf", 36)
    font_title = ImageFont.truetype("arial.ttf", 48)
    font_meta = ImageFont.truetype("arial.ttf", 28)

    # Rounded rectangle background
    radius = 40
    draw.rounded_rectangle([0, 0, WIDTH, HEIGHT], radius=radius, fill=BG_COLOUR)

    # Profile Picture
    pfp_x, pfp_y = 40, 30
    if profile_pic_url:
        try:
            headers = {"User-Agent": "vid_pipeline (by u/your_username)"}
            response = requests.get(profile_pic_url, headers=headers, timeout=5)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "image" in content_type:
                pfp = Image.open(BytesIO(response.content)).resize((64, 64)).convert("RGBA")

                def round_image(img, radius):
                    mask = Image.new("L", img.size, 0)
                    draw = ImageDraw.Draw(mask)
                    draw.rounded_rectangle([0, 0, img.size[0], img.size[1]], radius=radius, fill=255)
                    rounded = Image.new("RGBA", img.size)
                    rounded.paste(img, (0, 0), mask=mask)
                    return rounded

                rounded_pfp = round_image(pfp, radius=60)
                img.paste(rounded_pfp, (pfp_x, pfp_y), mask=rounded_pfp)
            else:
                print("⚠️ Profile URL didn't return an image:", content_type)

        except Exception as e:
            print("🚫 Failed to load profile pic:", e)

    # Username + Blue Tick
    name_x = pfp_x + 80
    draw.text((name_x, pfp_y + 10), f"u/{author}", fill=ACCENT, font=font_user)

    # Blue tick
    tick_path = Path(__file__).parent.parent / "assets" / "blue_tick.png"
    tick_icon = Image.open(tick_path).resize((24, 24)).convert("RGBA")
    tick_x = name_x + len(author) * 18 + 16
    img.paste(tick_icon, (tick_x, pfp_y + 12), mask=tick_icon)

    # Title text (wrapped)
    wrapped = textwrap.fill(title, width=40)
    draw.text((40, 120), wrapped, fill=TEXT_COLOUR, font=font_title)

    # Awards
    x = 40
    y = HEIGHT - 100
    for award in awards[:5]:  # Show up to 5 awards
        try:
            r = requests.get(award["icon_url"])
            icon = Image.open(BytesIO(r.content)).resize((48, 48)).convert("RGBA")
            img.paste(icon, (x, y), mask=icon)
            x += 56
        except Exception as e:
            print(f"Failed to load award {award['name']}: {e}")

    # Likes / Comments / Shares
    meta_text = "❤️ 999+    💬 999+    🔁 999+"
    draw.text((40, HEIGHT - 50), meta_text, fill=TEXT_COLOUR, font=font_meta)

    # Audio bar (optional)
    draw.text((WIDTH - 180, 40), "🔊 ▂▃▄▅▆▇", fill=ACCENT, font=font_meta)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return str(output_path)
