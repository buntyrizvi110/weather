from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
DEFAULT_CITY = "Dubai"   # fallback city


def get_city_from_ip(ip: str):
    try:
        if ip.startswith("127.") or ip == "localhost":
            return "Sharjah"  # local testing → skip IP lookup

        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url)
        data = response.json()

        if data.get("status") == "success":
            return data.get("city")
        return None
    except:
        return None


@app.get("/temperature")
async def get_temperature(request: Request):
    ip = request.headers.get("X-Forwarded-For") or request.client.host

    city = get_city_from_ip(ip) or DEFAULT_CITY

    weather_url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    response = requests.get(weather_url)
    data = response.json()

    if response.status_code != 200:
        return [f"error: {data.get('message', 'Unable to fetch temperature')}"]

    temperature = data["main"]["temp"]
    description = data["weather"][0]["description"]

    return [
        f"detected_city: {city}",
        f"temperature_celsius: {temperature}",
        f"weather: {description}"
    ]


