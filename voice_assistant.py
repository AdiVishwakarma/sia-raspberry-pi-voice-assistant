import speech_recognition as sr
from assistant import process_command


recognizer = sr.Recognizer()


def listen():
    with sr.Microphone() as source:
        print("🎤 Listening...")

        recognizer.adjust_for_ambient_noise(source, duration=1)

        try:
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=7
            )
        except sr.WaitTimeoutError:
            print("⏱️ Kuch suna nahi.")
            return None

    try:
        text = recognizer.recognize_google(
            audio,
            language="hi-IN"
        )

        print(f"🗣️ You said: {text}")
        return text

    except sr.UnknownValueError:
        print("❓ Speech samajh nahi aayi.")
        return None

    except sr.RequestError as e:
        print(f"❌ Speech recognition error: {e}")
        return None


def main():
    print("======================================")
    print("      Adi Voice Smart Home")
    print("======================================")
    print("Press Ctrl+C to stop.\n")

    while True:
        try:
            command = listen()

            if command:
                if not process_command(command):
                    break

        except KeyboardInterrupt:
            print("\nBye 👋")
            break

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
