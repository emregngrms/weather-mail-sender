import pandas as pd
import requests
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

API_KEY = os.getenv("OPENWEATHER_API_KEY")
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def get_forecast(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city},TR&appid={API_KEY}&units=metric&lang=tr"
    response = requests.get(url)
    data = response.json()

    # DEBUG - log api cevabı
    print(f"API cevabı ({city}):", data)

    if "list" not in data:
        return f"{city} için hava durumu alınamadı: {data.get('message', 'Bilinmeyen hata')}"

    forecast_output = f"<h2>{city} - 5 Günlük Hava Durumu</h2><ul>"
    dates_added = set()

    for entry in data["list"]:
        date = entry["dt_txt"].split(" ")[0]
        if date not in dates_added:
            temp = entry["main"]["temp"]
            desc = entry["weather"][0]["description"]
            forecast_output += f"<li><strong>{date}:</strong> {desc.capitalize()}, {temp:.1f}°C</li>"
            dates_added.add(date)
        if len(dates_added) >= 5:
            break

    forecast_output += "</ul>"
    return forecast_output

def send_email(to_list, subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = ", ".join(to_list)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL, EMAIL_PASSWORD)
        server.sendmail(EMAIL, to_list, msg.as_string())

def main():
    df = pd.read_csv("maillist.csv")
    grouped = df.groupby("sehir")["email"].apply(list).to_dict()

    for city, emails in grouped.items():
        try:
            print(f"{city} için hava durumu alınıyor...")
            body = get_forecast(city)
            subject = f"{city} için 5 Günlük Hava Durumu"
            send_email(emails, subject, body)
            print(f"{city} için mail gönderildi.")
        except Exception as e:
            print(f"{city} için hata oluştu: {e}")

if __name__ == "__main__":
    main()
