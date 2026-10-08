from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Set

from .infrai_client import InfraiClient


@dataclass
class MatterIntake:
    matter_id: str
    client_email: str
    signed_document_name: str
    deadline: date


@dataclass
class FollowUpService:
    client: InfraiClient
    suppressed: Set[str] = field(default_factory=set)
    sent_messages: Dict[str, str] = field(default_factory=dict)

    def record_hard_bounce(self, address: str) -> None:
        self.suppressed.add(address.casefold())

    def deliver_signed_document(self, matter: MatterIntake) -> str:
        address = matter.client_email.casefold()
        if address in self.suppressed:
            return "suppressed"
        reply = self.client.send_email(address, f"Signed document for matter {matter.matter_id}", f"<p>Your signed document: {matter.signed_document_name}</p>")
        message_id = reply["data"]["message_id"]
        self.sent_messages[matter.matter_id] = message_id
        return message_id

    def follow_deadline(self, matter: MatterIntake, today: date) -> str:
        if matter.client_email.casefold() in self.suppressed:
            return "suppressed"
        if today >= matter.deadline:
            return self.deliver_signed_document(matter)
        return "waiting"
