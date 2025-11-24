from typing import List
import aiosmtplib
from email.mime.text import MIMEText
import logging
from config.settings import settings
from contextlib import asynccontextmanager

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


class SMTPSender:
    def __init__(self) -> None:
        self.host: str = settings.SMTP_HOST
        self.port: int = getattr(settings, "SMTP_PORT", 465)
        self.user: str = settings.SMTP_USER
        self.password: str = settings.SMTP_PASSWORD
        
    @asynccontextmanager
    async def connection(self):
        """
        Async context manager for a persistent SMTP connection.
        Usage:
            async with smtp_sender.connection() as conn:
                await smtp_sender.send_email_async(..., connection=conn)
        """
        conn = aiosmtplib.SMTP(
            hostname=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            use_tls=True,
        )
        try:
            await conn.connect()
            logger.debug("Connected to SMTP server %s:%s", self.host, self.port)
            yield conn
        finally:
            await conn.quit()
            logger.debug("Disconnected from SMTP server %s:%s", self.host, self.port)

    async def send_email_async(
        self, to: str, cc: List[str], subject: str, body: str, connection: aiosmtplib.SMTP | None = None
    ) -> None:
        """
        Sends an email asynchronously. If a connection is provided, reuse it.
        """
        msg = MIMEText(body)
        msg["From"] = self.user
        msg["To"] = to
        msg["Cc"] = ", ".join(cc)
        msg["Subject"] = subject

        try:
            if connection:
                await connection.send_message(msg)
            else:
                # One-off connection
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
