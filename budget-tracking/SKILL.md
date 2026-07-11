
---
name: budget-tracking
description: Process bank statements and transaction files (PDFs and CSVs) to extract, categorize, and organize expenses and income. Use when the user uploads transaction files, mentions budget tracking, expense categorization, or asks to update their budget spreadsheet. Automatically categorizes transactions into expense and income categories based on merchant names and descriptions.
---

# Budget Tracking

Automatically process transaction files (PDFs and CSVs), extract transactions, categorize them as income or expenses, and update a Google Sheet with the categorized data.

## When to Use This Skill

- User uploads bank statements, credit card statements, or transaction files (PDF or CSV)
- User asks to categorize expenses or income
- User mentions budget tracking or financial organization
- User asks to update their budget spreadsheet with a link provided


## Processing Instructions

### Step 1: Extract Transactions

When user uploads files:

1. **Identify file types** (PDF or CSV)
2. **Extract transaction data into standard csv format**: with column fields 'Date, Amount, Description, Category'
3. **Extract all transactions** do not skip any.

### Step 2: Classify Income vs Expense

1. Based on description
2. Assign type: "Income" or "Expense"
3. If not sure, assign type "Other"

### Step 3: Categorize Transactions

1. Before categorising transactions, read [expense_categories.md](expense_categories.md) and [income_categories.md](income_categories.md) and treat their list entries as the authoritative allowed values.
2. For transactions with `Expense` type, assign exactly one category copied verbatim from [expense_categories.md](expense_categories.md).
3. For transactions with `Income` type, assign exactly one category copied verbatim from [income_categories.md](income_categories.md).
4. Category values must match the relevant list entry exactly, including capitalization, spaces, punctuation, and singular/plural wording. Do not rename, normalize, title-case, abbreviate, or invent categories such as `Other Expenses` or `Other Income` unless that exact wording appears in the relevant category file.
5. Perform the categorisation based on the transaction description. If uncertain, use the closest applicable category from the relevant category file. For income, use `Other` as the fallback while that exact entry remains in [income_categories.md](income_categories.md). The expense category list currently has no generic fallback, so choose the closest listed expense category rather than creating a new value.
6. Preserve the exact category wording when writing CSV files and when syncing values to Google Sheets.
7. **Special Categorization & Transfer Rules**:
   - Transfers/notes containing **"fun expense"** or **"weekly fun expense"** must be classified as **`Expense`** under the **`Weekly household`** category.
   - Transfers/notes containing **"joint expense"** or **"weekly joint expense"** must be classified as **`Expense`** under the **`Weekly household`** category.
   - Offset transfers/notes containing **"mortgage repayment"** or **"home loan repayment"** must be classified as **`Expense`** under the **`Mortgage`** category.
   - Credit card payments (transfers from checking/savings to a credit card account) should be classified as **`Other`** (ignored/excluded) to prevent double counting of individual credit card transactions.

### Step 4: Write the results into a CSV file

1. Write results to a CSV file, in the same folder as the uploaded files, with the following columns:
'Date, Amount, Description, Category'
2. Write expense transactions into the csv file "expense.csv" 
3. Write income transcations into the csv file "income.csv"

### Step 5: Update Google Sheet

Update google sheet following the instruction in [sync_budget.md](sync_budget.md).
