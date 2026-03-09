import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FAST2SMS_API_KEY")
URL = os.getenv("FAST2SMS_URL")


def send_otp_sms(phone: str, otp: str):

    querystring = {
        "route": "otp",
        "variables_values": otp,
        "numbers": phone,
        "flash": "0"
    }

    headers = {
        "authorization": API_KEY
    }

    response = requests.get(URL, headers=headers, params=querystring)

    return response.json()