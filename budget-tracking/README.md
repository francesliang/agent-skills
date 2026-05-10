# Budget Tracking Sync Tool

This tool automates the process of creating monthly budget spreadsheets by cloning [a master template](https://docs.google.com/spreadsheets/d/1eqQVAQzCJsMct4t0VHfwwZisfZeqIFD8V8MWpCkO1CU/edit?usp=sharing) and syncing transaction data from local files (e.g. CSV and PDF). It includes data cleaning logic to ensure compatibility with Google Sheets dropdowns and formulas.

## Use with Agent 

This tool is specifically designed to work with AI agents (e.g., Gemini CLI) by following the logic defined in `SKILL.md`. The agent automates the entire financial update workflow:

1.  **Clone Monthly Budget Sheet**: It automatically copies the master Google Sheet template into your target Drive folder for the specific year and month.
2.  **Extract Data**: Reads transaction data from both **CSV and PDF** bank statements.
3.  **Automatic Categorization**: Classifies and categorizes all transactions based on descriptions and your predefined rules in `SKILL.md`.
4.  **Data Sanitization & Sync**: 
    - Normalizes categories to **Title Case** and cleans currency strings to ensure spreadsheet formulas (like `SUMIFS`) work correctly.
    - Updates the new sheet using `USER_ENTERED` mode to trigger all native Google Sheet validations and formatting.
5.  **Secure Authentication**: Uses OAuth 2.0 to securely access your personal Google Drive and Sheets quota.

### Usage with Gemini CLI

You can execute the full automation flow by providing the folder containing your transaction files:

```plaintext
Can you read the PDFs and CSV files in "<path to folder with transaction files>" and follow the instructions in "agent-skills/budget-tracking/SKILL.md".
```

## Prerequisites

1.  **Google Cloud Project**:
    - Enable the **Google Drive API** and **Google Sheets API**.
    - Configure an **OAuth Consent Screen**.
    - Create **OAuth 2.0 Client IDs** (Desktop application).
    - Download the client secret JSON file and save it as `client_secret.json` in the project root.


## Configuration

Create a `.env` file in the root directory and provide your specific Google Drive IDs:

```env
DRIVE_FOLDER_ID=your_target_folder_id
BUDGET_TEMPLATE_ID=your_template_spreadsheet_id
```