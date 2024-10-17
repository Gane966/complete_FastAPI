import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(os.getcwd()) / "app" / ".env")
def send_email(to_address, from_address, subject, body) -> bool:
    try:
        # Set up the server
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_server.starttls()
        smtp_server.login(from_address, "dqti rsmz ayzq canp")  # Use your email password here

        # Create email
        msg = MIMEMultipart()
        msg['From'] = from_address
        msg['To'] = to_address
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        smtp_server.send_message(msg)
        smtp_server.quit()

        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False