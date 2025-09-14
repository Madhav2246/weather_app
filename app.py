from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_KEY")  # store API key in .env


@app.route("/", methods=["GET", "POST"])
def home():
    weather_data = None
    condition = None
    time_of_day = None
    error = None

    if request.method == "POST":
        city = request.form.get("city", "").strip()

        if not city:
            error = "⚠️ Please enter a city."
        else:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()

            if data.get("cod") != 200:
                error = f"⚠️ {data.get('message', 'City not found').capitalize()}."
            else:
                # Sunrise & Sunset
                sunrise = data["sys"]["sunrise"]
                sunset = data["sys"]["sunset"]
                current_time = datetime.utcfromtimestamp(data["dt"] + data["timezone"])

                if sunrise <= int(current_time.timestamp()) <= sunset:
                    time_of_day = "day"
                else:
                    time_of_day = "night"

                # Weather data for template
                weather_data = {
                    "city": data["name"],
                    "description": data["weather"][0]["description"].capitalize(),
                    "temp": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "temp_min": data["main"]["temp_min"],
                    "temp_max": data["main"]["temp_max"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "wind": data["wind"]["speed"],
                    "sunrise": sunrise,
                    "sunset": sunset
                }
                condition = data["weather"][0]["main"].lower()  # e.g. "clear", "clouds", "rain", "snow", "thunderstorm"

    return render_template(
        "index.html",
        weather=weather_data,
        condition=condition or "",
        time_of_day=time_of_day or "",
        error=error
    )


if __name__ == "__main__":
    # Bind to 0.0.0.0 so Docker can expose the port
    app.run(host="0.0.0.0", port=5000, debug=True)
