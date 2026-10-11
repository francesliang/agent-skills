---
name: ato-tax-return
description: Prepare Australian individual income-tax working papers by extracting rental-property expenses, ETF distributions, payslip leave hours, loan interest, and loan package fees from PDFs, CSVs, and spreadsheets. Use when processing end-of-financial-year documents or producing CSV summaries for an Australian tax return. Do not use it to lodge a return or make unsupported tax-deductibility decisions.
---

# ATO Tax Return

Process documents for an Australian financial year and produce concise CSV summaries using only the fields defined below.

## Guardrails

- Treat the outputs as working papers, not tax or financial advice.
- Do not lodge, amend, or submit a tax return.
- Do not modify, rename, move, or delete source documents unless the user explicitly requests it.
- Do not invent unreadable or missing values. Ask the user about material ambiguities.
- Do not count duplicate documents or transactions twice.
- Verify tax-sensitive treatment against current official ATO guidance.

## Locate the records

1. Use the tax-return root supplied by the user. If none is supplied, ask for it.
2. Determine the financial year from the request or directory name. Interpret `YYYY-YYYY` as 1 July of the first year through 30 June of the second year, inclusive.
3. Use this category structure:

```text
Rental Property/
├── Council Rates/
├── Water and Sewerage/
└── Body Corp/
ETF/
Payslip/
Debt recycling/
```

4. Recursively inspect supported PDFs, CSVs, and spreadsheets within those categories.
5. Create an `Output` directory under the tax-return root. Ignore that directory during later runs.

## General processing rules

1. Extract text directly where possible. Use OCR when a PDF has no usable text layer.
2. Include only records relevant to the target financial year.
3. Preserve complete source values. Do not silently apportion a charge spanning financial years.
4. Write valid UTF-8 CSV files with exactly the specified headers and no additional fields.
5. Write monetary amounts as decimal numbers without currency symbols or thousands separators.
6. Preserve debit signs as shown in transaction files unless an instruction below requires a calculated value.
7. If a required value is absent, leave it blank rather than adding explanatory columns.
8. Report skipped, unreadable, duplicate, or ambiguous records to the user in the final response rather than adding them to the CSV files.

## Rental Property

### Council Rates, Water and Sewerage, and Body Corp

Inspect all invoices, notices, receipts, and statements in each subfolder. Create one CSV per subfolder in `Output`:

- `council-rates.csv`
- `water-and-sewerage.csv`
- `body-corp.csv`

Use exactly these fields:

```text
Period,Paid Amount
```

Apply these rules:

- Use one row for each distinct charge or levy.
- Use the billing or levy period printed on the source document.
- Populate `Paid Amount` from the explicit paid amount when available.
- Treat an explicit `Amount Payable`, `Nett Amount Payable`, `Total Due`, `Current Charges`, or equivalent billed amount as interchangeable with `Paid Amount` for this output.
- If both a paid amount and a payable amount appear for the same charge, prefer the paid amount.
- Exclude optional donations and unrelated carried-forward account balances.
- Do not automatically treat a body-corporate special levy or capital charge as an immediately deductible expense; tell the user when one needs review.

### Rental property loan interest and package fees

Inspect rental-property home-loan transaction files when present. Extract only transactions whose details identify `Interest Charged` or `Package fee`. Write `Output/rental-property-interest.csv` using exactly these fields:

```text
Transaction Date,Account,Details,Debit
```

- Preserve the values as represented in the source transaction file.
- Exclude repayments, transfers, principal, other fees, and other transaction types.
- Do not assume that a package fee is fully deductible. Tell the user when it may cover multiple loans or accounts, or relate partly to private or mixed-purpose borrowing.
- Tell the user when the records indicate private use, refinancing, redraws, or mixed-purpose borrowing.

## ETF

Discover the immediate subfolders under `ETF` at runtime. Process only the foreign ETF subfolders whose distribution records contain corresponding AUD and USD payment values and a USD tax amount. Skip every other ETF subfolder. Do not hard-code or enumerate fund names in this skill.

Create one CSV per processed ETF in `Output`, named `<ETF>.csv`, using exactly these fields:

```text
Date,Payment (AUD),Payment (USD),Tax (USD),Tax (AUD)
```

Apply these rules:

- Extract each field directly from the source when it is present.
- Leave fields blank when the source does not provide enough information.
- Calculate `Tax (AUD)` only when the source provides corresponding non-zero `Payment (AUD)`, `Payment (USD)`, and `Tax (USD)` values for the same payment.
- Use this formula: `Tax (AUD) = Tax (USD) * (Payment (AUD) / Payment (USD))`.
- Do not divide by zero or combine values from different payments.
- Do not create a CSV for a skipped ETF subfolder.
- Tell the user when a selected foreign ETF's records do not provide the values needed for the calculation.

## Payslip

Inspect all payslips and select those that explicitly record leave hours or quantities. Write `Output/payslip-leave.csv` using exactly these fields:

```text
Period,Leave hours
```

- Use the payslip period printed on the document.
- Extract leave taken, not leave balances, accruals, opening balances, or closing balances.
- Add together multiple leave entries within the same payslip period only when they all represent leave taken in hours.
- Do not infer hours from dollar amounts unless the user explicitly requests it.

## Debt recycling

Inspect each transaction CSV or statement under `Debt recycling`. Extract only transactions whose details identify `Interest Charged`. Write `Output/debt-recycling-interest.csv` using exactly these fields:

```text
Transaction Date,Account,Details,Debit
```

- Preserve the values as represented in the source transaction file.
- Exclude repayments, transfers, fees, principal, and other transaction types.
- Do not infer investment purpose from the folder name alone.
- Tell the user when the records show redraws, private transactions, mixed-purpose borrowing, refinancing, or another issue that may affect deductibility.

## Finish the task

Before finishing:

1. Confirm that each source file was processed or identify it as skipped, unreadable, duplicate, ambiguous, or outside the financial year.
2. Confirm that every CSV uses exactly its specified headers and contains no extra fields.
3. Confirm that calculated `Tax (AUD)` values use the stated formula and inputs from the same payment.
4. Report the paths of all generated CSV files and summarize any records that need user or tax-agent review.
