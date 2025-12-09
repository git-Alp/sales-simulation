import os
import google.generativeai as genai

# --- CONFIGURATION ---
# Paste your API Key here directly
GOOGLE_API_KEY = ""

def list_available_models():

    print("Configuring Google AI...")
    
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        
        print("Fetching available models for this API Key...")
        print("-" * 40)
        
        # List all models
        models = list(genai.list_models())
        
        found_flash = False
        valid_models = []

        for m in models:
            # We only care about models that can generate content (chat)
            if 'generateContent' in m.supported_generation_methods:
                print(f"Model found: {m.name}")
                valid_models.append(m.name)
                if "flash" in m.name:
                    found_flash = True

        print("-" * 40)
        
        if found_flash:
            print("SUCCESS: Flash model is available! You can use it.")
        else:
            print("WARNING: 'gemini-1.5-flash' NOT found.")
            print(f"Please use one of these models in your code: {valid_models}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    list_available_models()