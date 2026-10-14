import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ATOMBERG_API_KEY")
REFRESH_TOKEN = os.getenv("ATOMBERG_REFRESH_TOKEN")

BASE_URL = "https://api.developer.atomberg-iot.com"

DEVICES = {
    "Living Left": "a846746f30d8",
    "living right": "a84674e9dd28",
    "Adi Fan": "588c817a1c90",
    "Sheela's Fan": "a846746d8620",
}


def main():
    session = requests.Session()
    session.trust_env = False

    # Get access token
    print("Getting access token...")

    response = session.get(
        f"{BASE_URL}/v1/get_access_token",
        headers={
            "accept": "application/json",
            "x-api-key": API_KEY,
            "Authorization": f"Bearer {REFRESH_TOKEN}",
        },
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()
    access_token = data["message"]["access_token"]

    print("✅ Authentication successful\n")

    # Check state of all fans
    for name, device_id in DEVICES.items():

        print("=" * 60)
        print(f"Fan: {name}")
        print(f"Device ID: {device_id}")

        response = session.get(
            f"{BASE_URL}/v1/get_device_state",
            params={"device_id": device_id},
            headers={
                "accept": "application/json",
                "x-api-key": API_KEY,
                "Authorization": f"Bearer {access_token}",
            },
            timeout=15,
        )

        print("Status:", response.status_code)

        if response.status_code == 200:
            try:
                result = response.json()
                print(json.dumps(result, indent=2))
            except ValueError:
                print(response.text)
        else:
            print("❌ Request failed")
            print(response.text)

        print()


if __name__ == "__main__":
    main()
