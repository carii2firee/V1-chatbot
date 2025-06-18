from googletrans import Translator
from voice_input import get_input
from gui_launcher import speak_with_elevenlabs  # Make sure this import path is correct
from dotenv import load_dotenv
import os
import pygame

load_dotenv()
translator = Translator()
voice_id = os.getenv("DEFAULT_VOICE_ID") or "VR6AewLTigWG4xSOukaG"

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
        translated_input = user_input
        if user_translate:
            try:
                translated_input = translator.translate(user_input, dest=target_lang).text
                print(f"(Translated Input): {translated_input}")
            except Exception as e:
                print(f"❌ Error translating input: {e}")
                translated_input = user_input  # fallback

        # Generate friendly, consistent AI companion message
        if ai_translate:
            try:
                final_response = f"This is your translated response: {translated_input}. Let me know if you want to translate anything else!"
                print(f"AI: {final_response}")

                # Optionally use ElevenLabs for speech
                audio_path = speak_with_elevenlabs(final_response, voice_id)
                if audio_path:
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
            except Exception as e:
                print(f"❌ Error speaking response: {e}")
                final_response = "Sorry, I couldn't process that response."
        else:
            final_response = translated_input
            print(f"AI: {final_response}")

        if memory_logger:
            memory_logger.log_interaction(original_input, final_response)
