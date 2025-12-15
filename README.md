Email Assistant — Backend Engineering Project

An AI-powered email assistant that connects to an email inbox, reads unread messages, extracts relevant context, generates intelligent replies using OpenAI, and triggers workflow actions such as creating tickets or sending automated responses.

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
    git clone https://github.com/nikolasil/property-management-assistant-ai.git
    cd property-management-assistant-ai

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

#### Non-Functional

✅ Clean modular project layout
✅ Python ≥ 3.10
✅ Async-friendly LLM integration with OpenAI
✅ Mimicked data is sufficient for testing
✅ No deployment required
✅ Dependencies listed in requirements.txt

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
