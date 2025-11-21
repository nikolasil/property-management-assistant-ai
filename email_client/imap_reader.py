import imaplib
from typing import List, Optional
import logging
from config.settings import settings

# Configure logger for this module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


class IMAPReader:
    def __init__(self) -> None:
        self.host: str = settings.IMAP_HOST
        self.user: str = settings.IMAP_USER
        self.password: str = settings.IMAP_PASSWORD

    def connect(self) -> imaplib.IMAP4_SSL:
        """
        Connects and logs in to the IMAP server.
        """
        logger.debug("Connecting to IMAP server %s", self.host)
        mail: imaplib.IMAP4_SSL = imaplib.IMAP4_SSL(self.host)
        mail.login(self.user, self.password)
        logger.info("Logged in as %s", self.user)
        return mail

    def fetch_unread_emails(self) -> List[bytes]:
        """
        Returns a list of raw email bytes for each unread email.
        """
        try:
            mail: imaplib.IMAP4_SSL = self.connect()
            mail.select("inbox")

            status: str
            messages_raw: List[bytes]
            status, messages_raw = mail.search(None, "(UNSEEN)")
            if status != "OK" or not messages_raw:
                logger.info("No unread emails found.")
                return []

            email_ids: List[str] = [eid.decode("utf-8") for eid in messages_raw[0].split()]
            logger.info("Found %d unread emails.", len(email_ids))

            raw_emails: List[bytes] = []

            for eid in email_ids:
                fetch_status, fetch_data = mail.fetch(eid, "(RFC822)")
                if fetch_status != "OK" or not fetch_data:
                    logger.warning("Failed to fetch email ID %s", eid)
                    continue

                # filter out only tuples with payload
                for item in fetch_data:
                    if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], (bytes, type(None))):
                        payload: Optional[bytes] = item[1]
                        if payload is not None:
                            raw_emails.append(payload)

            logger.info("Fetched %d raw emails.", len(raw_emails))
            return raw_emails

        except imaplib.IMAP4.error as e:
            logger.error("IMAP error: %s", e)
            return []
        except Exception as e:
            logger.exception("Unexpected error while fetching emails: %s", e)
            return []
