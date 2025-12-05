import os
import google.generativeai as genai
from config.settings import GOOGLE_API_KEY

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in settings.")
    exit()

genai.configure(api_key=GOOGLE_API_KEY)

print("Listing available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")