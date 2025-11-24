from flask import Flask, render_template, request, jsonify
import subprocess
import json
import os

app = Flask(__name__)

DATA_FILE = "wifi_data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_wifi_strength():
    try:
        result = subprocess.check_output(
            "netsh wlan show interfaces", shell=True
        ).decode(errors="ignore")

        for line in result.split("\n"):
            line = line.strip()
            if line.startswith("Signal"):
                percent = line.split(":")[1].replace("%", "").strip()
                return int(percent)
        return None
    except:
        return None


@app.route("/")
def home():
    data = load_data()
    return render_template("index.html", data=data)


@app.route("/measure", methods=["POST"])
def measure():
    room = request.form["room"].strip()
    if not room:
        return jsonify({"status": "error", "message": "Room name required."})

    strength = get_wifi_strength()
    if strength is None:
        return jsonify({"status": "error", "message": "Could not read WiFi strength"})

    data = load_data()

    # REMOVE OLD ENTRY IF ROOM ALREADY EXISTS (no duplicates)
    data = [item for item in data if item["room"].lower() != room.lower()]

    # ADD NEW ENTRY
    data.append({"room": room, "strength": strength})
    save_data(data)

    return jsonify({"status": "success", "strength": strength})


@app.route("/delete", methods=["POST"])
def delete():
    room = request.form["room"].strip()

    data = load_data()
    data = [item for item in data if item["room"] != room]
    save_data(data)

    return jsonify({"status": "success"})


@app.route("/reset", methods=["POST"])
def reset():
    save_data([])  # wipe file
    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(debug=True)
