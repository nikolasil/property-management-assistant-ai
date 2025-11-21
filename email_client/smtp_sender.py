import smtplib
from email.mime.text import MIMEText
import logging
from config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


class SMTPSender:
    def __init__(self) -> None:
        self.host: str = settings.SMTP_HOST
        self.user: str = settings.SMTP_USER
        self.password: str = settings.SMTP_PASSWORD

    def send_email(self, to: str, subject: str, body: str) -> None:
        """
        Sends an email via SMTP_SSL.
        """
        msg: MIMEText = MIMEText(body)
        msg["From"] = self.user
        msg["To"] = to
        msg["Subject"] = subject

        try:
            logger.debug("Connecting to SMTP server %s", self.host)
            with smtplib.SMTP_SSL(self.host) as server:
                server.login(self.user, self.password)
                server.sendmail(self.user, [to], msg.as_string())
            logger.info("Sent email to %s with subject '%s'", to, subject)

        except smtplib.SMTPException as e:
            logger.error("SMTP send error to %s: %s", to, e)
        except Exception as e:
            logger.exception("Unexpected error while sending email to %s: %s", to, e)
