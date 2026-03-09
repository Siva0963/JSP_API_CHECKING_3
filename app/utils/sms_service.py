from twilio.rest import Client
from app.core.config import settings


class SMSService:

    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN
    )

    @staticmethod
    def send_otp(mobile: str, otp: str):

        message = SMSService.client.messages.create(
            body=f"Your Voting System OTP is {otp}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=mobile
        )

        return message.sid