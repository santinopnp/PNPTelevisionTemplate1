import os
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet(sheet_name):
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(creds_json),
        ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(credentials)
    return client.open(sheet_name).sheet1
