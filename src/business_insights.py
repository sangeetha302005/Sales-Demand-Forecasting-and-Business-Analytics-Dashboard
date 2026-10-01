"""Automated business insights generation from sales data."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


def generate_insights(df: pd.DataFrame, col_map: Dict) -> List[Dict]:
    """Generate automated business insights from the dataset.
    
    Returns a list of insight dictionaries with 'icon', 'title', and 'detail'.
    """
    insights = []
    
    rev_col = col_map.get('revenue')
    profit_col = col_map.get('profit')
    qty_col = col_map.get('quantity')
    product_col = col_map.get('product')
    category_col = col_map.get('category')
    region_col = col_map.get('region')
    date_col = col_map.get('date')
    
    # --- Product Insights ---
    if product_col and product_col in df.columns:
        if rev_col and rev_col in df.columns:
            prod_rev = df.groupby(product_col)[rev_col].sum()
            
            top_product = prod_rev.idxmax()
            top_rev = prod_rev.max()
            insights.append({
                'icon': '🏆',
                'title': 'Highest Revenue Product',
                'detail': f"**{top_product}** generated the highest revenue of **\${top_rev:,.2f}**."
            })
            
            bottom_product = prod_rev.idxmin()
            bottom_rev = prod_rev.min()
            insights.append({
                'icon': '📉',
                'title': 'Lowest Revenue Product',
                'detail': f"**{bottom_product}** had the lowest revenue at **\${bottom_rev:,.2f}**."
            })
        
        if profit_col and profit_col in df.columns:
            prod_profit = df.groupby(product_col)[profit_col].sum()
            top_profit_product = prod_profit.idxmax()
            top_profit_val = prod_profit.max()
            insights.append({
                'icon': '💰',
                'title': 'Most Profitable Product',
                'detail': f"**{top_profit_product}** is the most profitable with **\${top_profit_val:,.2f}** in total profit."
            })
    
    # --- Category Insights ---
    if category_col and category_col in df.columns:
        if rev_col and rev_col in df.columns:
            cat_rev = df.groupby(category_col)[rev_col].sum()
            top_cat = cat_rev.idxmax()
            top_cat_rev = cat_rev.max()
            insights.append({
                'icon': '📦',
                'title': 'Top Category',
                'detail': f"**{top_cat}** is the highest-revenue category with **\${top_cat_rev:,.2f}**."
            })
        
        if profit_col and profit_col in df.columns:
            cat_profit = df.groupby(category_col)[profit_col].sum()
            top_profit_cat = cat_profit.idxmax()
            top_profit_cat_val = cat_profit.max()
            insights.append({
                'icon': '💎',
                'title': 'Highest-Profit Category',
                'detail': f"**{top_profit_cat}** has the highest total profit at **\${top_profit_cat_val:,.2f}**."
            })
    
    # --- Region Insights ---
    if region_col and region_col in df.columns and rev_col and rev_col in df.columns:
        region_rev = df.groupby(region_col)[rev_col].sum()
        top_region = region_rev.idxmax()
        top_region_rev = region_rev.max()
        insights.append({
            'icon': '🌍',
            'title': 'Best Performing Region',
            'detail': f"**{top_region}** leads all regions with **\${top_region_rev:,.2f}** in revenue."
        })
    
    # --- Time-based Insights ---
    if date_col and date_col in df.columns and rev_col and rev_col in df.columns:
        if 'Month_Name' in df.columns and 'Year' in df.columns:
            monthly = df.groupby([df[date_col].dt.to_period('M')])[rev_col].sum()
            if len(monthly) > 0:
                best_month = monthly.idxmax()
                best_month_rev = monthly.max()
                insights.append({
                    'icon': '📅',
                    'title': 'Highest Sales Month',
                    'detail': f"**{best_month}** was the best month with **\${best_month_rev:,.2f}** in revenue."
                })
        
        # Year-over-year growth
        if 'Year' in df.columns:
            yearly = df.groupby('Year')[rev_col].sum()
            if len(yearly) >= 2:
                years_sorted = yearly.sort_index()
                latest_year = years_sorted.index[-1]
                prev_year = years_sorted.index[-2]
                growth = ((years_sorted.iloc[-1] - years_sorted.iloc[-2]) / years_sorted.iloc[-2]) * 100
                direction = 'increased' if growth > 0 else 'decreased'
                insights.append({
                    'icon': '📊',
                    'title': 'Year-over-Year Growth',
                    'detail': f"Revenue {direction} by **{abs(growth):.1f}%** from {prev_year} to {latest_year}."
                })
    
    # --- Trend Insights for Products ---
    if product_col and product_col in df.columns and date_col and date_col in df.columns and rev_col and rev_col in df.columns:
        if 'Year' in df.columns:
            yearly_prod = df.groupby(['Year', product_col])[rev_col].sum().reset_index()
            years = sorted(yearly_prod['Year'].unique())
            if len(years) >= 2:
                latest = years[-1]
                previous = years[-2]
                
                latest_data = yearly_prod[yearly_prod['Year'] == latest].set_index(product_col)[rev_col]
                prev_data = yearly_prod[yearly_prod['Year'] == previous].set_index(product_col)[rev_col]
                
                common_products = latest_data.index.intersection(prev_data.index)
                if len(common_products) > 0:
                    growth_rates = ((latest_data[common_products] - prev_data[common_products]) / prev_data[common_products] * 100)
                    
                    growing = growth_rates[growth_rates > 0]
                    if len(growing) > 0:
                        fastest = growing.idxmax()
                        fastest_rate = growing.max()
                        insights.append({
                            'icon': '🚀',
                            'title': 'Fastest Growing Product',
                            'detail': f"**{fastest}** showed the highest demand growth at **{fastest_rate:.1f}%** ({previous}→{latest})."
                        })
                    
                    declining = growth_rates[growth_rates < 0]
                    if len(declining) > 0:
                        slowest = declining.idxmin()
                        slowest_rate = declining.min()
                        insights.append({
                            'icon': '⚠️',
                            'title': 'Declining Product',
                            'detail': f"**{slowest}** experienced a demand decline of **{abs(slowest_rate):.1f}%** ({previous}→{latest})."
                        })
    
    # --- Profit Margin Insight ---
    if rev_col and profit_col and rev_col in df.columns and profit_col in df.columns:
        total_rev = df[rev_col].sum()
        total_profit = df[profit_col].sum()
        if total_rev > 0:
            margin = (total_profit / total_rev) * 100
            insights.append({
                'icon': '📈',
                'title': 'Overall Profit Margin',
                'detail': f"The overall profit margin is **{margin:.1f}%**."
            })
    
    # --- Average Order Value ---
    if rev_col and rev_col in df.columns:
        aov = df[rev_col].mean()
        insights.append({
            'icon': '🛒',
            'title': 'Average Transaction Value',
            'detail': f"The average transaction value is **\${aov:,.2f}**."
        })
    
    return insights
