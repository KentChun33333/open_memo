#!/usr/bin/env python3
import requests
import time
import os
import sys
import subprocess
import argparse

# --- PRECONDITION CHECK ---
API_KEY = os.environ.get("DID_API_KEY")

if not API_KEY:
    print("Error: DID_API_KEY environment variable is not set.", file=sys.stderr)
    print("Please set it by running: export DID_API_KEY='your_d-id_api_key_here'", file=sys.stderr)
    sys.exit(1)

HEADERS_JSON = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Basic {API_KEY}"
}
HEADERS = {
    "accept": "application/json",
    "authorization": f"Basic {API_KEY}"
}

def generate_avatar(input_path, output_gif_path):
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    output_mp4_path = output_gif_path.replace('.gif', '.mp4')
    
    print(f"Uploading image '{input_path}' to D-ID...")
    with open(input_path, "rb") as f:
        # D-ID expects image upload via /images
        files = {"image": (os.path.basename(input_path), f, "image/jpeg")}
        resp = requests.post("https://api.d-id.com/images", headers=HEADERS, files=files)
        
        if not resp.ok:
            print(f"Failed to upload: {resp.text}", file=sys.stderr)
            sys.exit(1)
            
        source_url = resp.json().get("url")
    
    print(f"Uploaded! Image URL: {source_url}")
    
    print("Starting animation...")
    payload = {
        "source_url": source_url,
        "script": {
            "type": "text",
            "input": "Hello! I am Open Memo's Nanobot. I am ready to assist you!",
            "provider": {"type": "microsoft", "voice_id": "en-US-JennyNeural"}
        },
        "config": {
            "fluent": True,
            "pad_audio": 0.0,
            "result_format": "mp4"
        }
    }
    
    resp = requests.post("https://api.d-id.com/talks", headers=HEADERS_JSON, json=payload)
    if not resp.ok:
        print(f"Failed to start animation: {resp.text}", file=sys.stderr)
        sys.exit(1)
        
    talk_id = resp.json().get("id")
    print(f"Animation started successfully. ID: {talk_id}")
    
    video_url = None
    while True:
        resp = requests.get(f"https://api.d-id.com/talks/{talk_id}", headers=HEADERS_JSON)
        result = resp.json()
        
        status = result.get("status")
        print(f"Status: {status}...")
        
        if status == "done":
            video_url = result.get("result_url")
            print(f"Finished! Video URL: {video_url}")
            break
        elif status == "error":
            print(f"Error generating video: {result}", file=sys.stderr)
            sys.exit(1)
            
        time.sleep(3)
        
    print("Downloading video...")
    video_resp = requests.get(video_url)
    with open(output_mp4_path, "wb") as f:
        f.write(video_resp.content)
        
    print("Converting to GIF using ffmpeg...")
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", output_mp4_path, 
            "-vf", "fps=15,scale=256:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse", 
            "-loop", "0", output_gif_path
        ], check=True)
    except FileNotFoundError:
        print("Error: 'ffmpeg' is not installed or not in PATH.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Success! Created animated GIF at {output_gif_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an animated avatar GIF using D-ID API.")
    parser.add_argument("input_image", nargs="?", default="/Users/kentchiu/Documents/Github/open_memo/webapp/frontend/src/assets/logo.jpeg", help="Path to input JPEG image")
    parser.add_argument("output_gif", nargs="?", default="/Users/kentchiu/Documents/Github/open_memo/webapp/frontend/src/assets/logo.gif", help="Path to output GIF image")
    
    args = parser.parse_args()
    generate_avatar(args.input_image, args.output_gif)
