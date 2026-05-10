# Skill: Sync Monthly Budget (User Auth Mode)

## Goal
Clone the "Template - Monthly budget" and populate the side-by-side "Transactions" sheet using the user's personal Drive quota, ensuring that categories register with dropdowns and totals aggregate in the Summary sheet.

## Context
- **Target Folder:** Managed via `.env` (DRIVE_FOLDER_ID)
- **Template ID:** Managed via `.env` (BUDGET_TEMPLATE_ID)
- **Column Mapping:** 
    *   **Expenses:** Range `B5:E` (Date, Amount, Description, Category)
    *   **Income:** Range `G5:J` (Date, Amount, Description, Category)

## Instructions
1. **Identify Date:** Scan the transaction data (typically the `expense.csv`) to determine the target **Year (YYYY)** and **Month (MM)**.
2. **Auth & Prepare:** Ensure `client_secret.json` is present. The tool will use `token.json` or prompt for a browser login on the first run.
3. **Execute Sync:** Call the Python tool with the following four arguments:
   ```bash
   python google_sheets_tool.py [expense_csv] [income_csv] [YYYY] [MM]