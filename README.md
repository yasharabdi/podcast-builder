# Podcast Builder

Turn a simple dialogue script into a finished multi-voice podcast episode with one command.

Podcast Builder reads a JSON script, generates each line with a different [ElevenLabs](https://elevenlabs.io) voice, joins the clips with short pauses, and exports a single MP3 file. I built it to automate an English-learning podcast with four recurring characters, so I no longer have to cut and arrange audio clips by hand.

## Sample

[Listen to a sample](examples/sample.mp3) (about 15 seconds, three characters), generated from [`examples/sample_script.json`](examples/sample_script.json).

## Features

- One voice per character, defined in a single place
- Adjustable speech speed (useful for language learners)
- Automatic pauses between lines
- Checks character names before generating anything, so a typo doesn't waste credits
- Stops with a clear message if a line fails, instead of producing an incomplete episode
- Cleans up temporary files, even after errors
- Exports one MP3 at 128 kbps

## How it works

1. Reads the script from a JSON file.
2. Validates that every character has a voice.
3. Generates one audio clip per line with the ElevenLabs text-to-speech API.
4. Joins the clips in order with a pause between them and exports one MP3.

## Requirements

- Python 3 (developed and tested on 3.14)
- [FFmpeg](https://ffmpeg.org/download.html) installed and available in your PATH (needed by `pydub`)
- An ElevenLabs account and API key (every generated line uses your account's credits)

Check that FFmpeg works:

```
ffmpeg -version
```

## Setup

**1. Clone the repository and install dependencies**

```
git clone https://github.com/yasharabdi/podcast-builder.git
cd podcast-builder
pip install -r requirements.txt
```

**2. Add your API key**

Copy `.env.example` to `.env`:

```
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Then open `.env` and set your key:

```
ELEVENLABS_API_KEY=your_api_key_here
```

The `.env` file is listed in `.gitignore`. Never commit your key.

**3. Set your voices**

Open `podcast_generator.py` and replace the voice IDs in `VOICE_IDS` with your own ElevenLabs voice IDs. Character names must be lowercase and must match the names used in your script.

## Script format

A script is a JSON array. Each item is one line of dialogue, with the character's name and the text. The order of the items is the order of the episode.

```json
[
  {"char": "michael", "text": "Welcome back to English in Real Life!"},
  {"char": "thomas", "text": "Thanks for having me, Michael."}
]
```

- Use double quotes only.
- Do not put a comma after the last item.
- Every `char` must exist in `VOICE_IDS`.

## Usage

Build an episode from `script.json`. The result is saved as `episode_01.mp3`:

```
python podcast_generator.py
```

Or choose the input and output files yourself:

```
python podcast_generator.py examples/sample_script.json examples/sample.mp3
```

The first argument is the script, and the second is the output file. The output folder must already exist.

Tip: test with a short script first. Each line is one API request and uses credits.

## Configuration

These settings are at the top of `podcast_generator.py`:

| Setting | Default | Meaning |
| --- | --- | --- |
| `MODEL_ID` | `eleven_multilingual_v2` | ElevenLabs model used for generation |
| `SPEED` | `0.85` | `1.0` is normal speed, lower is slower |
| `VOICE_IDS` | (example IDs) | Character name to ElevenLabs voice ID |

The pause between lines (`pause_duration_ms`, 600 ms by default) is set in the last lines of the file. Per-character `stability` and `style` values are inside `generate_voice_clip`.

## Why Multilingual v2?

I wanted slower, clearer speech for learners. According to ElevenLabs' documentation, Eleven v4 has no Speed control, and I couldn't use speed with Eleven v3 either. Multilingual v2 supports the `speed` setting, so this project uses it.

## Troubleshooting

- **`Missing ELEVENLABS_API_KEY`**: the `.env` file is missing, or the variable name is wrong. Run the script from the project folder.
- **`Unknown character(s) in script`**: a name in your script doesn't match a key in `VOICE_IDS`.
- **FFmpeg errors from `pydub`**: FFmpeg is not installed or not in your PATH.
- **`Error generating for ...`**: read the message returned by ElevenLabs. It usually points to an invalid API key, a wrong voice ID, or not enough credits.
- **`JSONDecodeError`**: check your script for a trailing comma or single quotes.

## Project structure

```
podcast-builder/
├── examples/
│   ├── sample_script.json
│   └── sample.mp3
├── podcast_generator.py
├── script.json
├── requirements.txt
├── .env.example
└── .gitignore
```

## Notes

- Audio is generated with ElevenLabs. Check their terms and your plan's rules before publishing or using generated audio commercially.

## License

MIT License. See [LICENSE](LICENSE)

## Author

Built by [Yashar Abdi](https://github.com/yasharabdi).
