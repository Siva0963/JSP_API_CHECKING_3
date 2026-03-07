import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL


def send_otp_email(to_email: str, otp: str):

    subject = "Voting Login OTP"

    body = f"""
    Hello,

    Your OTP for login is:

    {otp}

    OTP expires in 5 minutes.
    """

    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)

    server.starttls()

    server.login(SMTP_USER, SMTP_PASSWORD)

    server.sendmail(FROM_EMAIL, to_email, msg.as_string())

    server.quit()