from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path
from matplotlib import font_manager as fm

# Get absolute path to the project root (assumes script is in src/media)
project_root = Path(__file__).resolve().parents[1]
font_path = project_root / "assets" / "fonts" / "BarlowCondensed-Bold.ttf"
font_props = fm.FontProperties(fname=str(font_path))
font_name = font_props.get_name()

output_dir = project_root / "output" / "subtitle_frames"
os.makedirs(output_dir, exist_ok=True)

def render_subtitle_image(text, highlight_index=None, image_index=0,
                          resolution=(1920, 1080), font_size=92):
    font = ImageFont.truetype(font_path, size=font_size)
    img = Image.new("RGBA", (resolution[0], 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    words = text.split()
    x = (resolution[0] - sum(draw.textlength(w + " ", font=font) for w in words)) // 2
    y = 50

    for i, word in enumerate(words):
        if i == highlight_index:
            fill = "gold"
            stroke_width = 6
        else:
            fill = "white"
            stroke_width = 3

        draw.text((x, y), word, font=font, fill=fill,
                  stroke_width=stroke_width, stroke_fill="black")
        x += draw.textlength(word + " ", font=font)

    filename = f"{output_dir}/frame_{image_index:04d}.png"
    img.save(filename)
    return filename


# Example usage: render a line with 4 words and highlight one of them
example_text = "This is a test"
generated_files = [render_subtitle_image(example_text, highlight_index=i, image_index=i) for i in range(4)]
generated_files
print(generated_files)

from pathlib import Path

print("Output directory:", Path(output_dir).resolve())
