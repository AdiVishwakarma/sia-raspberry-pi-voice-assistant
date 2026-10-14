import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ATOMBERG_API_KEY")
REFRESH_TOKEN = os.getenv("ATOMBERG_REFRESH_TOKEN")

BASE_URL = "https://api.developer.atomberg-iot.com"

# ---------------------------------------
# FAN DEVICE IDs
# ---------------------------------------

FANS = {
    "living left": "a846746f30d8",
    "living right": "a84674e9dd28",
    "adi fan": "588c817a1c90",
    "sheela fan": "a846746d8620",
}


# ---------------------------------------
# FAN ALIASES
# ---------------------------------------

FAN_ALIASES = {
    # Living Left
    "living left": "living left",
    "living left fan": "living left",
    "living room left": "living left",
    "living room left fan": "living left",
    "living room ka left fan": "living left",
    "living room ke left fan": "living left",
    "living room ka left": "living left",
    "living room ke left": "living left",
    "left fan living room": "living left",

    # Living Right
    "living right": "living right",
    "living right fan": "living right",
    "living room right": "living right",
    "living room right fan": "living right",
    "living room ka right fan": "living right",
    "living room ke right fan": "living right",
    "living room ka right": "living right",
    "living room ke right": "living right",
    "right fan living room": "living right",

    # Adi Fan / Common Bedroom
    "adi fan": "adi fan",
    "adi's fan": "adi fan",
    "adis fan": "adi fan",
    "common bedroom fan": "adi fan",
    "common bedroom ka fan": "adi fan",
    "common bedroom ke fan": "adi fan",
    "common bedroom": "adi fan",

    # Sheela Fan / Master Bedroom
    "sheela fan": "sheela fan",
    "sheela's fan": "sheela fan",
    "sheelas fan": "sheela fan",
    "master bedroom fan": "sheela fan",
    "master bedroom ka fan": "sheela fan",
    "master bedroom ke fan": "sheela fan",
    "master bedroom": "sheela fan",
}


# ---------------------------------------
# NORMALIZE TEXT
# ---------------------------------------

def normalize_text(text):
    text = text.lower().strip()

    # Remove common apostrophe variations
    text = text.replace("'", "")
    text = text.replace("’", "")

    # Hindi / Devanagari speech recognition mapping
    replacements = {
        "आदि": "adi",
        "एड़ी": "adi",
        "आदित्य": "adi",

        "फैन": "fan",

        "आफ": "off",
        "ऑफ": "off",
        "औफ": "off",

        "बंद": "off",
        "बन्द": "off",
        "बंद करो": "off",
        "बन्द करो": "off",

        "चालू": "on",
        "चालू करो": "on",

        "स्पीड": "speed",

        "लिविंग": "living",
        "रूम": "room",

        "लेफ्ट": "left",
        "राइट": "right",

        "करो": "karo",
        "कर": "karo",

        "पर": "pe",
        "पे": "pe",
    }

    for hindi, english in replacements.items():
        text = text.replace(hindi, english)

    # Fix common speech recognition result:
    # "adi s fan" → "adi fan"
    text = re.sub(r"\badi\s+s\b", "adi", text)

    # Normalize multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ---------------------------------------
# DETECT FAN
# ---------------------------------------

def detect_fan(text):
    # Longest alias first
    aliases = sorted(
        FAN_ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True
    )

    for alias, fan_name in aliases:
        if alias in text:
            return fan_name

    return None


# ---------------------------------------
# DETECT SPEED
# ---------------------------------------

def detect_speed(text):
    patterns = [
        # speed 4
        r"\bspeed\s*(\d+)\b",

        # speed ko 4
        r"\bspeed\s+ko\s+(\d+)\b",

        # fan speed 4
        r"\bfan\s+speed\s*(\d+)\b",

        # fan speed 4 pe karo
        r"\bfan\s+speed\s*(\d+)\s*(?:pe|par)?\b",

        # fast 4
        r"\bfast\s*(\d+)\b",

        # fan fast 4
        r"\bfan\s+fast\s*(\d+)\b",

        # 4 pe / 4 par
        r"\b(\d+)\s*(?:pe|par)\b",

        # fan 4
        r"\bfan\s+(\d+)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return int(match.group(1))

    return None


# ---------------------------------------
# GET ACCESS TOKEN
# ---------------------------------------

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

    data = response.json()

    return data["message"]["access_token"]


# ---------------------------------------
# SEND ATOMBERG COMMAND
# ---------------------------------------

def send_command(device_id, command):
    access_token = get_access_token()

    response = requests.post(
        f"{BASE_URL}/v1/send_command",
        headers={
            "accept": "application/json",
            "x-api-key": API_KEY,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json={
            "device_id": device_id,
            "command": command,
        },
        timeout=15,
    )

    response.raise_for_status()

    return response.json()


# ---------------------------------------
# PROCESS COMMAND
# ---------------------------------------

def process_command(text):
    original_text = text

    text = normalize_text(text)

    print(f"🧠 Normalized: {text}")

    # -----------------------------------
    # EXIT
    # -----------------------------------

    if text in ["exit", "quit", "bye", "stop"]:
        return False

    # -----------------------------------
    # FAN DETECTION
    # -----------------------------------

    fan_name = detect_fan(text)

    # Default fan if no fan is specified
    if fan_name is None:
        fan_name = "adi fan"

    device_id = FANS[fan_name]

    # -----------------------------------
    # OFF DETECTION
    # -----------------------------------

    off_words = [
        "off",
        "band",
        "bandh",
        "turn off",
        "switch off",
    ]

    is_off_command = any(
        word in text
        for word in off_words
    )

    if "fan" in text and is_off_command:

        print(f"⚙️ Sending OFF command to {fan_name.title()}...")

        result = send_command(
            device_id,
            {"power": False}
        )

        print(f"✅ {fan_name.title()} → OFF")
        print(result.get("message", result))

        return True

    # -----------------------------------
    # ON DETECTION
    # -----------------------------------

    on_words = [
        "on",
        "chalu",
        "turn on",
        "switch on",
    ]

    is_on_command = any(
        word in text
        for word in on_words
    )

    if "fan" in text and is_on_command:

        print(f"⚙️ Sending ON command to {fan_name.title()}...")

        result = send_command(
            device_id,
            {"power": True}
        )

        print(f"✅ {fan_name.title()} → ON")
        print(result.get("message", result))

        return True

    # -----------------------------------
    # SPEED DETECTION
    # -----------------------------------

    speed = detect_speed(text)

    if speed is not None:

        if speed < 1 or speed > 6:
            print("❌ Fan speed 1 se 6 ke beech honi chahiye.")
            return True

        print(
            f"⚙️ Sending speed {speed} "
            f"to {fan_name.title()}..."
        )

        result = send_command(
            device_id,
            {"speed": speed}
        )

        print(f"✅ {fan_name.title()} → Speed {speed}")
        print(result.get("message", result))

        return True

    # -----------------------------------
    # FAN NAME ONLY
    # -----------------------------------

    if fan_name in FANS:

        print(f"✅ Fan detected: {fan_name.title()}")
        print("Use commands like:")
        print("  fan on")
        print("  fan off")
        print("  fan speed 4")

        return True

    # -----------------------------------
    # UNKNOWN COMMAND
    # -----------------------------------

    print(f"❓ Command samajh nahi aaya: {original_text}")

    print("\nExamples:")
    print("  Adi fan off")
    print("  turn off Adi fan")
    print("  Adi fan chalu karo")
    print("  living room ka left fan 5 pe karo")
    print("  living room ka right fan on karo")
    print("  master bedroom fan speed 3 karo")
    print("  fan fast 4")
    print("  fan speed 5")
    print("  exit")

    return True


# ---------------------------------------
# MAIN LOOP
# ---------------------------------------

def main():

    if not API_KEY:
        print("❌ ATOMBERG_API_KEY missing in .env")
        return

    if not REFRESH_TOKEN:
        print("❌ ATOMBERG_REFRESH_TOKEN missing in .env")
        return

    print("=" * 55)
    print("           ADI SMART HOME ASSISTANT")
    print("=" * 55)

    print("Default fan: Adi Fan")
    print("Type 'exit' to quit.")
    print()

    while True:

        try:
            user_input = input("You: ")

            if not user_input.strip():
                continue

            result = process_command(user_input)

            if result is False:
                print("Bye 👋")
                break

        except KeyboardInterrupt:
            print("\nBye 👋")
            break

        except requests.RequestException as error:
            print(f"❌ Atomberg API error: {error}")

        except Exception as error:
            print(f"❌ Error: {error}")


if __name__ == "__main__":
    main()
