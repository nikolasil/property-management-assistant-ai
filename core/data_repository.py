import json
import re
from pathlib import Path
from typing import List, Optional

from core.models.intent import Intent


class DataRepository:
    def __init__(self):
        base = Path(__file__).resolve().parent.parent / "data"
        self.tenants_path = base / "tenants.json"
        self.units_path = base / "units.json"
        self.stakeholders_path = base / "stakeholders.json"

        self._tenants = self._load_json(self.tenants_path)
        self._units = self._load_json(self.units_path)
        self._stakeholders = self._load_json(self.stakeholders_path)

    def _load_json(self, path: Path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ---------- LOOKUPS ---------- #


    def find_tenant_by_email(self, sender: str) -> Optional[dict]:
        """
        Finds tenant by sender email.
        Supports formats:
        - 'First Name <email@example.com>'
        - 'email@example.com'
        """
        # Extract email if in <...> format
        match = re.search(r"<(.+?)>", sender)
        email = match.group(1) if match else sender
        email = email.strip().lower()

        return next((t for t in self._tenants if t.get("email", "").lower() == email), None)

    def find_unit(self, unit_id: str):
        for unit in self._units:
            if unit["unit_id"] == unit_id:
                return unit
        return None

    def get_full_context_for_email(self, sender_email: str):
        """
        Returns combined tenant + unit context, or None.
        """
        tenant = self.find_tenant_by_email(sender_email)
        if not tenant:
            return None

        unit = self.find_unit(tenant["unit_id"])

        return {
            "tenant": tenant,
            "unit": unit,
        }

    def get_stakeholders_for_intent(self, intent: Intent) -> List[str]:
        """
        Returns a list of stakeholder emails for a given intent.
        """
        return self._stakeholders.get(intent, [])