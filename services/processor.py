from typing import List
import logging

from email_client.imap_reader import IMAPReader
from email_client.email_parser import parse_email
from email_client.smtp_sender import SMTPSender
from core.models import EmailMessage
from config.texts import EmailTexts

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class EmailProcessor:
    def __init__(self) -> None:
        self.imap: IMAPReader = IMAPReader()
        self.smtp: SMTPSender = SMTPSender()

    def run_once(self) -> None:
        """Fetch unread emails, parse them, and reply."""
        raw_emails: List[bytes] = self.fetch_unread()
        if not raw_emails:
            logger.info("No unread emails.")
            return

        email_messages: List[EmailMessage] = self.parse_emails(raw_emails)

        for email_message in email_messages:
            self.handle_email(email_message)

    def fetch_unread(self) -> List[bytes]:
        """Fetch unread raw email bytes from IMAP."""
        logger.info("Checking for unread emails...")
        try:
            return self.imap.fetch_unread_emails()
        except Exception as e:
            logger.error(f"Failed to fetch unread emails: {e}")
            return []

    def parse_emails(self, raw_emails: List[bytes]) -> List[EmailMessage]:
        """Parse raw email bytes into EmailMessage objects."""
        messages: List[EmailMessage] = []
        for raw in raw_emails:
            try:
                email_message: EmailMessage = parse_email(raw)
                messages.append(email_message)
            except Exception as e:
                logger.error(f"Failed to parse email: {e}")
        return messages

    def handle_email(self, email_message: EmailMessage) -> None:
        """Process a single email: log it and send a reply."""
        try:
            logger.info(f"Processing email from {email_message.sender}, subject: {email_message.subject}")

            reply_text: str = EmailTexts.REPLY_TEMPLATE.format(
                greeting=EmailTexts.REPLY_GREETING,
                body_prefix=EmailTexts.REPLY_BODY_PREFIX,
                body=email_message.body,
                thank_you=EmailTexts.REPLY_THANK_YOU,
            )

            self.smtp.send_email(
                to=email_message.sender,
                subject=EmailTexts.REPLY_SUBJECT_PREFIX.format(email_message.subject),
                body=reply_text,
            )

            logger.info(f"Sent reply to {email_message.sender}")
        except Exception as e:
            logger.error(f"Error handling email from {email_message.sender}: {e}")
