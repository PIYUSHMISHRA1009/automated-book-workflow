# test_voice.py
from ai.voice import speak, listen

speak("This is a test. Say something after the beep.")
result = listen("Listening now. Please say 'approve' or 'edit' or a number between 1 and 5.")
print("You said:", result)