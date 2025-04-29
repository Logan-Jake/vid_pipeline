import pysubs2
import whisper

# 1) load & transcribe
model = whisper.load_model("small")
res = model.transcribe("voice.mp3", word_timestamps=True)

# 2) prepare the ASS file
subs = pysubs2.SSAFile()
# video resolution
subs.script_info["PlayResX"] = 1920
subs.script_info["PlayResY"] = 1080
# centred (an5 = centre-centre)
style = pysubs2.SSAStyle(
    fontname="Arial", fontsize=48,
    alignment=5, margin_v=50
)
subs.styles["Default"] = style

# 3) for each segment, emit one “karaoke” line
MAX_WIN = 4
for segment in res["segments"]:
    words = segment["words"]
    # sliding window of up to MAX_WIN words
    for i in range(len(words)):
        win = words[max(0, i - (MAX_WIN-1)) : i+1]
        # total window duration in centiseconds
        total_cs = int((win[-1]["end"] - win[0]["start"]) * 100)
        # generate \k tags: each word ≈ equal share of the window
        num = len(win)
        each_cs = total_cs // num
        karaoke = "".join(f"{{\\k{each_cs}}}{w['word']}" for w in win)
        # event runs from first word start to last word end
        start_ms = int(win[0]["start"] * 1000)
        end_ms   = int(win[-1]["end"]   * 1000)
        subs.append(pysubs2.SSAEvent(
            start=start_ms, end=end_ms,
            style="Default",
            text=f"{{\\pos(960,540)}}{karaoke}"
        ))

# 4) save
subs.save("highlight.ass")
