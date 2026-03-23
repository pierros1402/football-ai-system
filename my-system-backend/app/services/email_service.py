import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class EmailService:

    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str):
        message = Mail(
            from_email=os.getenv("EMAIL_FROM"),
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        try:
            sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
            response = sg.send(message)

            print("SENDGRID STATUS:", response.status_code)
            print("SENDGRID BODY:", response.body)
            print("SENDGRID HEADERS:", response.headers)

            return True

        except Exception as e:
            print("SENDGRID ERROR:", e)
            return False
