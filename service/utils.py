import os
import mailtrap as mt

def send_mailtrap_email(to_email, subject, text_content, html_content=None):
    client = mt.MailtrapClient(token=os.getenv("MAILTRAP_API_TOKEN"))

    mail = mt.Mail(
        sender=mt.Address(email="smtp@mailtrap.io", name="groops"),
        to=[mt.Address(email=to_email)],
        subject=subject,
        text=text_content,
        html=html_content or f"<p>{text_content}</p>",
        category="App Notification"
    )

    response = client.send(mail)
    return response
