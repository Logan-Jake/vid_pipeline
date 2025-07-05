from faster_whisper import WhisperModel
import pysubs2
from matplotlib import font_manager as fm
from pathlib import Path

# Get absolute path to the project root (assumes script is in src/media)
project_root = Path(__file__).resolve().parents[1]
font_path = project_root / "assets" / "fonts" / "BarlowCondensed-Bold.ttf" # "ConcertOne-Regular.ttf"
font_props = fm.FontProperties(fname=str(font_path))
font_name = font_props.get_name()


def make_ass(input_audio, output_ass,
             font=font_name, size=84,
             resolution=(1920, 1080),
             pos=(960, 540),
             delay=-0.1,
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
    # style.shadow = 1
    style.primary_colour = pysubs2.Color(255, 255, 255)  # White (unhighlighted)
    style.secondary_colour = pysubs2.Color(255, 215, 0)  # Yellow (highlighted)
    style.outline_colour = pysubs2.Color(0, 0, 0)  # Black
    style.margin_v = 50
    subs.styles["Default"] = style

    # Collect all words from all segments into one list
    all_words = []
    for segment in segments:
        if segment.words:
            all_words.extend(segment.words)

    print(f"Total words collected: {len(all_words)}")

    if not all_words:
        print("No words found!")
        return

    # Now chunk across all words, respecting punctuation breaks
    i = 0
    while i < len(all_words):
        # Start building a chunk
        chunk = []
        chunk_start_index = i

        # Add words to chunk until we hit max_words_per_line or punctuation
        while i < len(all_words) and len(chunk) < max_words_per_line:
            word = all_words[i]
            chunk.append(word)
            i += 1

            # Check if this word ends with punctuation that should force a new chunk
            clean_word = word.word.strip()
            if clean_word.endswith(('.', ',', '!', '?', ';', ':')):
                print(f"Found punctuation in '{clean_word}' - forcing new chunk")
                break

        if not chunk:
            break

        print(
            f"Processing chunk {chunk_start_index // max_words_per_line + 1}: indices {chunk_start_index} to {chunk_start_index + len(chunk) - 1}")
        print(f"Chunk contents: {[w.word for w in chunk]}")

        # Calculate chunk timing
        chunk_start = chunk[0].start + delay
        chunk_end = chunk[-1].end + delay

        # Create separate overlapping events for each word to ensure only one is highlighted
        for j, word in enumerate(chunk):
            word_start = word.start + delay
            word_end = word.end + delay

            # Build the line with only this word highlighted
            line_parts = []
            for k, w in enumerate(chunk):
                clean_word = w.word.strip()
                if k > 0:
                    clean_word = " " + clean_word

                if k == j:
                    # This is the highlighted word
                    line_parts.append(f"{{\\c&H00D7FF&}}{clean_word}")  # Yellow
                else:
                    # This is an unhighlighted word
                    line_parts.append(f"{{\\c&HFFFFFF&}}{clean_word}")  # White

            # Create the complete line
            styled_text = f"{{\\pos({pos[0]},{pos[1]})}}" + "".join(line_parts)

            print(f"Word {j + 1}: '{word.word.strip()}' from {word_start:.2f}s to {word_end:.2f}s")

            # Create subtitle event for this word's highlight duration
            subs.append(pysubs2.SSAEvent(
                start=int(word_start * 1000),
                end=int(word_end * 1000),
                style="Default",
                text=styled_text
            ))

        print(f"Chunk completed with {len(chunk)} words")
        print("---")

        # Note: i is already incremented in the chunk-building loop above

    subs.save(output_ass)
    print("Subs saved to:", output_ass)