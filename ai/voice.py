# ai/voice.py

import speech_recognition as sr
import pyttsx3
from pathlib import Path

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 180)
    engine.say(text)
    engine.runAndWait()

def text_to_speech(text: str, output_path: str = "output/audio.mp3") -> str:
    """
    Converts text to speech using pyttsx3 and saves as audio.
    NOTE: pyttsx3 doesn't support MP3, so it saves as WAV instead.
    """
    engine = pyttsx3.init()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    output_path = output_path.replace(".mp3", ".wav")  # pyttsx3 only supports WAV
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    return output_path

def listen(prompt=""):
    if prompt:
        speak(prompt)
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source, phrase_time_limit=10)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"⚠️ STT error: {e}")
        return ""

def handle_voice_command(text: str) -> str:
    """
    Process a text command (converted from voice) and return a reply string.
    """
    text = text.lower().strip()
    
    if "hello" in text:
        response = "Hi! How can I help you today?"
    elif "upload" in text:
        response = "You can upload a book using the upload button on the page."
    elif "search" in text:
        response = "Sure, what would you like to search for?"
    else:
        response = f"I'm not sure how to respond to: '{text}'"

    speak(response)
    return response
