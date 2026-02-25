---
name: avatar-animation
description: Skill to generate animated avatar GIFs from static images using the D-ID API. This skill drives the D-ID API to physically animate faces with nodding and lip syncing and convert the output to a GIF.
---

# Avatar Animation Skill

A toolkit for turning static avatar images (e.g., logo.jpeg) into animated nodding and talking GIFs using the D-ID API.

## Preconditions

This skill requires the `DID_API_KEY` environment variable to be set.
If this key is missing, the script will immediately exit.

**Setting the Key on macOS:**

```bash
export DID_API_KEY="your_api_key_here"
```

## Running the Script

The core script is located at `scripts/generate_avatar.py`.

```bash
python scripts/generate_avatar.py <path_to_input_jpeg> <path_to_output_gif>
```

If no arguments are provided, the script defaults to animating `open_memo/webapp/frontend/src/assets/logo.jpeg` and saving it as `logo.gif` in the same directory.

### Requirements

The script uses `ffmpeg` for converting the output `.mp4` into an optimized `.gif`. Ensure you have `ffmpeg` installed (e.g., `brew install ffmpeg`).
It also requires `requests` (e.g., `pip install requests`).
