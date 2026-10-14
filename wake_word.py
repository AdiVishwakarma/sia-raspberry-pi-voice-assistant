import pyaudio
import numpy as np
from openwakeword.model import Model


RATE = 16000
CHANNELS = 1

CHUNK = 1280  # 80 ms at 16 kHz

MODEL_PATH = (
    "/home/sia/atomberg/.venv/lib/python3.13/"
    "site-packages/openwakeword/resources/models/"
    "hey_jarvis_v0.1.onnx"
)


def main():
    print("Loading wake-word model...")

    model = Model(
        wakeword_models=[MODEL_PATH],
        inference_framework="onnx"
    )

    print("✅ Wake-word model loaded")
    print("Waiting for: Hey Jarvis")
    print("Press Ctrl+C to stop.\n")

    audio = pyaudio.PyAudio()

    stream = audio.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    try:
        while True:

            data = stream.read(
                CHUNK,
                exception_on_overflow=False
            )

            audio_data = np.frombuffer(
                data,
                dtype=np.int16
            )

            prediction = model.predict(audio_data)

            for name, score in prediction.items():

                if score > 0.5:
                    print(
                        f"\n🔥 Wake word detected: "
                        f"{name} (score={score:.2f})"
                    )

                    # Later:
                    # start command listening here

    except KeyboardInterrupt:
        print("\nStopped.")

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()


if __name__ == "__main__":
    main()
