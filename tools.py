from fastapi import APIRouter
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

router = APIRouter()

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = os.getenv("GOOGLE_CREDS_JSON")

if not creds_json:
    raise RuntimeError("GOOGLE_CREDS_JSON environment variable is not set")

credentials = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), scope)
gc = gspread.authorize(credentials)

# Open spreadsheet and worksheet
sheet = gc.open("Aflac_Leads").worksheet("Leads")  # Sheet name and tab name must match exactly

@router.get("/tools/get_next_lead")
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
