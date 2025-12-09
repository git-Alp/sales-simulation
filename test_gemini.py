import os
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core.exceptions import NotFound, ResourceExhausted

# --- CONFIGURATION ---
# Ideally, we should use environment variables for safety.
# For now, pasting the key here is fine for testing.
GOOGLE_API_KEY = ""

def test_connection():

    print("Initializing Gemini Model...")

    # Initialize the LLM
    # We use 'gemini-flash-latest' which is fast and cost-effective.
    print("Initializing Gemini Model (gemini-flash-latest)...")

    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.7
    )

    try:
        print("Sending request to Google AI Studio...")
        
        prompt = "Explain the concept of 'Flash Sale' in one short sentence."
        response = llm.invoke(prompt)
        
        print("-" * 40)
        print("SUCCESS! API RESPONSE RECEIVED:")
        print(f"Answer: {response.content}")
        print("-" * 40)

    except ResourceExhausted:
         print("ERROR: Quota exceeded or model not allowed in Free Tier.")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    test_connection()