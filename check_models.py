import os
from google import genai

gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

# List all available models
models = client.models.list()

print("Available models:")
for model in models:
    if "tts" in model.name.lower() or "audio" in model.name.lower():
        print(f"- {model.name} (Supports: {model.supported_generation_methods})")