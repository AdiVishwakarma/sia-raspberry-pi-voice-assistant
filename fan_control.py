import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ATOMBERG_API_KEY")
REFRESH_TOKEN = os.getenv("ATOMBERG_REFRESH_TOKEN")

BASE_URL = "https://api.developer.atomberg-iot.com"
DEVICE_ID = "588c817a1c90"  # Adi Fan


def get_access_token():
    response = requests.get(
        f"{BASE_URL}/v1/get_access_token",
        headers={
            "accept": "application/json",
            "x-api-key": API_KEY,
            "Authorization": f"Bearer {REFRESH_TOKEN}",
        },
        timeout=15,
    )

    response.raise_for_status()
    return response.json()["message"]["access_token"]


def send_command(access_token, command):
    response = requests.post(
        f"{BASE_URL}/v1/send_command",
        headers={
            "accept": "application/json",
            "x-api-key": API_KEY,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json={
            "device_id": DEVICE_ID,
            "command": command
        },
        timeout=15,
    )

    response.raise_for_status()
    return response.json()


def main():
    if not API_KEY or not REFRESH_TOKEN:
        print("❌ API credentials missing in .env")
        return

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python fan_control.py on")
        print("  python fan_control.py off")
        print("  python fan_control.py speed 4")
        return

    action = sys.argv[1].lower()

    if action == "on":
        command = {"power": True}

    elif action == "off":
        command = {"power": False}

    elif action == "speed":
        if len(sys.argv) < 3:
            print("❌ Speed missing. Example: python fan_control.py speed 4")
            return

        speed = int(sys.argv[2])

        if speed < 1 or speed > 6:
            print("❌ Speed must be between 1 and 6")
            return

        command = {"speed": speed}

    else:
        print("❌ Unknown command")
        return

    print("Getting access token...")
    access_token = get_access_token()

    print("Sending command...")
    result = send_command(access_token, command)

    print("✅ Command sent successfully")
    print(result)


if __name__ == "__main__":
    main()
