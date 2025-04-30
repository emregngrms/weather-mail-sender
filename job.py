import pandas as pd
import requests
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

API_KEY = os.getenv("WEATHERSTACK_API_KEY")
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def get_forecast(city):
    url = f"http://api.weatherstack.com/forecast?access_key={API_KEY}&query={city}&forecast_days=7&units=m"
    response = requests.get(url)
    data = response.json()

    if "forecast" not in data:
        return f"{city} için hava durumu alınamadı: {data.get('error', {}).get('info', 'Bilinmeyen hata')}"

    forecast_data = data["forecast"]
    output = f"<h2>{city} - 7 Günlük Hava Durumu</h2><ul>"
    for date, day_data in forecast_data.items():
        desc = day_data['weather_descriptions'][0] if 'weather_descriptions' in day_data else 'Açıklama yok'
        temp = day_data['avgtemp']
        output += f"<li><strong>{date}:</strong> {desc}, Ortalama Sıcaklık: {temp}°C</li>"
    output += "</ul>"
    return output

def main():
    df = pd.read_excel("maillist.xlsx")
    grouped = df.groupby("sehir")

    for sehir, group in grouped:
        to_list = group["email"].tolist()
        body = get_forecast(sehir)

        msg = MIMEMultipart()
        msg["From"] = EMAIL
        msg["To"] = ", ".join(to_list)
        msg["Subject"] = f"{sehir} için 7 Günlük Hava Durumu"

        msg.attach(MIMEText(body, "html"))

        try:
            with smtplib.SMTP('smtp.office365.com', 587) as server:
                server.starttls()
                server.login(EMAIL, EMAIL_PASSWORD)
                server.sendmail(EMAIL, to_list, msg.as_string())
                print(f"{sehir} için mail gönderildi.")
        except Exception as e:
            print(f"{sehir} için mail gönderilemedi: {str(e)}")

if __name__ == "__main__":
    main()
