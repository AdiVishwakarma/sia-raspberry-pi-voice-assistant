import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ATOMBERG_API_KEY")
REFRESH_TOKEN = os.getenv("ATOMBERG_REFRESH_TOKEN")

BASE_URL = "https://api.developer.atomberg-iot.com"


def main():
    # Check credentials
    if not API_KEY:
        print("❌ ATOMBERG_API_KEY missing in .env")
        return

    if not REFRESH_TOKEN:
        print("❌ ATOMBERG_REFRESH_TOKEN missing in .env")
        return

    session = requests.Session()
    session.trust_env = False

    # -------------------------------
    # STEP 1: Get access token
    # -------------------------------
    print("1. Getting access token...")

    try:
        response = session.get(
            f"{BASE_URL}/v1/get_access_token",
            headers={
                "accept": "application/json",
                "x-api-key": API_KEY,
                "Authorization": f"Bearer {REFRESH_TOKEN}",
            },
            timeout=15,
        )

        print("Auth status:", response.status_code)

    except requests.RequestException as e:
        print("❌ Network/Auth request failed:")
        print(e)
        return

    if response.status_code != 200:
        print("❌ Authentication failed")
        print(response.text)
        return

    try:
        data = response.json()
    except ValueError:
        print("❌ API returned invalid JSON")
        print(response.text)
        return

    message = data.get("message", {})

    if not isinstance(message, dict):
        print("❌ Unexpected API response:")
        print(data)
        return

    access_token = message.get("access_token")

    if not access_token:
        print("❌ Access token not found in response")
        print(data)
        return

    print("✅ Authentication successful")

    # -------------------------------
    # STEP 2: Get device list
    # -------------------------------
    print("\n2. Fetching Atomberg devices...")

    try:
        response = session.get(
            f"{BASE_URL}/v1/get_list_of_devices",
            headers={
                "accept": "application/json",
                "x-api-key": API_KEY,
                "Authorization": f"Bearer {access_token}",
            },
            timeout=15,
        )

        print("Device API status:", response.status_code)

    except requests.RequestException as e:
        print("❌ Device request failed:")
        print(e)
        return

    if response.status_code != 200:
        print("❌ Failed to fetch devices")
        print(response.text)
        return

    try:
        device_data = response.json()
    except ValueError:
        print("❌ Device API returned invalid JSON")
        print(response.text)
        return

    message = device_data.get("message", {})

    if not isinstance(message, dict):
        print("❌ Unexpected device response:")
        print(device_data)
        return

    devices = message.get("devices_list", [])

    if not devices:
        print("⚠️ No Atomberg devices found on this account.")
        return

    print(f"✅ Found {len(devices)} device(s)\n")

    # -------------------------------
    # STEP 3: Print device details
    # -------------------------------
    for index, device in enumerate(devices, start=1):
        print(f"Device {index}")
        print("-" * 40)

        print("Name     :", device.get("name"))
        print("Device ID:", device.get("device_id"))
        print("Model    :", device.get("model"))
        print("Firmware :", device.get("firmware_version"))
        print("Room     :", device.get("room"))
        print("MAC      :", device.get("mac_address"))

        print()


if __name__ == "__main__":
    main()
