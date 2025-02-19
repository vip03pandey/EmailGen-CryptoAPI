import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import email.encoders
import requests
import pandas as pd
from datetime import datetime
import schedule


load_dotenv()
email_password = os.getenv("EMAIL_PASSWORD")  

if not email_password:
    raise ValueError("EMAIL_PASSWORD is not set. Please check your .env file.")

def send_mail(subject, body, filename):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_mail = "vipul03pandey@gmail.com"
    receiver_mail = "22102137@mail.jiit.ac.in"

    # Composing email
    message = MIMEMultipart()
    message["From"] = sender_mail
    message["To"] = receiver_mail
    message["Subject"] = subject

    # Attach mail body
    message.attach(MIMEText(body, "plain"))

    # Attaching CSV file
    with open(filename, "rb") as file:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(file.read())
        email.encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename={filename}')
        message.attach(part)

    # Start server
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_mail, email_password)
            server.sendmail(sender_mail, receiver_mail, message.as_string())
            print("✅ Email sent successfully!")

    except Exception as e:
        print(f"❌ Unable to send email: {e}")

# Function to get crypto data
def get_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1
    }

    # Sending request
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("✅ Connection successful")
        data = response.json()
        df = pd.DataFrame(data)

        df = df[[
            "id", "current_price", "market_cap", "price_change_percentage_24h",
            "ath", "atl", "high_24h", "low_24h"
        ]]

        # Creating a new column
        today = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        df["time_stamp"] = today

        top_negative_10 = df.nsmallest(10, "price_change_percentage_24h")
        top_positive_10 = df.nlargest(10, "price_change_percentage_24h")

        # ✅ Safe filename
        file_name = f'crypto_data_{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.csv'
        df.to_csv(file_name, index=False)

        print(f"✅ Data saved successfully as {file_name}")

        subject = f"📊 Crypto Market Report - {today}"
        body = f"""
        Good Morning!
        Your crypto report is here:

        📈 **Top 10 Gainers:** 
        {top_positive_10.to_string(index=False)}

        📉 **Top 10 Losers:** 
        {top_negative_10.to_string(index=False)}

        Regards,
        Your Crypto Bot
        """

        send_mail(subject, body, file_name)
    else:
        print("❌ Connection failed")

if __name__ == "__main__":
    get_crypto_data()
    schedule.every().day.at('08:00').do(get_crypto_data)

    while True:
        schedule.run_pending()