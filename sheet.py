from __future__ import print_function
from googleapiclient.discovery import build
from google.oauth2 import service_account
from config import *

SERVICE_ACCOUNT_FILE = 'keys.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

SAMPLE_SPREADSHEET_ID = getSheet()
service = build('sheets', 'v4', credentials=creds)

def easy(name):
    # The ID and range of a sample spreadsheet.
    SAMPLE_RANGE_NAME = name
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    final =[]
    for i in range(1,len(values)):
        name = values[i][0]
        disc_name = values[i][1]
        for j in range(2,len(values[i])):
            if values[i][j] == '' or values[i][j] == ' ':
                continue
            else:
                final.append([name, disc_name, values[0][j], values[i][j]])
    return final

def clear(name):
    SAMPLE_RANGE_NAME = name
    sheet = service.spreadsheets()
    res = sheet.values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
    print(res)
