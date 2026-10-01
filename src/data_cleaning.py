"""Data cleaning and preprocessing module for sales data."""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Optional


def identify_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """Identify standard columns from various naming conventions.
    
    Returns a mapping of standard names to actual column names found.
    """
    column_map = {}
    
    mappings = {
        'date': ['date', 'order_date', 'transaction_date', 'sale_date', 'orderdate', 'trans_date'],
        'product': ['product', 'product_name', 'item', 'item_name', 'productname'],
        'category': ['category', 'product_category', 'cat', 'segment', 'product_type'],
        'region': ['region', 'area', 'territory', 'zone', 'location', 'state', 'city'],
        'sales_rep': ['sales_representative', 'sales_rep', 'salesperson', 'rep', 'representative', 'agent', 'salesman'],
        'quantity': ['quantity', 'qty', 'units', 'units_sold', 'quantity_sold', 'count'],
        'unit_price': ['unit_price', 'price', 'selling_price', 'unitprice', 'price_per_unit'],
        'revenue': ['revenue', 'sales', 'total_sales', 'amount', 'total_amount', 'total_revenue', 'sales_amount'],
        'cost': ['cost', 'total_cost', 'cogs', 'cost_of_goods', 'expense', 'unit_cost'],
        'profit': ['profit', 'net_profit', 'margin', 'gross_profit', 'earnings'],
    }
    
    df_cols_lower = {col.lower().strip().replace(' ', '_'): col for col in df.columns}
    
    for standard_name, variants in mappings.items():
        column_map[standard_name] = None
        for variant in variants:
            if variant in df_cols_lower:
                column_map[standard_name] = df_cols_lower[variant]
                break
    
    return column_map


def get_data_summary(df: pd.DataFrame) -> Dict:
    """Generate a summary of the dataset."""
    summary = {
        'rows': len(df),
        'columns': len(df.columns),
        'column_names': list(df.columns),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'total_missing': int(df.isnull().sum().sum()),
        'duplicates': int(df.duplicated().sum()),
        'memory_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
    }
    return summary


def clean_data(df: pd.DataFrame, column_map: Dict[str, Optional[str]]) -> Tuple[pd.DataFrame, List[str]]:
    """Clean the dataset and return cleaned DataFrame with log of operations."""
    df = df.copy()
    operations = []
    
    # 1. Remove exact duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        df = df.drop_duplicates().reset_index(drop=True)
        operations.append(f"Removed {dup_count} duplicate rows.")
    
    # 2. Handle date column
    date_col = column_map.get('date')
    if date_col and date_col in df.columns:
        original_nulls = df[date_col].isnull().sum()
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=False)
        new_nulls = df[date_col].isnull().sum()
        if new_nulls > original_nulls:
            operations.append(f"Converted '{date_col}' to datetime. {new_nulls - original_nulls} invalid dates set to NaT.")
        else:
            operations.append(f"Converted '{date_col}' to datetime.")
        
        # Drop rows with no date
        null_dates = df[date_col].isnull().sum()
        if null_dates > 0:
            df = df.dropna(subset=[date_col]).reset_index(drop=True)
            operations.append(f"Removed {null_dates} rows with missing dates.")
        
        # Sort by date
        df = df.sort_values(date_col).reset_index(drop=True)
        operations.append("Sorted data by date.")
    
    # 3. Convert numeric columns
    numeric_cols = ['quantity', 'unit_price', 'revenue', 'cost', 'profit']
    for std_name in numeric_cols:
        col = column_map.get(std_name)
        if col and col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            null_count = df[col].isnull().sum()
            if null_count > 0:
                if std_name == 'quantity':
                    df[col] = df[col].fillna(1)
                    operations.append(f"Filled {null_count} missing '{col}' values with 1.")
                else:
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)
                    operations.append(f"Filled {null_count} missing '{col}' values with median ({median_val:.2f}).")
    
    # 4. Fill missing categorical values
    cat_cols = ['product', 'category', 'region', 'sales_rep']
    for std_name in cat_cols:
        col = column_map.get(std_name)
        if col and col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                df[col] = df[col].fillna('Unknown')
                operations.append(f"Filled {null_count} missing '{col}' values with 'Unknown'.")
    
    # 5. Calculate Revenue if missing but Quantity and Unit_Price exist
    qty_col = column_map.get('quantity')
    price_col = column_map.get('unit_price')
    rev_col = column_map.get('revenue')
    cost_col = column_map.get('cost')
    profit_col = column_map.get('profit')
    
    if rev_col is None and qty_col and price_col:
        if qty_col in df.columns and price_col in df.columns:
            df['Revenue'] = (df[qty_col] * df[price_col]).round(2)
            column_map['revenue'] = 'Revenue'
            operations.append("Calculated 'Revenue' from Quantity × Unit_Price.")
    
    # 6. Calculate Profit if missing but Revenue and Cost exist
    rev_col = column_map.get('revenue')  # refresh
    if profit_col is None and rev_col and cost_col:
        if rev_col in df.columns and cost_col in df.columns:
            df['Profit'] = (df[rev_col] - df[cost_col]).round(2)
            column_map['profit'] = 'Profit'
            operations.append("Calculated 'Profit' from Revenue − Cost.")
    
    # 7. Add derived date columns
    date_col = column_map.get('date')
    if date_col and date_col in df.columns:
        df['Year'] = df[date_col].dt.year
        df['Month'] = df[date_col].dt.month
        df['Month_Name'] = df[date_col].dt.strftime('%B')
        df['Quarter'] = df[date_col].dt.quarter
        df['Day_of_Week'] = df[date_col].dt.day_name()
        df['Week_Number'] = df[date_col].dt.isocalendar().week.astype(int)
        operations.append("Added derived date columns: Year, Month, Month_Name, Quarter, Day_of_Week, Week_Number.")
    
    # 8. Remove negative quantities
    qty_col = column_map.get('quantity')
    if qty_col and qty_col in df.columns:
        neg_count = (df[qty_col] < 0).sum()
        if neg_count > 0:
            df = df[df[qty_col] >= 0].reset_index(drop=True)
            operations.append(f"Removed {neg_count} rows with negative quantities.")
    
    if not operations:
        operations.append("No cleaning operations were necessary.")
    
    return df, operations


def load_and_prepare(file_path: str = None, uploaded_file=None) -> Tuple[pd.DataFrame, Dict, List[str]]:
    """Load data from file path or uploaded file, clean it, and return results."""
    if uploaded_file is not None:
        file_name = uploaded_file.name
        if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            df = pd.read_csv(uploaded_file)
    elif file_path:
        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            df = pd.read_csv(file_path)
    else:
        raise ValueError("No data source provided.")
    
    column_map = identify_columns(df)
    df_clean, operations = clean_data(df, column_map)
    
    return df_clean, column_map, operations
