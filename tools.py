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

if not creds_json:
    raise RuntimeError("GOOGLE_CREDS_JSON environment variable is not set")

credentials = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), scope)
gc = gspread.authorize(credentials)

# Open spreadsheet and worksheet for leads
sheet = gc.open("Aflac_Leads").worksheet("Leads")  # Source sheet for leads

@router.get("/get_next_lead")
def get_next_lead():
    leads = sheet.get_all_records()
    for lead in leads:
        if lead.get("Status", "").strip().lower() == "not contacted":
            return {
                "name": lead.get("Name", ""),
                "company": lead.get("Company", ""),
                "phone": lead.get("Phone", ""),
                "email": lead.get("Email", ""),
                "role": lead.get("Role", ""),
                "employee_count": lead.get("EmployeeCount", "")
            }
    return {"message": "No more uncontacted leads"}


# ✅ NEW: Log call results to Aflac_Call_Results
@router.post("/log_call_result")
async def log_call_result(request: Request):
    data = await request.json()

    # Open the results worksheet
    results_sheet = gc.open("Aflac_Call_Results").worksheet("Results")

    # Prepare values in exact order
    new_row = [
        datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
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
        data.get("transcript_url", ""),  # This is the full transcript link
        data.get("agent_responses", "")
    ]

    results_sheet.append_row(new_row)
    return {"status": "success", "message": "Call result logged."}
