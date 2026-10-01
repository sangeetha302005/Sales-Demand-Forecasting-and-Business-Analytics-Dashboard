# Data Directory

This directory contains the sales dataset used by the application.

## Sample Dataset

- `sample_sales_data.csv` — A synthetic sales dataset with ~6000 records spanning 2022–2025.

## Expected Columns

| Column | Type | Description |
|--------|------|-------------|
| Date | date | Transaction date |
| Product | string | Product name |
| Category | string | Product category |
| Region | string | Sales region |
| Sales_Representative | string | Name of sales representative |
| Quantity | integer | Units sold |
| Unit_Price | float | Price per unit |
| Revenue | float | Total revenue (Quantity × Unit_Price) |
| Cost | float | Total cost |
| Profit | float | Profit (Revenue − Cost) |

## Using Your Own Data

Replace `sample_sales_data.csv` with your own CSV file, or upload it through the dashboard.
The application will adapt to your column names where possible.
