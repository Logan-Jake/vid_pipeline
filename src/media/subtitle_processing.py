from faster_whisper import WhisperModel
import pysubs2
from matplotlib import font_manager as fm
from pathlib import Path

# Get absolute path to the project root (assumes script is in src/media)
project_root = Path(__file__).resolve().parents[1]
font_path = project_root / "assets" / "fonts" / "ConcertOne-Regular.ttf"  # "BarlowCondensed-Bold.ttf"
font_props = fm.FontProperties(fname=str(font_path))
font_name = font_props.get_name()



def make_ass(input_audio, output_ass,
             font=font_name, size=84,
             resolution=(1920, 1080),
             pos=(960, 540),
             delay=-0.1,
             max_words_per_line=1):

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
    # style.shadow = 1
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

            # Determine when to end this chunk
            if i + max_words_per_line < len(words):
                chunk_end_time = words[i + max_words_per_line].start + delay
            else:
                chunk_end_time = chunk[-1].end + delay

            # One subtitle event per word in the chunk
            for j, word in enumerate(chunk):
                word_start = word.start + delay

                line_parts = []
                for k, w in enumerate(chunk):
                    if j == k:
                        line_parts.append(r"{\c&H00BFFF&\bord3\3c&H000000&}" + w.word)
                    else:
                        line_parts.append(r"{\c&HFFFFFF&}" + w.word)

                styled_text = f"{{\\pos({pos[0]},{pos[1]})}}" + " ".join(line_parts)

                subs.append(pysubs2.SSAEvent(
                    start=int(word_start * 1000),
                    end=int(chunk_end_time * 1000),
                    style="Default",
                    text=styled_text
                ))

            # move to the next chunk
            i += max_words_per_line

    subs.save(output_ass)
    print("Subs saved to:", output_ass)