import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText
import os

# Ortam değişkenlerinden bilgileri çekiyoruz
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
EMAIL = os.getenv('EMAIL')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

def get_weather(city_name):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_name},TR&appid={OPENWEATHER_API_KEY}&units=metric&lang=tr"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def prepare_forecast_text(weather_data):
    daily_forecast = {}
    for entry in weather_data['list']:
        date = entry['dt_txt'].split(' ')[0]
        if date not in daily_forecast:
            description = entry['weather'][0]['description']
            temp = entry['main']['temp']
            daily_forecast[date] = f"{description.capitalize()}, {temp:.1f}°C"
    forecast_text = "\n".join([f"{day}: {info}" for day, info in daily_forecast.items()])
    return forecast_text

def send_email(to_list, subject, body):
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = EMAIL
    msg['To'] = ", ".join(to_list)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL, EMAIL_PASSWORD)
        server.sendmail(EMAIL, to_list, msg.as_string())

def main():
    df = pd.read_excel('maillist.xlsx')
    city_groups = df.groupby('sehir')['email'].apply(list).to_dict()

    for city, emails in city_groups.items():
        try:
            print(f"{city} için hava durumu çekiliyor...")
            weather_data = get_weather(city)
            forecast_text = prepare_forecast_text(weather_data)
            subject = f"{city} Haftalık Hava Durumu Raporu"
            send_email(emails, subject, forecast_text)
            print(f"{city} için e-posta gönderildi.")
        except Exception as e:
            print(f"{city} için hata oluştu: {e}")

if __name__ == "__main__":
    main()
