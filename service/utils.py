import os
import requests

def send_email_resend(to_email, subject, html_content):
    api_key = "re_cmNY5Mok_QoV2oKPFApm6ghZGUhQypnC9"
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": "no-reply@monapp.com",
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
