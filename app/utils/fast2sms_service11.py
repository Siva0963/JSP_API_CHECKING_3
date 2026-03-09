import os
import httpx
from dotenv import load_dotenv
from app.core.logger import logger

load_dotenv()


class SMSService:

    API_KEY = os.getenv("FAST2SMS_API_KEY")
    BASE_URL = os.getenv("FAST2SMS_URL")

    @staticmethod
    async def send_otp(phone: str, otp: str):

        try:

            params = {
                "route": "otp",
                "variables_values": otp,
                "numbers": phone,
                "flash": "0"
            }

            headers = {
                "authorization": SMSService.API_KEY
            }

            async with httpx.AsyncClient(timeout=10) as client:

                response = await client.get(
                    SMSService.BASE_URL,
                    params=params,
                    headers=headers
                )

            data = response.json()

            if not data.get("return"):
                logger.error(f"Fast2SMS failed: {data}")
                raise Exception("SMS sending failed")

            logger.info(f"OTP SMS sent successfully to {phone}")

            return data

        except Exception as e:

            logger.exception(f"SMS sending error: {str(e)}")

            raise