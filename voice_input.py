import speech_recognition as sr

def listen_for_command():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("🎙️ Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source)
        print("🎧 Listening for your command...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print(f"🗣️ You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("❌ Sorry, I didn't catch that. Please try again.")
    except sr.RequestError:
        print("❌ Speech recognition service unavailable. Check your internet connection.")
    return None


def get_input(prompt_text=""):
    """
    Voice input with text fallback.
    Tries voice input first; if it fails, falls back to keyboard input.
    """
    user_input = listen_for_command()
    if user_input is None:
        user_input = input(prompt_text).strip().lower()
    else:
        user_input = user_input.strip().lower()
    return user_input