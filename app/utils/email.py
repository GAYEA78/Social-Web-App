import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app


def send_waitlist_notification(recipient_email, event_name, event_date):
    """Send notification email to waitlisted user."""
    msg = MIMEMultipart()
    msg["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
    msg["To"] = recipient_email
    msg["Subject"] = f"Spot Available: {event_name}"

    body = f"""
    Hello,

    A spot has become available for the event "{event_name}" on {event_date}.
    Please log in to confirm your registration.

    Best regards,
    The Events Team
    """

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(current_app.config["MAIL_SERVER"], current_app.config["MAIL_PORT"])
        server.starttls()
        server.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False
