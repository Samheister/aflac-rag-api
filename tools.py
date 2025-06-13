from fastapi import APIRouter
import gspread
from oauth2client.service_account import ServiceAccountCredentials

router = APIRouter()

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("your_credentials.json", scope)
gc = gspread.authorize(credentials)

# Open the spreadsheet and worksheet
sheet = gc.open("Aflac_Leads").worksheet("Leads")  # Adjust if different

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
