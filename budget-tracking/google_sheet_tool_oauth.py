import os
import sys
import warnings
warnings.filterwarnings('ignore')
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

import pandas as pd
import gspread
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load the variables from the .env file
load_dotenv()

# Configuration
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
FOLDER_ID = os.getenv('DRIVE_FOLDER_ID')
TEMPLATE_ID = os.getenv('BUDGET_TEMPLATE_ID')

def get_user_creds():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0, prompt='consent')
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def prepare_data_for_sheets(csv_path):
    """Cleans data for Google Sheets dropdown and formula compatibility."""
    df = pd.read_csv(csv_path)
    if df.empty:
        return []
    
    # Clean column names
    df.columns = [c.strip() for c in df.columns]
    
    # The order in both CSV and Sheets is: [Date, Amount, Description, Category]
    # We ensure we have these columns in this order.
    cols = ['Date', 'Amount', 'Description', 'Category']
    if all(col in df.columns for col in cols):
        df = df[cols]
    
    # 1. Date (Index 0)
    df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.strip()
    
    # 2. Amount (Index 1) - Crucial for SUMIFS formulas
    df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1], errors='coerce').fillna(0)
    
    # 3. Description (Index 2)
    df.iloc[:, 2] = df.iloc[:, 2].astype(str).str.strip()
    
    # 4. Category (Index 3) - Preserve the authoritative category wording.
    # Categories must match expense_categories.md or income_categories.md exactly.
    df.iloc[:, 3] = df.iloc[:, 3].astype(str).str.strip()
    
    return df.values.tolist()

def run_sync(expense_path, income_path, year, month):
    try:
        creds = get_user_creds()
        drive_service = build('drive', 'v3', credentials=creds)
        gc = gspread.authorize(creds)

        # 1. Set the Name: "YYYY-MM Monthly Budget"
        formatted_month = str(month).zfill(2)
        new_name = f"{year}-{formatted_month} Monthly Budget"
        
        # 2. Clone the Template into the target folder
        file_metadata = {'name': new_name, 'parents': [FOLDER_ID]}
        new_file = drive_service.files().copy(fileId=TEMPLATE_ID, body=file_metadata).execute()
        new_id = new_file.get('id')
        
        spreadsheet = gc.open_by_key(new_id)
        sheet = spreadsheet.worksheet("Transactions")

        # 3. Prepare and Write Data using USER_ENTERED mode
        # This mode triggers the dropdown validation and spreadsheet formulas.
        expense_data = prepare_data_for_sheets(expense_path)
        income_data = prepare_data_for_sheets(income_path)

        if expense_data:
            sheet.update(
                range_name=f'B5:F{4+len(expense_data)}', 
                values=expense_data,
                value_input_option='USER_ENTERED' 
            )

        if income_data:
            sheet.update(
                range_name=f'G5:K{4+len(income_data)}', 
                values=income_data,
                value_input_option='USER_ENTERED'
            )

        print(f"SUCCESS: Created '{new_name}'")
        print(f"URL: https://docs.google.com/spreadsheets/d/{new_id}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python google_sheets_tool.py expense.csv income.csv YYYY MM")
    else:
        run_sync(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
