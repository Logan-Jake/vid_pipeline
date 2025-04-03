#NEEDS UPDATEING TO ELEVEN LABS
import pyttsx3
import os
from pathlib import Path

#NEEDS UPDATEING TO ELEVEN LABS
def generate_voiceover(text: str, filename: str = "voiceover.wav") -> str:
    engine = pyttsx3.init()
    engine.setProperty("rate", 230)
    engine.setProperty("volume", 1.0)

    output_path = Path("output") / filename
    output_path = output_path.resolve()  # Absolute path

    engine.save_to_file(text, str(output_path))
    engine.runAndWait()

    print("Saved to:", output_path)
    return str(output_path)