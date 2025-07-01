from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
import smtplib
import os
from pathlib import Path
from django.conf import settings

class EmailProvider:
    def __init__(self, host, port, username, password, use_ssl=True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl

    def send_email(self, sender, recipient, subject, html_content):
        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = recipient
        message['Subject'] = subject
        message.attach(MIMEText(html_content, "html"))
        email_string = message.as_string()

        if self.use_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.host, self.port, context=context) as server:
                server.login(self.username, self.password)
                server.sendmail(sender, recipient, email_string)
        else:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(sender, recipient, email_string)

        return {"success": True}


def get_email_provider():
    return EmailProvider(
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_SENDER,
        password=settings.EMAIL_PASSWORD,
        use_ssl=getattr(settings, 'EMAIL_USE_SSL', True)
    )


def load_template(template_name):
    current_dir = Path(__file__).parent
    template_path = current_dir / 'emails' / template_name
    with open(template_path, 'r') as file:
        return file.read()


def render_template(template_content, context):
    for key, value in context.items():
        template_content = template_content.replace(f"{{{{ {key} }}}}", str(value))
    return template_content


def send_email(template_type, username, recipient_email, link):
    """
    Send an email for one of the template types: 'registration', 'password_reset', or 'email_update'.
    """
    template_map = {
        'registration': {
            'template': 'registration.html',
            'subject': 'Welcome to Prelude Curation'
        },
        'password_reset': {
            'template': 'password_reset.html',
            'subject': 'Prelude Curation Password Reset'
        },
        'email_update': {
            'template': 'email_update.html',
            'subject': 'Prelude Curation Email Update Confirmation'
        }
    }

    if template_type not in template_map:
        return {"success": False, "error": f"Unknown email type: {template_type}"}

    template_info = template_map[template_type]

    context = {'username': username}
    if template_type == 'registration':
        context['registration_link'] = link
    elif template_type == 'password_reset':
        context['reset_link'] = link
    elif template_type == 'email_update':
        context['update_link'] = link

    html_content = render_template(
        load_template(template_info['template']),
        context
    )
    subject = template_info['subject']

    provider = get_email_provider()
    return provider.send_email(
        sender=settings.EMAIL_SENDER,
        recipient=recipient_email,
        subject=subject,
        html_content=html_content
    )