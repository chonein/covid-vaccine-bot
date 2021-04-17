import json
from typing import Any
from googleapiclient.discovery import build
from google.oauth2 import service_account
import create_config_json as cfig_creator


sheet: Any = None


try:
    with open('config.json', 'r') as cfig:
        cfig_dict = json.loads(cfig.read())
        SERVICE_ACCOUNT_FILE = cfig_dict['SERVICE_ACCOUNT_FILE']
        # Spread Sheet Id
        ss_ID = cfig_dict['ss_ID']
except FileNotFoundError:
    cfig_creator.main()
    with open('config.json', 'r') as cfig:
        cfig_dict = json.loads(cfig.read())
        SERVICE_ACCOUNT_FILE = cfig_dict['SERVICE_ACCOUNT_FILE']
        # Spread Sheet Id
        ss_ID = cfig_dict['ss_ID']


def setup() -> None:
    global sheet
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()


def get_spreadsheet_rows() -> dict:
    result = sheet.values().get(spreadsheetId=ss_ID,
                                range="Form Responses 1!A1:I1000000").execute()
    # print('\n\n' + str(result) + '\n\n')
    return result['values'][1:]


setup()
