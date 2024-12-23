import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

service_account_info = json.loads(os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'))
# The ID of your Google Sheet
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Set up the credentials using the JSON from environment variable
credentials = Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

def save_to_google_sheet(user_query, response):
    """
    Save the user_query and response to the Google Sheet.
    """
    try:
        # Prepare the data to save in the sheet
        values = [[user_query, response]]

        # Body for the Sheets API request
        body = {
            'values': values
        }

        # Append the data to the Google Sheet
        sheet = service.spreadsheets()
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range='PaperQueryAI!A1',  # Adjust the range based on where you want to append the data
            valueInputOption='RAW',
            body=body
        ).execute()

        print('Data saved successfully:', result)
    except Exception as e:
        print('Error saving data to Google Sheets:', e)


