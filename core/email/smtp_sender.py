import aiosmtplib
from email.mime.text import MIMEText
import logging
from config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


class SMTPSender:
    def __init__(self) -> None:
        self.host: str = settings.SMTP_HOST
        self.port: int = getattr(settings, "SMTP_PORT", 465)
        self.user: str = settings.SMTP_USER
        self.password: str = settings.SMTP_PASSWORD

    async def send_email_async(self, to: str, subject: str, body: str) -> None:
        """
        Sends an email asynchronously using aiosmtplib.
        """
        msg = MIMEText(body)
        msg["From"] = self.user
        msg["To"] = to
        msg["Subject"] = subject

        try:
            logger.debug("Connecting to SMTP server %s:%s", self.host, self.port)
            await aiosmtplib.send(
                msg,
                hostname=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                use_tls=True,
            )
            logger.info("Sent email to %s with subject '%s'", to, subject)

        except aiosmtplib.SMTPException as e:
            logger.error("SMTP send error to %s: %s", to, e)
        except Exception as e:
            logger.exception("Unexpected error while sending email to %s: %s", to, e)
