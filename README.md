Domos Email Assistant — Backend Engineering Assignment

An AI-powered email assistant for property management that connects to an email inbox, reads unread messages, extracts tenant/unit context, generates intelligent replies using OpenAI, and triggers workflow actions such as maintenance tickets or lockout requests.

The system is fully asynchronous and supports concurrency for efficient email processing.

## 🚀 Features

- Async IMAP & SMTP (supports concurrent processing)
- Email parsing (subject, body, sender)
- Tenant & unit context loading from mock datastore
- Fully asynchronous LLM-powered reply generator using OpenAI
- Intent classification (locked_out, maintenance, rent, general)
- Workflow engine generating action tickets & saving them to JSON
- Concurrency limiting (Semaphore-based)

## ⚙️ Setup & Run Instructions
1. Clone the repository
git clone https://github.com/nikolasil/domos-assignment.git
cd domos-assignment

3. Install dependencies
pip install -r requirements.txt

4. Create a .env file from example file
cp .env.example .env

5. Run the assistant
python main.py

The system will:

- Poll for emails
Defaults:
    - concurrency=2 (emails handled concurrently)
    - polling=2s interval
    - max_retries=2 per email
    - unread_days_back=1
- Generates asynchronous LLM replies
- Create workflow action tickets

Tickets are saved under:
output/*.json

## INFO

1. **Connect to an Inbox**

Implemented with aioimaplib (async IMAP client for Gmail or any inbox). Allows concurrent fetching of emails.

2. **Fetch Unread Messages (Only Recent)**

Supports fetching unread messages from the last n days (unread_days_back=1 by default).

3a. **Load Relevant Information**

Tenant and unit data is mocked via JSON files.
Context lookup based on sender email.
Also there is a stakeholder.json based on the intent to find which stakeholders should be in the Cc section of the mail.

3b. **Generate a Reply**

Fully asynchronous LLM-powered reply generator using AsyncOpenAI.

Input: Raw email + tenant/unit context.
Output: JSON with ready-to-send plain-text reply.
Choice: OpenAI async client ensures non-blocking execution; JSON output enforces structured, consistent responses.
Optional enhancement: Fine-tuning or RAG prompts can improve consistency for repetitive property-management scenarios.

3c. **Create Action Items**

Workflow engine generates JSON tickets for actions like maintenance or lockout.
JSON saved in output/*.json.
Tradeoff: No database yet, but JSON allows easy inspection and extension later.

3d. **Send Email**

Async SMTP implemented via aiosmtplib.

Emails include generated reply and relevant stakeholders (e.g., maintenance team).

Tradeoff: No retry/backoff currently; network errors are logged.

## Non-Functional Expectations

✅ Clean modular project layout

✅ Python ≥ 3.10

✅ Async-friendly LLM integration with OpenAI

✅ Mimicked data is sufficient for testing

✅ No deployment required

✅ Dependencies listed in requirements.txt

## ⚠️ Known Limitations / Tradeoffs

1. **IMAP is partially async**  
    While `aioimaplib` is async, some IMAP operations (especially search and fetch) may internally rely on sync calls due to library limitations.
    Current polling every 2 seconds should be replaced with a more efficient method, like IMAP IDLE or Gmail push notifications.

2. **SMTP is fully async**  
    Using `aiosmtplib` provides true async sending, but network errors are logged and no retry/backoff is implemented.

3. **LLM call is fully asynchronous**
    AsyncOpenAI ensures non-blocking requests, with concurrent execution support.

4. **No persistence layer**  
    Tickets and logs are still stored as JSON files, not in a database.

6. **No conversation history**  
    The LLM receives only single-email context + tenant/unit info

## Enchancements (Future features)

### 🚀 Product / Infrastructure

- Full Gmail OAuth (instead of passwords / app passwords)
- Current polling every 2 seconds should be replaced with a more efficient method, like IMAP IDLE or Gmail push notifications.
- Dockerization
- Web dashboard to view tickets, logs, and email threads
- Postgres persistence for emails and workflows
- Prometheus metrics

### ⚙️ Backend / Code Quality

- Unit tests & integration tests (pytest)
- Retry & backoff strategy for IMAP/SMTP/LLM.
    Now there is only a generic retry for the whole process of handling the mail
- Add internal event bus (Redis)

### 🤖 AI Enhancements

- Embedding-based similarity search for conversation history
- Fine-tuning or RAG prompts for more consistent replies
- Evaluation metrics ("response correctness", "hallucination score")

### 🤖 AI Notes

Used ChatGPT (GPT-4/GPT-5) for architecture planning, async design, prompt design, and refactoring guidance.

AI assisted with:

- Designing the modular folder structure
- Constructing async patterns (semaphores, task spawning, executors)
- Building workflow abstractions
- Creating prompt formats for structured JSON
- Refining error handling and logging
- Improving system robustness and readability
- Even with the documentation (README.md)

What worked well

- Iterating on design and async concurrency model
- Generating high-quality boilerplate while focusing on core logic
- IMAP/SMTP Snippets

Challenges

- IMAP & SMTP async libraries
- Maintaining clean async patterns
- Ensuring LLM always returns valid JSON (needed careful prompting)
- Ensuring the LLM email answer was correct