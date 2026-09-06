import os
import random
from datetime import datetime, timedelta
from database.models import SessionLocal, CallRecord
import uuid

session = SessionLocal()

intents = ['balance_inquiry', 'transfer_funds', 'billing_inquiry', 'technical_support', 'password_reset']
dispositions = ['resolved', 'resolved', 'resolved', 'abandoned', 'escalated']

# Today is 2026-09-05
today = datetime(2026, 9, 5, 10, 0, 0)

# Generate 5 calls for today
for i in range(5):
    rec = CallRecord(
        id=str(uuid.uuid4()),
        timestamp=today - timedelta(hours=i),
        duration=random.uniform(30.0, 300.0),
        disposition=random.choice(dispositions),
        intent=random.choice(intents),
        confidence=random.uniform(0.7, 1.0),
        fallback_count=random.randint(0, 2) if random.random() > 0.7 else 0
    )
    session.add(rec)

# Generate 15 calls for this week (last 7 days)
for i in range(15):
    rec = CallRecord(
        id=str(uuid.uuid4()),
        timestamp=today - timedelta(days=random.randint(1, 6), hours=random.randint(0, 23)),
        duration=random.uniform(30.0, 300.0),
        disposition=random.choice(dispositions),
        intent=random.choice(intents),
        confidence=random.uniform(0.7, 1.0),
        fallback_count=random.randint(0, 2) if random.random() > 0.7 else 0
    )
    session.add(rec)

# Generate 20 calls for this month (last 30 days)
for i in range(20):
    rec = CallRecord(
        id=str(uuid.uuid4()),
        timestamp=today - timedelta(days=random.randint(7, 29), hours=random.randint(0, 23)),
        duration=random.uniform(30.0, 300.0),
        disposition=random.choice(dispositions),
        intent=random.choice(intents),
        confidence=random.uniform(0.7, 1.0),
        fallback_count=random.randint(0, 2) if random.random() > 0.7 else 0
    )
    session.add(rec)
    
# Generate 30 calls for this year
for i in range(30):
    rec = CallRecord(
        id=str(uuid.uuid4()),
        timestamp=today - timedelta(days=random.randint(30, 200), hours=random.randint(0, 23)),
        duration=random.uniform(30.0, 300.0),
        disposition=random.choice(dispositions),
        intent=random.choice(intents),
        confidence=random.uniform(0.7, 1.0),
        fallback_count=random.randint(0, 2) if random.random() > 0.7 else 0
    )
    session.add(rec)

session.commit()
print("Successfully generated mock data for today, this week, this month, and this year.")
session.close()

