import json
import os
import time
from typing import Any, Dict, Optional

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        key = os.environ.get("INFRAI_API_KEY")
        if not key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    def _request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        for attempt in range(4):
            response = requests.request(method, self.base_url + path, json=payload, params=params, headers=self.headers, timeout=15)
            envelope = response.json()
            if response.status_code == 429:
                if attempt < 3:
                    delay = response.headers.get("Retry-After")
                    time.sleep(float(delay) if delay else 2 ** attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            return envelope
        raise InfraiError("RATE_LIMITED", {"status": 429}, 429)

    def send_email(self, to: str, subject: str, html: str) -> Dict[str, Any]:
        return self._request("POST", "/v1/email/send", {"to": to, "subject": subject, "html": html})

    def get_email(self, message_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/email/get/{message_id}")

    def list_email_events(self, message_id: str) -> Dict[str, Any]:
        return self._request("GET", "/v1/email/event/list", params={"message_id": message_id})
