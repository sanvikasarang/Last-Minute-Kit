from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime


# =========================================================
# FLASK CONFIGURATION
# =========================================================

# index.html and style.css are in the same folder as app.py.
app = Flask(
    __name__,
    template_folder=".",
    static_folder=".",
    static_url_path=""
)


# =========================================================
# HISTORY FILE
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")


def load_history():
    """
    Loads previously saved kits from history.json.
    If the file does not exist or is damaged, an empty
    history list is returned.
    """

    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except (json.JSONDecodeError, OSError):
        pass

    return []


def save_history(history):
    """
    Saves the current kit history to history.json.
    """

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4)


def save_kit(category, duration, weather, kit):
    """
    Saves a newly generated kit.
    """

    history = load_history()

    new_kit = {
        "date": datetime.now().strftime("%d %b %Y"),
        "time": datetime.now().strftime("%I:%M %p"),
        "category": category,
        "duration": duration,
        "weather": weather,
        "items": kit
    }

    # Put newest kit first.
    history.insert(0, new_kit)

    # Keep only the latest 10 kits.
    history = history[:10]

    save_history(history)


# =========================================================
# KIT DATABASE
# =========================================================

BASE_ITEMS = {

    "Travel": [
        "Wallet / Cash",
        "Mobile Phone",
        "Phone Charger",
        "Power Bank",
        "House Keys",
        "Water Bottle",
        "Hand Sanitizer",
        "Tissues",
        "Earphones"
    ],

    "College": [
        "College ID Card",
        "Notebook",
        "Pens",
        "Laptop",
        "Laptop Charger",
        "Water Bottle",
        "College Bag",
        "Hand Sanitizer"
    ],

    "Work": [
        "Office ID Card",
        "Notebook",
        "Pens",
        "Laptop",
        "Laptop Charger",
        "Water Bottle",
        "Documents",
        "Hand Sanitizer"
    ],

    "Gym": [
        "Gym Clothes",
        "Sports Shoes",
        "Water Bottle",
        "Towel",
        "Earphones",
        "Gym Lock",
        "Energy Snack"
    ],

    "Emergency": [
        "First Aid Kit",
        "Emergency Contact Information",
        "Water Bottle",
        "Power Bank",
        "Flashlight",
        "Basic Medicines",
        "Important Documents"
    ]
}


# =========================================================
# DURATION ITEMS
# =========================================================

EXTRA_ITEMS = {

    "Short": [
        "Small Snack"
    ],

    "Medium": [
        "Extra Clothes",
        "Toiletries"
    ],

    "Long": [
        "Extra Clothes",
        "Toiletries",
        "Extra Footwear",
        "Laundry Bag",
        "Travel Documents"
    ]
}


# =========================================================
# WEATHER ITEMS
# =========================================================

SPECIAL_ITEMS = {

    "Normal": [],

    "Rainy": [
        "Umbrella",
        "Raincoat",
        "Waterproof Bag"
    ],

    "Hot": [
        "Sunglasses",
        "Cap",
        "Sunscreen",
        "Extra Water"
    ],

    "Cold": [
        "Jacket",
        "Warm Socks",
        "Moisturizer"
    ]
}


# =========================================================
# KIT GENERATOR
# =========================================================

def generate_kit(category, duration, weather):

    kit = []

    # Situation-specific items
    if category in BASE_ITEMS:
        kit.extend(BASE_ITEMS[category])

    # Duration-specific items
    if duration in EXTRA_ITEMS:
        kit.extend(EXTRA_ITEMS[duration])

    # Weather-specific items
    if weather in SPECIAL_ITEMS:
        kit.extend(SPECIAL_ITEMS[weather])

    # Remove duplicates while preserving order.
    final_kit = []

    for item in kit:
        if item not in final_kit:
            final_kit.append(item)

    return final_kit


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/", methods=["GET", "POST"])
def home():

    kit = []
    submitted = False

    category = ""
    duration = ""
    weather = ""

    history = load_history()

    if request.method == "POST":

        category = request.form.get("category", "")
        duration = request.form.get("duration", "")
        weather = request.form.get("weather", "")

        if category and duration and weather:

            kit = generate_kit(
                category,
                duration,
                weather
            )

            save_kit(
                category,
                duration,
                weather,
                kit
            )

            submitted = True

            # Reload history so the new kit appears immediately.
            history = load_history()

    return render_template(
        "index.html",
        kit=kit,
        submitted=submitted,
        category=category,
        duration=duration,
        weather=weather,
        history=history
    )


# =========================================================
# CLEAR HISTORY
# =========================================================

@app.route("/clear-history", methods=["POST"])
def clear_history():

    save_history([])

    return redirect(url_for("home"))


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)