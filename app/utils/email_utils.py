import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings


def send_otp_email(to_email: str, otp: str):

    try:
        subject = "Voting Login OTP"

        body = f"""
Hello,

Your OTP for login is:

{otp}

OTP expires in 5 minutes.
"""

        msg = MIMEMultipart()
        msg["From"] = settings.FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)

        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        server.sendmail(settings.FROM_EMAIL, to_email, msg.as_string())

        server.quit()

        print("OTP email sent successfully")

    except Exception as e:
        print("Email sending failed:", e)
        raise