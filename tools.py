from fastapi import APIRouter
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

router = APIRouter()

# Load credentials from environment variable
GOOGLE_CREDS_JSON = os.environ.get("GOOGLE_CREDS_JSON")
if not GOOGLE_CREDS_JSON:
    raise RuntimeError("GOOGLE_CREDS_JSON environment variable is not set")

creds_dict = json.loads(GOOGLE_CREDS_JSON)

# Setup gspread client
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(credentials)

# Open the sheet and get the "Leads" worksheet or fallback
spreadsheet = gc.open("Aflac_Leads")
try:
    worksheet = spreadsheet.worksheet("Leads")
except gspread.exceptions.WorksheetNotFound:
    print("[!] 'Leads' worksheet not found. Available worksheets are:")
    print([ws.title for ws in spreadsheet.worksheets()])
    worksheet = spreadsheet.get_worksheet(0)  # fallback to first sheet
    print(f"[✓] Falling back to: {worksheet.title}")

@router.get("/leads")
def get_leads():
    data = worksheet.get_all_records()
    return {"leads": data}
