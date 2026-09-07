from database.models import SessionLocal, CallRecord, EmailDeliveryLog
from datetime import datetime

session = SessionLocal()

print("\n" + "="*95)
print(" 📞 IVR ANALYTICS SQLITE DATABASE - RECENT CALL RECORDS")
print("="*95)
print(f"{'CALL ID':<15} | {'TIMESTAMP':<22} | {'INTENT':<20} | {'DISPOSITION':<12} | {'DURATION':<10}")
print("-" * 95)

records = session.query(CallRecord).order_by(CallRecord.timestamp.desc()).limit(15).all()

for r in records:
    ts_str = r.timestamp.strftime("%Y-%m-%d %H:%M:%S") if isinstance(r.timestamp, datetime) else str(r.timestamp)[:19]
    print(f"{r.id[:15]:<15} | {ts_str:<22} | {r.intent:<20} | {r.disposition:<12} | {r.duration:<10.1f}s")

print("="*95)
total_count = session.query(CallRecord).count()
print(f" Total records stored in database: {total_count}")
print("="*95 + "\n")

session.close()
