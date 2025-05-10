import pysubs2, whisper


def make_ass(input_audio, output_ass,
             font="Arial", size=48,
             resolution=(1920,1080),
             pos=(960,540),
             delay=0.0,
             skip_duration=0.1): # if this is set to 0.0 then subs don't generate
    # 1) transcribe
    model = whisper.load_model("small")
    result = model.transcribe(input_audio, word_timestamps=True)

    # 2) prepare ASS
    subs = pysubs2.SSAFile()
    info = getattr(subs, "script_info", subs.info)
    info["PlayResX"], info["PlayResY"] = resolution

    # default style: white text
    style = pysubs2.SSAStyle(fontname=font, fontsize=size, alignment=5)
    style.primarycolour = pysubs2.Color(255,255,255,0)  # white
    style.margin_v     = 50
    subs.styles["Default"] = style

    # 3) one event *per word*
    for seg in result["segments"]:
        if seg["start"] < skip_duration:
                words = seg["words"]
                for w in words:
                    start_ms = int((w["start"] + delay) * 1000)
                    end_ms = int((w["end"] + delay) * 1000)

                    # rebuild the whole line, but ONLY w['word'] in red:
                    parts = []
                    for w2 in words:
                        if w2 is w:
                            parts.append(f"{{\\c&H0000FF&}}{w2['word']}")  # red in BGR hex
                        else:
                            parts.append(w2["word"])
                    text = f"{{\\pos({pos[0]},{pos[1]})}} " + " ".join(parts)

                    subs.append(pysubs2.SSAEvent(
                        start=start_ms,
                        end=end_ms,
                        style="Default",
                        text=text
                    ))

    # 4) save
    subs.save(output_ass)
    print("Subs saved to:", output_ass)
