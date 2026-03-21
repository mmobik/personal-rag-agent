import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_confirmation_email(email: str, token: str):
    """Отправляет письмо с подтверждением email"""
    message = MIMEMultipart("alternative")
    message["Subject"] = "Подтверждение регистрации"
    message["From"] = settings.SMTP_USER
    message["To"] = email

    # Создаем HTML версию письма
    html = f"""
    <html>
      <body>
        <p>Здравствуйте!</p>
        <p>Для подтверждения вашей почты перейдите по ссылке:</p>
        <p><a href="{settings.BASE_URL}/api/v1/auth/confirm/{token}">Подтвердить email</a></p>
        <p>Или введите этот код подтверждения: {token}</p>
        <p>С уважением,<br>Команда Agent Service</p>
      </body>
    </html>
    """

    # Преобразуем в MIMEText объект
    part = MIMEText(html, "html")
    message.attach(part)

    # Создаем безопасное соединение и отправляем письмо
    context = ssl.create_default_context()
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, email, message.as_string())
