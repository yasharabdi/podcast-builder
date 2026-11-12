import os
import sys
import json
import requests
from dotenv import load_dotenv
from pydub import AudioSegment

# --- Configuration ---
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise SystemExit("Missing ELEVENLABS_API_KEY. Add it to your .env file.")

BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech"
MODEL_ID = "eleven_multilingual_v2"
SPEED = 0.85

VOICE_IDS = {
    "michael": "l7x3FBD2xZRRYomG9yLN",  # Michael (fixed host)
    "thomas":  "MoJJpya8yKhIwmreOkBj",  # Thomas (rotating guest)
    "linda":   "HdlVQttQnf158KhDVgTX",  # Linda (rotating guest)
    "susan":   "2Q2BNaHvoHSxOfVBW83r",  # Susan (rotating guest)
}


def generate_voice_clip(text: str, character: str, output_path: str) -> bool:
    """Generate one audio clip with ElevenLabs. Returns True on success."""
    url = f"{BASE_URL}/{VOICE_IDS[character]}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    payload = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.40 if character == "michael" else 0.68,
            "similarity_boost": 0.75,
            "style": 0.20 if character == "michael" else 0.08,
            "use_speaker_boost": True,
            "speed": SPEED,
        },
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
    except requests.RequestException as error:
        print(f"Network error for {character}: {error}")
        return False

    if response.status_code != 200:
        print(f"Error generating for {character}: {response.text}")
        return False

    with open(output_path, "wb") as f:
        f.write(response.content)
    return True


def build_podcast(script_dialogues, output_final_file="final_podcast.mp3", pause_duration_ms=500):
    """Generate every line, join the clips with pauses, and export one mp3 file."""
    # Check all character names first, so no credits are wasted on a typo.
    unknown = {item["char"] for item in script_dialogues} - set(VOICE_IDS)
    if unknown:
        raise ValueError(f"Unknown character(s) in script: {', '.join(sorted(unknown))}")

    combined_audio = AudioSegment.empty()
    pause = AudioSegment.silent(duration=pause_duration_ms)
    temp_files = []

    try:
        for i, item in enumerate(script_dialogues, start=1):
            char = item["char"]
            text = item["text"]
            temp_filename = f"temp_{i}.mp3"
            temp_files.append(temp_filename)

            print(f"Processing line {i} by [{char}]...")
            if not generate_voice_clip(text, char, temp_filename):
                raise RuntimeError(f"Failed to generate line {i} by [{char}]. Stopping.")

            combined_audio += AudioSegment.from_mp3(temp_filename) + pause
    finally:
        # Remove temp files even if something failed.
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    combined_audio.export(output_final_file, format="mp3", bitrate="128k")
    print(f"\n[OK] Podcast saved as '{output_final_file}'")


if __name__ == "__main__":
    script_path = sys.argv[1] if len(sys.argv) > 1 else "script.json"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "episode_01.mp3"

    with open(script_path, encoding="utf-8") as f:
        script = json.load(f)

    build_podcast(script, output_path, pause_duration_ms=600)