import os
import smtplib
import mimetypes
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


class GmailClient:

    def __init__(self, smtp_server: str = 'smtp.gmail.com', port: int = 587, use_tls: bool = True, timeout: int | None = None):
        self.smtp_server = smtp_server
        self.port = port
        self.use_tls = use_tls
        self.timeout = timeout
        self.server = smtplib.SMTP(self.smtp_server, self.port, timeout=self.timeout)
        self.server.ehlo()
        if self.use_tls:
            self.server.starttls()
        self._logged_in = False
        self._email = None

    def login(self, email: str, password: str):
        self.server.login(email, password)
        self._logged_in = True
        self._email = email

    def send_email(self, subject: str, body: str, to, from_addr: str | None = None, html: bool = False): 
        if from_addr is None:   
            from_addr = self._email
        if not from_addr:
            raise ValueError('from_addr must be provided or you must call login() first')

        if isinstance(to, (list, tuple)):
            to_list = list(to)
        else:
            to_list = [to]

        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = ', '.join(to_list)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html' if html else 'plain'))


        self.server.send_message(msg)
        del msg

    def logout(self):
        try:
            self.server.quit()
        finally:
            self._logged_in = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.logout()