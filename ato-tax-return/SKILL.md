
---
name: ato-tax-return
description: Assist tax return at the end of a financial year.
---

# ATO Tax Return

## When to Use This Skill


## Processing categories

The tax return processing includes the following categories:
- Rental Property
   - Council Rates
   - Water and Sewerage
   - Body Corp
- ETF
- Payslip
- Debt recycling

## Processing Instructions

### Rental Property

1. Inspect all the invoices in each folder category under the "Rental Property" folder
2. For each folder, output the following to a csv file: 'Period', 'Paid Amount'
3. For the home loan transactions, extract only the "Interest Charged" items, and output the following to a csv file: 'Transaction Date', 'Account', 'Details', 'Debit'.

### ETF

1. Inspect the folders and files in each folder under "ETF/VTS" and "ETF/VEU"
2. For the files under each folder, output the following to a csv:
- Extract the following:
   - 'Date'
   - 'Payment (AUD)'
   - 'Payment (USD)'
   - 'Tax (USD)'
- Add a new column 'Tax (AUD)', can calculate the amount using the formula: 'Tax (AUD)' = 'Tax (USD)' x ('Payment (AUD)' / 'Payment (USD)')


### Payslip

1. Inspect all the payslips in the folder, identify the ones that have "Leave" hours / quantity
2. For those that records the hours of "Leave", output the following to a csv file: 'Period', 'Leave hours'


### Debt recycling

1. Inspect each transation csv file, extract only the "Interest Charged" items, and output the following to a csv file: 'Transaction Date', 'Account', 'Details', 'Debit'

