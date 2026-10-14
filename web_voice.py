from flask import Flask, request, jsonify, render_template_string
from assistant import process_command

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Adi Smart Home</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background: #f5f5f5;
            margin: 0;
            padding: 50px 20px;
        }

        h1 {
            font-size: 42px;
            margin-bottom: 40px;
        }

        button {
            font-size: 24px;
            padding: 20px 40px;
            border: none;
            border-radius: 16px;
            background: white;
            cursor: pointer;
            box-shadow: 0 5px 20px rgba(0,0,0,0.12);
        }

        button:active {
            transform: scale(0.97);
        }

        #status {
            margin-top: 30px;
            font-size: 20px;
        }

        #heard {
            margin-top: 15px;
            font-size: 18px;
            color: #666;
        }
    </style>
</head>

<body>

    <h1>🏠 Adi Smart Home</h1>

    <button onclick="startListening()">
        🎤 Speak
    </button>

    <div id="status">
        Press Speak and talk
    </div>

    <div id="heard"></div>

<script>

function startListening() {

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        document.getElementById("status").innerText =
            "❌ Speech recognition supported nahi hai.";
        return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = function() {
        document.getElementById("status").innerText =
            "🎤 Listening...";
        document.getElementById("heard").innerText = "";
    };

    recognition.onspeechstart = function() {
        document.getElementById("status").innerText =
            "👂 Speech detected...";
    };

    recognition.onresult = async function(event) {

        const text =
            event.results[0][0].transcript;

        document.getElementById("heard").innerText =
            "🗣️ You said: " + text;

        document.getElementById("status").innerText =
            "⚙️ Processing...";

        try {

            const response = await fetch("/command", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    command: text
                })
            });

            const data = await response.json();

            if (data.success) {

                document.getElementById("status").innerText =
                    "✅ " + data.message;

            } else {

                document.getElementById("status").innerText =
                    "❌ " + data.message;

            }

        } catch (error) {

            console.error(error);

            document.getElementById("status").innerText =
                "❌ Raspberry Pi connection failed";
        }
    };

    recognition.onerror = function(event) {

        document.getElementById("status").innerText =
            "❌ Speech error: " + event.error;
    };

    recognition.onend = function() {
        console.log("Recognition ended");
    };

    recognition.start();
}

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/command", methods=["POST"])
def command():

    data = request.get_json()

    if not data or not data.get("command"):
        return jsonify({
            "success": False,
            "message": "No command received"
        }), 400

    text = data["command"]

    print(f"\\n🎤 Voice command: {text}")

    try:

        result = process_command(text)

        if result is False:
            return jsonify({
                "success": False,
                "message": "Assistant stopped"
            })

        return jsonify({
            "success": True,
            "message": f"Command executed: {text}"
        })

    except Exception as error:

        print("❌ Error:", error)

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


if __name__ == "__main__":

    print("=" * 50)
    print("        ADI SMART HOME")
    print("=" * 50)
    print("Server: http://0.0.0.0:5000")
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
