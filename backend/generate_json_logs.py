import json
import os
from datetime import datetime, timedelta

def create_log(call_id, start_time, duration_sec, events, routing):
    end_time = start_time + timedelta(seconds=duration_sec)
    return {
        "call_id": call_id,
        "start_time": start_time.isoformat() + "Z",
        "end_time": end_time.isoformat() + "Z",
        "caller_id": "+1555" + str(hash(call_id))[-7:],
        "events": events,
        "routing": routing
    }

mock_s3_path = "mock_s3"
os.makedirs(mock_s3_path, exist_ok=True)

base_time = datetime(2023, 10, 4, 9, 0, 0)

logs = [
    # Call 1: Lost Card (Transferred to agent)
    create_log(
        "B-4001", base_time, 120,
        [
            {"timestamp": (base_time + timedelta(seconds=2)).isoformat() + "Z", "speaker": "BOT", "text": "Welcome to Global Bank. How can I help you today?"},
            {"timestamp": (base_time + timedelta(seconds=10)).isoformat() + "Z", "speaker": "USER", "text": "I lost my credit card at the bar last night, I need to freeze it immediately."},
            {"timestamp": (base_time + timedelta(seconds=14)).isoformat() + "Z", "speaker": "BOT", "text": "I understand you want to report a lost or stolen card. Let me transfer you to our fraud and security team to secure your account immediately."},
        ],
        {"final_disposition": "transferred", "transferred_to_agent": True, "agent_queue": "fraud_security"}
    ),
    
    # Call 2: Transfer Funds (Resolved)
    create_log(
        "B-4002", base_time + timedelta(minutes=15), 65,
        [
            {"timestamp": (base_time + timedelta(minutes=15, seconds=2)).isoformat() + "Z", "speaker": "BOT", "text": "Welcome to Global Bank. How can I help you today?"},
            {"timestamp": (base_time + timedelta(minutes=15, seconds=8)).isoformat() + "Z", "speaker": "USER", "text": "I want to move 500 dollars from savings to checking."},
            {"timestamp": (base_time + timedelta(minutes=15, seconds=12)).isoformat() + "Z", "speaker": "BOT", "text": "To transfer funds, please say or enter your 4-digit PIN."},
            {"timestamp": (base_time + timedelta(minutes=15, seconds=18)).isoformat() + "Z", "speaker": "USER", "text": "[DTMF_INPUT_HIDDEN]"},
            {"timestamp": (base_time + timedelta(minutes=15, seconds=22)).isoformat() + "Z", "speaker": "BOT", "text": "Got it. I will transfer $500.00 from your Savings to your Checking account. Is that correct?"},
            {"timestamp": (base_time + timedelta(minutes=15, seconds=26)).isoformat() + "Z", "speaker": "USER", "text": "Yes."},
            {"timestamp": (base_time + timedelta(minutes=15, seconds=30)).isoformat() + "Z", "speaker": "BOT", "text": "The transfer is complete. Your new checking balance is $2,400. Anything else?"},
            {"timestamp": (base_time + timedelta(minutes=15, seconds=34)).isoformat() + "Z", "speaker": "USER", "text": "Nope, thanks."}
        ],
        {"final_disposition": "hangup_by_user", "transferred_to_agent": False}
    ),
    
    # Call 3: High Fallback / Abandoned
    create_log(
        "B-4003", base_time + timedelta(minutes=30), 45,
        [
            {"timestamp": (base_time + timedelta(minutes=30, seconds=2)).isoformat() + "Z", "speaker": "BOT", "text": "Welcome to Global Bank. How can I help you today?"},
            {"timestamp": (base_time + timedelta(minutes=30, seconds=10)).isoformat() + "Z", "speaker": "USER", "text": "Yeah I got this weird letter about my mortgage escrow account being short."},
            {"timestamp": (base_time + timedelta(minutes=30, seconds=14)).isoformat() + "Z", "speaker": "BOT", "text": "I'm sorry, I didn't quite get that. You can say things like 'check my balance', 'transfer funds', or 'report a lost card'."},
            {"timestamp": (base_time + timedelta(minutes=30, seconds=22)).isoformat() + "Z", "speaker": "USER", "text": "Mortgage. Escrow. Shortage."},
            {"timestamp": (base_time + timedelta(minutes=30, seconds=26)).isoformat() + "Z", "speaker": "BOT", "text": "I'm still having trouble understanding. Would you like to speak to a representative?"},
            {"timestamp": (base_time + timedelta(minutes=30, seconds=30)).isoformat() + "Z", "speaker": "USER", "text": "Ugh, nevermind. I'll just go to the branch."}
        ],
        {"final_disposition": "hangup_by_user", "transferred_to_agent": False}
    )
]

for log in logs:
    filename = f"{mock_s3_path}/call_{log['call_id']}.json"
    with open(filename, "w") as f:
        json.dump(log, f, indent=2)
    print(f"Generated {filename}")
