import os
import requests

API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_forecast(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city},TR&appid={API_KEY}&units=metric&lang=tr"
    response = requests.get(url)
    data = response.json()

    if "list" not in data:
        return f"{city} için hava durumu alınamadı: {data.get('message', 'Bilinmeyen hata')}"

    forecast_output = f"<h2>{city} - 5 Günlük Hava Durumu</h2><ul>"
    dates_added = set()

    for entry in data["list"]:
        dt_txt = entry["dt_txt"].split(" ")[0]
        if dt_txt not in dates_added:
            temp = entry["main"]["temp"]
            desc = entry["weather"][0]["description"]
            forecast_output += f"<li><strong>{dt_txt}:</strong> {desc.capitalize()}, {temp:.1f}°C</li>"
            dates_added.add(dt_txt)
        if len(dates_added) >= 5:
            break

    forecast_output += "</ul>"
    return forecast_output
