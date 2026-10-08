from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.infrai_client import InfraiClient
from src.legal_followup import FollowUpService, MatterIntake


matter = MatterIntake("MAT-104", "chenhua@changba.com", "settlement.pdf", date(2026, 9, 10))
service = FollowUpService(InfraiClient())
print(service.follow_deadline(matter, date.today()))
