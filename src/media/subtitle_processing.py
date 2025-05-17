from faster_whisper import WhisperModel
import pysubs2
from matplotlib import font_manager as fm
from pathlib import Path


# Get absolute path to the project root (assumes script is in src/media)
project_root = Path(__file__).resolve().parents[1]
print(project_root)
font_path = project_root / "assets" / "fonts" / "ConcertOne-Regular.ttf"
print(font_path)

font_props = fm.FontProperties(fname=str(font_path))
font_name = font_props.get_name()



def make_ass(input_audio, output_ass,
             font="Concert One", size=64,
             resolution=(1920, 1080),
             pos=(960, 540),
             delay=0.0,
             max_words_per_line=4):

    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(input_audio, word_timestamps=True)

    subs = pysubs2.SSAFile()
    info = getattr(subs, "script_info", subs.info)
    info["PlayResX"], info["PlayResY"] = resolution

    style = pysubs2.SSAStyle(
        fontname=font,
        fontsize=size,
        alignment=5,
        borderstyle=1,
        outline=2
    )
    style.primary_colour = pysubs2.Color(255, 255, 0)  # Yellow
    style.outline_colour = pysubs2.Color(0, 0, 0)  # Black
    style.margin_v = 50
    subs.styles["Default"] = style

    for segment in segments:
        words = segment.words
        if not words:
            continue

        # Step over the transcript in chunks of 3-4 words
        i = 0
        while i < len(words):
            chunk = words[i:i + max_words_per_line]
            if len(chunk) < 1:
                break

            for j, word in enumerate(chunk):
                start = word.start + delay
                end = word.end + delay

                # Highlight the j-th word in the chunk
                line_parts = []
                for k, w in enumerate(chunk):
                    if j == k:
                        line_parts.append(r"{\c&H00FFFF&\bord2\3c&H000000&}" + w.word)
                    else:
                        line_parts.append(r"{\c&HFFFFFF&}" + w.word)

                styled_text = f"{{\\pos({pos[0]},{pos[1]})}}" + " ".join(line_parts)

                subs.append(pysubs2.SSAEvent(
                    start=int(start * 1000),
                    end=int(end * 1000),
                    style="Default",
                    text=styled_text
                ))

            # move to the next chunk
            i += max_words_per_line

    subs.save(output_ass)
    print("Subs saved to:", output_ass)
