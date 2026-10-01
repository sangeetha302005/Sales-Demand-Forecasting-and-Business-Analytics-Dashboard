# 📊 Sales Demand Forecasting & Business Analytics Dashboard

> A comprehensive data science project for analyzing historical sales data, generating business insights, forecasting future demand, and presenting everything in an interactive Streamlit dashboard.

🔗 **GitHub Repository:** [https://github.com/sangeetha302005/Sales-Demand-Forecasting-and-Business-Analytics-Dashboard](https://github.com/sangeetha302005/Sales-Demand-Forecasting-and-Business-Analytics-Dashboard)

🌐 **Live Demo:** [https://sales-demand-forecasting-dashboard.streamlit.app](https://sales-demand-forecasting-dashboard.streamlit.app)

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sales-demand-forecasting-dashboard.streamlit.app)

### 📂 Upload Your Own Data!
This dashboard supports **CSV and Excel file uploads**. You can upload your own sales dataset directly through the sidebar — the app will automatically detect columns, clean the data, and generate all charts, forecasts, and insights for your data.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Features](#features)
- [Architecture](#architecture)
- [Dataset](#dataset)
- [Data Preprocessing](#data-preprocessing)
- [Exploratory Data Analysis](#exploratory-data-analysis)
- [Forecasting Methodology](#forecasting-methodology)
- [Evaluation Metrics](#evaluation-metrics)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [How to Use Your Own Dataset](#how-to-use-your-own-dataset)
- [Results](#results)
- [Future Enhancements](#future-enhancements)
- [Author](#author)

---

## 🔍 Project Overview

This project demonstrates a complete end-to-end data science workflow — from raw data ingestion and cleaning through exploratory analysis, statistical forecasting, and interactive visualization. It is designed as a professional yet beginner-friendly final-year project for B.E. Computer Science / Data Science students.

The application ingests historical sales data, automatically cleans and preprocesses it, generates actionable business insights, and forecasts future demand using statistical models — all presented through an interactive Streamlit dashboard.

## 🎯 Problem Statement

Businesses need to understand their sales patterns and forecast future demand to make informed decisions about inventory, staffing, marketing, and resource allocation. Manual analysis of large sales datasets is time-consuming, error-prone, and often lacks the depth needed for strategic planning.

This project automates the analysis process, providing instant insights and reliable demand forecasts from historical sales data.

## 🏆 Objectives

1. **Data Ingestion** — Support CSV and Excel file uploads with automatic structure detection.
2. **Data Cleaning** — Automatically handle missing values, duplicates, type conversions, and derived calculations.
3. **Exploratory Analysis** — Generate interactive visualizations across multiple dimensions (time, product, region, category).
4. **Demand Forecasting** — Implement and compare baseline (Moving Average) and statistical (Exponential Smoothing) forecasting models.
5. **Business Insights** — Automatically extract actionable insights from the data.
6. **Interactive Dashboard** — Present all findings in a professional, filterable Streamlit dashboard.

## ✨ Features

### Data Management
- CSV and Excel file upload support
- Automatic column identification from various naming conventions
- Comprehensive data quality report (missing values, duplicates, data types)
- Automatic data cleaning with detailed operation log

### Dashboard Pages
1. **Executive Overview** — KPI cards, revenue/profit trends, regional breakdown
2. **Sales Analysis** — Daily, monthly, yearly trends with category performance
3. **Product Analysis** — Top/bottom products, product deep-dive with history
4. **Regional Analysis** — Revenue, profit, and quantity by region with ranking table
5. **Sales Rep Analysis** — Performance comparison (shown when data is available)
6. **Demand Forecasting** — Historical trends, model predictions, future forecasts with confidence intervals
7. **Model Evaluation** — MAE, RMSE, MAPE comparison with explanations
8. **Business Insights** — Auto-generated insights with supporting data

### Interactive Filters
- Date range picker
- Category selector
- Region selector
- Product selector
- Sales Representative selector

## 🏗️ Architecture

```
User → Streamlit Dashboard (app.py)
              │
              ├── Data Loading & Cleaning (src/data_cleaning.py)
              ├── EDA & Visualization (src/eda.py)
              ├── Forecasting Engine (src/forecasting.py)
              └── Insights Generator (src/business_insights.py)
```

The application follows a modular architecture with separate source modules for each concern, making the code maintainable, testable, and extensible.

## 📊 Dataset

### Sample Dataset
A synthetic sales dataset (`data/sample_sales_data.csv`) is included with ~6,000 records spanning January 2022 to September 2025.

### Fields

| Column | Type | Description |
|--------|------|-------------|
| Date | date | Transaction date |
| Product | string | Product name (25 unique products) |
| Category | string | Product category (Electronics, Furniture, Office Supplies, Accessories) |
| Region | string | Sales region (North, South, East, West, Central) |
| Sales_Representative | string | Sales representative name |
| Quantity | integer | Units sold |
| Unit_Price | float | Price per unit |
| Revenue | float | Quantity × Unit_Price |
| Cost | float | Total cost of goods |
| Profit | float | Revenue − Cost |

The dataset includes realistic seasonality (higher Q4 sales), year-over-year growth trends, and realistic price/cost relationships.

## 🧹 Data Preprocessing

- **Duplicate Removal** — Exact duplicate rows are removed
- **Date Conversion** — Date columns are parsed and invalid dates are handled
- **Numeric Conversion** — Numeric columns are coerced with fallback handling
- **Missing Value Imputation** — Quantities default to 1; numeric fields use median; categoricals use "Unknown"
- **Derived Columns** — Revenue and Profit are calculated when missing; Year, Month, Quarter, Day_of_Week are added
- **Invalid Value Detection** — Negative quantities are removed
- **Cleaning Log** — All operations are recorded and displayed to the user

## 📈 Exploratory Data Analysis

- Monthly and daily revenue/profit trends
- Year-over-year comparisons
- Category-wise performance analysis
- Top/bottom product rankings
- Regional performance breakdown
- Sales representative comparison
- Interactive product deep-dives

All charts are built with Plotly for full interactivity (zoom, pan, hover, export).

## 🔮 Forecasting Methodology

### Baseline Model — Moving Average
A simple 3-period moving average serves as the baseline for comparison.

### Statistical Model — Exponential Smoothing (Holt-Winters)
- **With Seasonality**: Applied when sufficient data exists (≥2 seasonal cycles)
- **Without Seasonality**: Holt's linear trend when seasonal data is insufficient
- **Fallback**: Simple Exponential Smoothing when other models fail

### Pipeline
1. Aggregate data to chosen frequency (daily/monthly)
2. Chronological 80/20 train-test split (no data leakage)
3. Fit baseline and statistical models on training data
4. Evaluate on held-out test set
5. Refit on full data for future predictions
6. Generate forecasts with 95% confidence intervals

## 📏 Evaluation Metrics

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| **MAE** | Mean Absolute Error | Average absolute prediction error (in revenue units) |
| **RMSE** | Root Mean Squared Error | Like MAE but penalizes large errors more |
| **MAPE** | Mean Absolute Percentage Error | Percentage error (< 10% excellent, 10-20% good) |

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|--------|
| Python 3.9+ | Core programming language |
| Pandas | Data manipulation and analysis |
| NumPy | Numerical computations |
| Plotly | Interactive visualizations |
| Streamlit | Web dashboard framework |
| Scikit-learn | Machine learning utilities |
| Statsmodels | Statistical forecasting models |
| OpenPyXL | Excel file support |

## 📁 Project Structure

```
sales-demand-forecasting/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore rules
│
├── data/
│   ├── sample_sales_data.csv   # Sample sales dataset (~6000 records)
│   └── README.md               # Dataset documentation
│
├── src/
│   ├── __init__.py             # Package initializer
│   ├── data_cleaning.py        # Data loading, cleaning, preprocessing
│   ├── eda.py                  # EDA and visualization functions
│   ├── forecasting.py          # Forecasting models and pipeline
│   └── business_insights.py    # Automated insight generation
│
├── notebooks/
│   └── sales_analysis.ipynb    # Jupyter notebook for exploration
│
├── outputs/                    # Generated outputs (charts, reports)
│   └── .gitkeep
│
└── images/                     # Screenshots and images
    └── .gitkeep
```

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/sales-demand-forecasting.git
   cd sales-demand-forecasting
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**

   - **Windows (PowerShell)**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD)**:
     ```cmd
     .\.venv\Scripts\activate.bat
     ```
   - **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

The dashboard will open automatically in your default browser at `http://localhost:8501`.

## 💻 Usage

1. **Launch** the dashboard with `streamlit run app.py`
2. **Choose a data source** — use the sample dataset or upload your own CSV/Excel file
3. **Navigate** between pages using the sidebar menu
4. **Apply filters** in the sidebar to focus on specific date ranges, categories, regions, or products
5. **Explore forecasts** on the Demand Forecasting page
6. **Review insights** on the Business Insights page

## 📂 How to Use Your Own Dataset

### Option 1: Upload via Dashboard (Recommended)
1. Launch the dashboard with `streamlit run app.py`
2. In the sidebar under **Data Source**, select **"Upload CSV"** or **"Upload Excel"**
3. Click **Browse files** and select your sales data file
4. The app will automatically:
   - Detect your column names and map them to the expected fields
   - Show a data summary (rows, columns, missing values, duplicates)
   - Clean the data (handle missing values, fix types, remove duplicates)
   - Display a log of all cleaning operations performed
   - Generate all charts, forecasts, and insights from your uploaded data

**Supported file formats:**
| Format | Extensions |
|--------|-----------|
| CSV | `.csv` |
| Excel | `.xlsx`, `.xls` |

### Option 2: Replace Sample File
1. Replace `data/sample_sales_data.csv` with your own CSV file
2. Ensure your file has at minimum a date column and a revenue/sales column
3. Restart the application

### Supported Column Names
The application recognizes various column naming conventions:
- **Date**: `Date`, `Order_Date`, `Transaction_Date`, `Sale_Date`
- **Product**: `Product`, `Product_Name`, `Item`, `Item_Name`
- **Revenue**: `Revenue`, `Sales`, `Total_Sales`, `Amount`
- **Category**: `Category`, `Product_Category`, `Segment`
- **Region**: `Region`, `Area`, `Territory`, `Zone`
- And more — see `src/data_cleaning.py` for the full mapping

## 📊 Results

- Interactive dashboard with 8 specialized analysis pages
- Automatic data quality assessment and cleaning
- Exponential Smoothing forecasting with confidence intervals
- Auto-generated business insights
- Support for custom datasets via upload

## 🚀 Future Enhancements

- [ ] Add ARIMA / SARIMA forecasting models
- [ ] Implement Prophet for advanced seasonality detection
- [ ] Add export functionality (PDF reports, CSV downloads)
- [ ] Implement anomaly detection for unusual sales patterns
- [ ] Add customer segmentation analysis (RFM)
- [ ] Support for multiple currencies
- [ ] Add predictive analytics for customer churn
- [ ] Implement A/B testing analysis module
- [ ] Add email alerting for KPI thresholds

## 👤 Author

**[Your Name]**

- B.E. Computer Science / Data Science
- Final Year Project
- Academic Year 2025–2026

---

*Built with ❤️ using Python, Streamlit, and Plotly*
