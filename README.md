# Sia — Raspberry Pi Voice Assistant

Sia is a Python-based voice assistant project built on Raspberry Pi
for smart home automation using compatible Atomberg smart fans.

## Features

- Control fan power and speed using the Atomberg API
- Process voice commands using Python
- Normalize Hindi/Hinglish voice commands
- Flask-based web voice interface
- Wake-word detection experiments using openWakeWord and ONNX

## Tech Stack

Python, Raspberry Pi 3 Model B+, Linux, Flask, REST APIs,
Speech Recognition, Atomberg API, openWakeWord, ONNX

## Project Files

- `assistant.py` — Main assistant logic
- `fan_control.py` — Fan control operations
- `check_state.py` — Device state checking
- `test_atomberg.py` — Atomberg integration testing
- `voice_assistant.py` — Voice assistant functionality
- `web_voice.py` — Web-based voice interface
- `wake_word.py` — Wake-word detection

## Setup

1. Install Python and create a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Configure your local `.env` file using `.env.example`.
4. Run the relevant Python script for the feature you want to use.

## Security

Never commit API keys, refresh tokens, passwords, or other secrets.
