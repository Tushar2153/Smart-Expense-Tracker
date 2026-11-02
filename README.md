# Smart Expense Tracker — Synthetic Starter Data

All data in this package is synthetic and generated for development/education. It is NOT real bank data and must not be used to claim real-world model performance.

## Files
- `transactions_synthetic.csv`: transaction records with dates, descriptions, merchant, amount, direction, category, account and synthetic anomaly flag.
- `categorization_training.csv`: text/category pairs for training a first classifier.
- `daily_cashflow_synthetic.csv`: daily income, expenses, net cash flow and closing balance for forecasting experiments.
- `receipt_fields_synthetic.csv`: structured receipt field examples (ground truth only; this file does NOT contain receipt images).
- `budgets_example.csv`: example category budgets.

## Important limitations
1. Transaction descriptions and labels are generated from templates. A classifier can learn template patterns and appear more accurate than it would on real bank statements.
2. `is_synthetic_anomaly` marks injected high-value outliers and duplicated records. It is a teaching label, not a fraud label.
3. The daily cashflow data is artificial and its balance is not linked to the transaction CSV.
4. Receipt examples are tabular ground truth, not OCR training images.
5. For credible evaluation, split by time or hold out unseen templates/merchants, and test on appropriately anonymized real records only with permission.

## Suggested first experiment
Train a text classifier on `categorization_training.csv`, report macro-F1 and per-class precision/recall, and inspect a confusion matrix. Then build rules for exact duplicate detection before trying Isolation Forest.
