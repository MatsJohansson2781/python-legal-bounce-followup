from datetime import date
from unittest.mock import Mock

from src.legal_followup import FollowUpService, MatterIntake
from src.infrai_client import InfraiClient


def test_hard_bounce_suppresses_delivery():
    client = Mock()
    service = FollowUpService(client)
    service.record_hard_bounce("Client@Example.com")
    matter = MatterIntake("MAT-1", "client@example.com", "signed.pdf", date(2026, 1, 1))
    assert service.follow_deadline(matter, date(2026, 1, 2)) == "suppressed"
    client.send_email.assert_not_called()


def test_due_matter_sends_and_returns_message_id():
    client = Mock()
    client.send_email.return_value = {"ok": True, "data": {"message_id": "msg-7"}}
    service = FollowUpService(client)
    matter = MatterIntake("MAT-2", "a@example.com", "signed.pdf", date(2026, 1, 1))
    assert service.follow_deadline(matter, date(2026, 1, 2)) == "msg-7"


def test_rate_limit_error_envelope_retries(monkeypatch):
    monkeypatch.setenv("INFRAI_API_KEY", "test-key")
    limited = Mock(status_code=429, headers={"Retry-After": "0"})
    limited.json.return_value = {"ok": False, "error": {"code": "RATE_LIMITED"}}
    success = Mock(status_code=200, headers={})
    success.json.return_value = {"ok": True, "data": {"message_id": "msg-7"}}
    request = Mock(side_effect=[limited, success])
    monkeypatch.setattr("src.infrai_client.requests.request", request)
    monkeypatch.setattr("src.infrai_client.time.sleep", lambda _: None)

    assert InfraiClient().send_email("chenhua@changba.com", "subject", "body") == success.json.return_value
    assert request.call_count == 2
