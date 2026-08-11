#!/usr/bin/env python3
"""
YUGRAAL Gemstone Video Generator Engine
Direct REST API Implementation (Zero SDK Bugs)
"""

import os
import sys
import json
import random
import asyncio
import textwrap
import urllib.request
import urllib.parse
from PIL import Image, ImageDraw
import edge_tts
from moviepy import ImageClip, AudioFileClip

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY environment variable missing.", file=sys.stderr)
    sys.exit(1)

GEMSTONES = [
    "Yellow Sapphire (Pukhraj)", 
    "Blue Sapphire (Neelam)", 
    "Ruby (Manik)", 
    "Emerald (Panna)", 
    "Turquoise (Firoza)",
    "Red Coral (Moonga)",
    "Pearl (Moti)"
]

SCRIPT_PROMPT_TEMPLATE = """
Tu ek master Hindi storyteller aur gemstone expert hai. Niche diye gaye gemstone par ek dramatic short voiceover script likh.

Gemstone: {gemstone}

Requirements:
1. Hindi me kahani ya uski shakti/history explain karo (Anime/Manga dramatic commentary style me).
2. Pure Hindi text likho jo bolne me shaandar aur energetic lage (60-80 words max).
3. Output strictly valid JSON format me do:
{{
  "gemstone": "{gemstone}",
  "title": "Dramatic Title in Hindi",
  "hindi_script": "Pura Hindi voiceover text."
}}
"""

def generate_gemstone_script(gemstone_name: str) -> dict:
    print(f"📖 Generating Hindi story for {gemstone_name} via Direct REST API...")
    
    prompt_text = SCRIPT_PROMPT_TEMPLATE.format(gemstone=gemstone_name)
    
    # Try models directly via HTTP REST API
    models = ["gemini-2.0-flash", "gemini-1.5-flash"]
    last_err = None

    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt_text}]
                }
            ]
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        
        try:
            print(f"🔄 Requesting via model: {model_name}...")
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                raw_text = res_data['candidates'][0]['content']['parts'][0]['text']
                cleaned = raw_text.replace("```json", "").replace("```", "").strip()
                print(f"✨ Success with model: {model_name}")
                return json.loads(cleaned)
        except Exception as e:
            print(f"⚠️ Model {model_name} failed: {e}")
            last_err = e

    raise RuntimeError(f"All API model attempts failed. Error: {last_err}")

async def text_to_speech_hindi(text: str, output_audio_path: str):
    print("🎙️ Generating AI Hindi Voiceover (Edge-TTS hi-IN-MadhurNeural)...")
    voice = "hi-IN-MadhurNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_audio_path)

def create_card_image(title: str, gemstone: str, output_img_path: str):
    img = Image.new('RGB', (720, 1280), color=(10, 12, 24))
    draw = ImageDraw.Draw(img)
    
    # Outer Glow Frame
    draw.rectangle([20, 20, 700, 1260], outline=(0, 240, 255), width=4)
    
    # Headers
    draw.text((60, 150), "YUGRAAL GEMSTONE SERIES", fill=(0, 240, 255))
    draw.text((60, 240), f"GEM: {gemstone.upper()}", fill=(255, 215, 0))
    
    # Dynamic Title Wrapping
    margin = 60
    offset = 400
    for line in textwrap.wrap(title, width=16):
        draw.text((margin, offset), line, fill=(255, 255, 255))
        offset += 70
        
    img.save(output_img_path)

def build_video(image_path: str, audio_path: str, output_video_path: str):
    print("🎬 Rendering MP4 Video via MoviePy...")
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    
    clip = ImageClip(image_path).with_duration(duration)
    video = clip.with_audio(audio)
    
    video.write_videofile(
        output_video_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )
    print(f"✅ Rendered Video Saved at: {output_video_path}")

async def main():
    selected_stone = random.choice(GEMSTONES)
    script_data = generate_gemstone_script(selected_stone)
    
    os.makedirs("output", exist_ok=True)
    audio_file = "output/voiceover.mp3"
    image_file = "output/poster.png"
    video_file = "output/gemstone_story.mp4"
    
    await text_to_speech_hindi(script_data["hindi_script"], audio_file)
    create_card_image(script_data["title"], script_data["gemstone"], image_file)
    build_video(image_file, audio_file, video_file)

if __name__ == "__main__":
    asyncio.run(main())
