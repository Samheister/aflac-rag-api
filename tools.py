from fastapi import APIRouter
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

router = APIRouter()

# Google Sheets setup from Railway environment variable
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds_json = os.environ.get("GOOGLE_CREDS_JSON")
if not creds_json:
    raise RuntimeError("GOOGLE_CREDS_JSON environment variable is not set")

credentials = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), scope)
gc = gspread.authorize(credentials)

# Open the spreadsheet and worksheet
sheet = gc.open("Aflac_Leads").worksheet("Leads")  # Ensure this matches your sheet name and tab

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
