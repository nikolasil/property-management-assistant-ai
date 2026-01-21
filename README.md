# AI-Powered Property Management Assistant (Async Backend)

An industrial-grade backend service designed to automate property management communication. This system utilizes **Asynchronous I/O** to poll email servers, classify tenant intent using **LLMs**, and execute automated workflows—all while maintaining high throughput through concurrency control.

## 🛠️ Tech Stack & Engineering Focus

* **Runtime:** Python 3.10+ (utilizing `asyncio` for non-blocking I/O)
* **AI Orchestration:** OpenAI API (Structured JSON outputs)
* **Protocols:** IMAP (`aioimaplib`) & SMTP (`aiosmtplib`)
* **Design Patterns:** Semaphore-based concurrency limiting, Strategy-based intent classification, Modular Workflow Engine

## 🏗️ Architecture & Data Flow

The system operates on an asynchronous polling loop designed to handle multiple emails simultaneously without blocking the main execution thread.

1.  **Ingestion:** The `AsyncIMAP` client fetches unread messages from a specified window (default: 24h).
2.  **Context Enrichment:** Maps the sender's email against a mock datastore (`tenants.json`) to retrieve unit history and lease details.
3.  **Intelligence:** * **Intent Classification:** Categorizes requests into `locked_out`, `maintenance`, `rent`, or `general`.
    * **Stakeholder Mapping:** Dynamically looks up relevant contacts (e.g., locksmiths or maintenance leads) based on intent.
4.  **Action:** Simultaneously generates a professional email reply and exports a structured **Action Ticket** (JSON) for downstream CRM integration.

## 🚀 Key Engineering Features

* **Concurrency Control:** Uses an `asyncio.Semaphore` to limit simultaneous LLM calls, preventing rate-limiting and managing system resources effectively.
* **Structured Outputs:** Leverages OpenAI's JSON mode to ensure the workflow engine receives predictable data, eliminating "hallucination" in ticket creation.
* **Non-Blocking I/O:** Every network call (Email fetch, LLM generation, SMTP send) is awaited, allowing the assistant to scale horizontally without thread-locking.

## 📊 System Demonstration

### Example Workflow Execution

**1. Input (Raw Tenant Email):**
> "Hi, I'm from Apt 4B. I've lost my keys and I'm stuck outside. Can someone help?"

**2. System Logic:**
* **Identified Tenant:** Nikolas (Apt 4B) via `tenants.json`
* **Classified Intent:** `locked_out`
* **Async Task:** Generating professional reply + notifying Locksmith.

**3. Output (Generated Workflow Ticket — `output/ticket_123.json`):**
```json
{
  "tenant": "Nikolas",
  "unit": "4B",
  "intent": "locked_out",
  "priority": "high",
  "action_required": "Dispatch locksmith",
  "notified_stakeholders": [
    "building_manager@example.com", 
    "locksmith_urgent@example.com"
  ]
}
````

---

## 🚦 Getting Started

### Prerequisites
* Python 3.10+
* OpenAI API Key
* App password for your email provider (Gmail/Outlook)

### Installation
```bash
# Clone the repository
git clone [https://github.com/nikolasil/property-management-assistant-ai.git](https://github.com/nikolasil/property-management-assistant-ai.git)
cd property-management-assistant-ai

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
````
