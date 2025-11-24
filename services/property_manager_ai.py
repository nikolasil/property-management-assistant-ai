import asyncio
import logging

from core.data_repository import DataRepository
from core.llm_client import LLMClient
from core.email.imap_reader import IMAPReader
from core.email.email_parser import parse_email
from core.email.smtp_sender import SMTPSender
from core.models import EmailMessage
from core.workflows.dispatcher import WorkflowDispatcher

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


class PropertyManagerAi:
    def __init__(self, concurrency: int = 2, polling: int = 2, max_retries: int = 2, unread_days_back: int = 1):
        self.concurrency = concurrency
        self.max_retries = max_retries
        self.polling = polling
    
        self.imap = IMAPReader(days_back=unread_days_back)
        self.smtp = SMTPSender()
        self.data_repo = DataRepository()
        self.llm = LLMClient()
        self.dispatcher = WorkflowDispatcher()
        self.semaphore = asyncio.Semaphore(self.concurrency)

    async def run_once(self):
        """Fetch unread emails and process them asynchronously using a persistent SMTP connection."""
        logger.info("Checking for unread emails...")

        try:
            async with self.smtp.connection() as smtp_conn:
                # Collect tasks but ensure they all run inside the connection context
                tasks = [
                    self.process_email(raw_email, smtp_conn)
                    async for raw_email in self.fetch_unread_stream()
                ]

                if tasks:
                    # Run all tasks concurrently with semaphore control
                    await asyncio.gather(*tasks)

            await asyncio.sleep(self.polling)
        except Exception as e:
            logger.error(f"Error in run_once: {e}")

    async def fetch_unread_stream(self):
        """Async generator yielding unread emails one by one."""
        try:
            async for raw in self.imap.fetch_unread_stream():
                yield raw
        except Exception as e:
            logger.error(f"Failed to fetch emails: {e}")

    async def process_email(self, raw_email: bytes, smtp_conn):
        """Parse and reply to a single email with concurrency control."""
        async with self.semaphore:
            email_message = await self.safe_parse_email(raw_email)
            if not email_message:
                return

            retries = 0
            while retries <= self.max_retries:
                try:
                    await self.handle_email(email_message, smtp_conn)
                    break  # success
                except Exception as e:
                    retries += 1
                    logger.warning(f"Retry {retries}/{self.max_retries} for {email_message.sender}: {e}")
                    await asyncio.sleep(1 * retries)  # exponential backoff

    @staticmethod
    async def safe_parse_email(raw: bytes) -> EmailMessage | None:
        """Parse raw email asynchronously using a thread pool."""
        try:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, parse_email, raw)
        except Exception as e:
            logger.error(f"Failed to parse email: {e}")
            return None

    async def handle_email(self, email_message: EmailMessage, smtp_conn):
        """Generate LLM response and send email using a persistent SMTP connection."""
        logger.info(f"Processing email from {email_message.sender}, subject: {email_message.subject}")

        context = await self._get_context(email_message.sender)

        # LLM call is async
        llm_response = await self.llm.generate_response_async(email=email_message, context=context)

        await self._trigger_workflows(llm_response=llm_response, context=context, email_message=email_message)

        # Send reply
        await self.smtp.send_email_async(
            to=email_message.sender,
            cc=self.data_repo.get_stakeholders_for_intent(llm_response.intent),
            subject=f"Re: {email_message.subject}",
            body=llm_response.reply,
            connection=smtp_conn
        )

    async def _get_context(self, sender: str):
        """Retrieve context using executor to avoid blocking."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.data_repo.get_full_context_for_email, sender)

    async def _trigger_workflows(self, email_message, context, llm_response):
        workflow_result = self.dispatcher.dispatch(
            intent=llm_response.intent,
            action_items=llm_response.action_items,
            email_message=email_message,
            context=context
        )

        if workflow_result:
            logger.info(f"Workflow executed: {workflow_result}")
        else:
            logger.info("No workflow actions required.")
