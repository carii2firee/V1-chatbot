import requests
from googletrans import Translator
from voice_input import get_input
import os
from dotenv import load_dotenv

# Load Hugging Face API credentials from environment
load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_API_URL = os.getenv("HF_API_URL")

user_language_preferences = {}
translator = Translator()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/gpt2"  

translator = Translator()


def generate_ai_response(prompt):
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": prompt}
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        else:
            return data[0].get("generated_text", "").strip() if data else "Sorry, no response."
    except requests.exceptions.RequestException as e:
        print(f"❌ HuggingFace API error: {e}")
        return "Sorry, I couldn't generate a response right now."

# ========== Translation Mode ==========
def language_translation_mode(user_name, memory_logger):
    print("Would you like to enable language translation for:")
    user_translate = get_input("1. Your inputs? (yes/no): ").strip().lower() in ("yes", "y")
    ai_translate = get_input("2. AI responses? (yes/no): ").strip().lower() in ("yes", "y")

    if not user_translate and not ai_translate:
        print("No translation enabled. Exiting.")
        return

    print("\nExample language codes:")
    print("en - English, es - Spanish, fr - French, de - German, it - Italian, "
          "pt - Portuguese, ru - Russian, ja - Japanese, ko - Korean, zh-cn - Chinese (Simplified)")

    target_lang = get_input("Enter the target language code (e.g., 'en', 'es', 'fr'): ").strip().lower()

    print("\n🌍 Translation mode active. Say 'exit' to quit.")

    while True:
        user_input = get_input(f"\n{user_name}: ").strip()
        if user_input.lower() == "exit":
            print("Exiting translation mode.")
            break

        original_input = user_input

        # Translate user input if enabled
        if user_translate:
            try:
                user_input = translator.translate(user_input, dest=target_lang).text
                print(f"(Translated Input): {user_input}")
            except Exception as e:
                print(f"❌ Error translating input: {e}")

        # Generate AI response
        ai_response = generate_ai_response(user_input)

        # Translate AI response if enabled
        final_response = ai_response
        if ai_translate:
            try:
                final_response = translator.translate(ai_response, dest=target_lang).text
                print(f"AI: {final_response}")
            except Exception as e:
                print(f"❌ Error translating AI response: {e}")
        else:
            print(f"AI: {ai_response}")

        
        if memory_logger:
            memory_logger.log_interaction(original_input, final_response)