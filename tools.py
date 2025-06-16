from fastapi import APIRouter, Request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime

router = APIRouter()

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = os.getenv("GOOGLE_CREDS_JSON")
credentials = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), scope)
gc = gspread.authorize(credentials)

# ✅ Updated /log_call_result route
@router.post("/tools/log_call_result")
async def log_call_result(request: Request):
    try:
        # Log raw request body
        raw = await request.body()
        print("RAW BODY >>>", raw)

        # Try parsing as JSON directly
        try:
            data = await request.json()
        except Exception:
            print("Failed standard JSON parse. Trying manual decode...")
            data = json.loads(raw.decode())

        # Log parsed data
        print("PARSED DATA >>>", data)

        # Open the right sheet/tab
        results_sheet = gc.open("Aflac_Call_Results").worksheet("Results")

        # Append the call result row
        new_row = [
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            data.get("lead_name", ""),
            data.get("company", ""),
            data.get("phone", ""),
            data.get("email", ""),
            data.get("role", ""),
            data.get("employee_count", ""),
            data.get("outcome", ""),
            data.get("appointment_time", ""),
            data.get("follow_up_time", ""),
            data.get("objections", ""),
            data.get("transcript_url", ""),
            data.get("agent_responses", "")
        ]

        results_sheet.append_row(new_row)

        return {"status": "success", "message": "Call result logged."}

    except Exception as e:
        print("ERROR >>>", str(e))
        return {"status": "error", "message": str(e)}
