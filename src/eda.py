"""Exploratory Data Analysis and visualization functions."""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Optional


def create_kpi_metrics(df: pd.DataFrame, col_map: Dict) -> Dict:
    """Calculate KPI metrics from the dataset."""
    metrics = {}
    
    rev_col = col_map.get('revenue')
    profit_col = col_map.get('profit')
    qty_col = col_map.get('quantity')
    
    metrics['total_revenue'] = df[rev_col].sum() if rev_col and rev_col in df.columns else 0
    metrics['total_profit'] = df[profit_col].sum() if profit_col and profit_col in df.columns else 0
    metrics['total_quantity'] = int(df[qty_col].sum()) if qty_col and qty_col in df.columns else 0
    metrics['total_orders'] = len(df)
    metrics['avg_order_value'] = metrics['total_revenue'] / metrics['total_orders'] if metrics['total_orders'] > 0 else 0
    
    if rev_col and rev_col in df.columns and qty_col and qty_col in df.columns:
        total_qty = df[qty_col].sum()
        metrics['avg_selling_price'] = df[rev_col].sum() / total_qty if total_qty > 0 else 0
    else:
        metrics['avg_selling_price'] = 0
    
    if rev_col and rev_col in df.columns:
        metrics['profit_margin'] = (metrics['total_profit'] / metrics['total_revenue'] * 100) if metrics['total_revenue'] > 0 else 0
    else:
        metrics['profit_margin'] = 0
    
    return metrics


def plot_monthly_revenue_trend(df: pd.DataFrame, col_map: Dict) -> Optional[go.Figure]:
    """Plot monthly revenue trend."""
    date_col = col_map.get('date')
    rev_col = col_map.get('revenue')
    if not date_col or not rev_col or date_col not in df.columns or rev_col not in df.columns:
        return None
    
    monthly = df.groupby(df[date_col].dt.to_period('M')).agg({rev_col: 'sum'}).reset_index()
    monthly[date_col] = monthly[date_col].dt.to_timestamp()
    
    fig = px.line(monthly, x=date_col, y=rev_col,
                  title='Monthly Revenue Trend',
                  labels={date_col: 'Month', rev_col: 'Revenue'},
                  template='plotly_white')
    fig.update_traces(line=dict(width=2.5, color='#2E86AB'))
    fig.update_layout(hovermode='x unified')
    return fig


def plot_monthly_profit_trend(df: pd.DataFrame, col_map: Dict) -> Optional[go.Figure]:
    """Plot monthly profit trend."""
    date_col = col_map.get('date')
    profit_col = col_map.get('profit')
    if not date_col or not profit_col or date_col not in df.columns or profit_col not in df.columns:
        return None
    
    monthly = df.groupby(df[date_col].dt.to_period('M')).agg({profit_col: 'sum'}).reset_index()
    monthly[date_col] = monthly[date_col].dt.to_timestamp()
    
    fig = px.line(monthly, x=date_col, y=profit_col,
                  title='Monthly Profit Trend',
                  labels={date_col: 'Month', profit_col: 'Profit'},
                  template='plotly_white')
    fig.update_traces(line=dict(width=2.5, color='#28A745'))
    fig.update_layout(hovermode='x unified')
    return fig


def plot_revenue_vs_profit(df: pd.DataFrame, col_map: Dict) -> Optional[go.Figure]:
    """Plot revenue vs profit monthly comparison."""
    date_col = col_map.get('date')
    rev_col = col_map.get('revenue')
    profit_col = col_map.get('profit')
    if not all([date_col, rev_col, profit_col]):
        return None
    if not all(c in df.columns for c in [date_col, rev_col, profit_col]):
        return None
    
    monthly = df.groupby(df[date_col].dt.to_period('M')).agg(
        {rev_col: 'sum', profit_col: 'sum'}
    ).reset_index()
    monthly[date_col] = monthly[date_col].dt.to_timestamp()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly[date_col], y=monthly[rev_col], name='Revenue', marker_color='#2E86AB'))
    fig.add_trace(go.Bar(x=monthly[date_col], y=monthly[profit_col], name='Profit', marker_color='#28A745'))
    fig.update_layout(title='Revenue vs Profit (Monthly)',
                      barmode='group', template='plotly_white',
                      hovermode='x unified')
    return fig


def plot_sales_by_region(df: pd.DataFrame, col_map: Dict) -> Optional[go.Figure]:
    """Plot sales distribution by region."""
    region_col = col_map.get('region')
    rev_col = col_map.get('revenue')
    if not region_col or not rev_col or region_col not in df.columns or rev_col not in df.columns:
        return None
    
    region_data = df.groupby(region_col).agg({rev_col: 'sum'}).reset_index()
    region_data = region_data.sort_values(rev_col, ascending=True)
    
    fig = px.bar(region_data, x=rev_col, y=region_col, orientation='h',
                 title='Revenue by Region',
                 labels={rev_col: 'Total Revenue', region_col: 'Region'},
                 template='plotly_white',
                 color=region_col,
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(showlegend=False)
    return fig


def plot_daily_sales(df: pd.DataFrame, col_map: Dict) -> Optional[go.Figure]:
    """Plot daily sales trend."""
    date_col = col_map.get('date')
    rev_col = col_map.get('revenue')
    if not date_col or not rev_col or date_col not in df.columns or rev_col not in df.columns:
        return None
    
    daily = df.groupby(date_col).agg({rev_col: 'sum'}).reset_index()
    
    fig = px.line(daily, x=date_col, y=rev_col,
                  title='Daily Revenue Trend',
                  labels={date_col: 'Date', rev_col: 'Revenue'},
                  template='plotly_white')
    fig.update_traces(line=dict(width=1, color='#2E86AB'))
    fig.update_layout(hovermode='x unified')
    return fig


def plot_yearly_sales(df: pd.DataFrame, col_map: Dict) -> Optional[go.Figure]:
    """Plot yearly sales comparison."""
    rev_col = col_map.get('revenue')
    if not rev_col or rev_col not in df.columns or 'Year' not in df.columns:
        return None
    
    yearly = df.groupby('Year').agg({rev_col: 'sum'}).reset_index()
    yearly['Year'] = yearly['Year'].astype(str)
    
    fig = px.bar(yearly, x='Year', y=rev_col,
                 title='Yearly Revenue',
                 labels={rev_col: 'Total Revenue'},
                 template='plotly_white',
                 color='Year',
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(showlegend=False)
    return fig


def plot_quantity_trend(df: pd.DataFrame, col_map: Dict) -> Optional[go.Figure]:
    """Plot monthly quantity trend."""
    date_col = col_map.get('date')
    qty_col = col_map.get('quantity')
    if not date_col or not qty_col or date_col not in df.columns or qty_col not in df.columns:
        return None
    
    monthly = df.groupby(df[date_col].dt.to_period('M')).agg({qty_col: 'sum'}).reset_index()
    monthly[date_col] = monthly[date_col].dt.to_timestamp()
    
    fig = px.bar(monthly, x=date_col, y=qty_col,
                 title='Monthly Quantity Sold',
                 labels={date_col: 'Month', qty_col: 'Quantity'},
                 template='plotly_white',
                 color_discrete_sequence=['#F18F01'])
    fig.update_layout(hovermode='x unified')
    return fig


def plot_category_performance(df: pd.DataFrame, col_map: Dict) -> Optional[go.Figure]:
    """Plot category-wise performance."""
    cat_col = col_map.get('category')
    rev_col = col_map.get('revenue')
    profit_col = col_map.get('profit')
    if not cat_col or not rev_col or cat_col not in df.columns or rev_col not in df.columns:
        return None
    
    agg_dict = {rev_col: 'sum'}
    if profit_col and profit_col in df.columns:
        agg_dict[profit_col] = 'sum'
    
    cat_data = df.groupby(cat_col).agg(agg_dict).reset_index()
    cat_data = cat_data.sort_values(rev_col, ascending=False)
    
    fig = px.bar(cat_data, x=cat_col, y=list(agg_dict.keys()),
                 title='Category Performance',
                 barmode='group',
                 template='plotly_white',
                 color_discrete_sequence=['#2E86AB', '#28A745'])
    return fig


def plot_top_products(df: pd.DataFrame, col_map: Dict, top_n: int = 10, ascending: bool = False) -> Optional[go.Figure]:
    """Plot top or bottom N products by revenue."""
    product_col = col_map.get('product')
    rev_col = col_map.get('revenue')
    if not product_col or not rev_col or product_col not in df.columns or rev_col not in df.columns:
        return None
    
    prod_data = df.groupby(product_col).agg({rev_col: 'sum'}).reset_index()
    prod_data = prod_data.sort_values(rev_col, ascending=ascending).head(top_n)
    
    if not ascending:
        prod_data = prod_data.sort_values(rev_col, ascending=True)
    
    title = f"{'Bottom' if ascending else 'Top'} {top_n} Products by Revenue"
    color = '#DC3545' if ascending else '#2E86AB'
    
    fig = px.bar(prod_data, x=rev_col, y=product_col, orientation='h',
                 title=title,
                 labels={rev_col: 'Total Revenue', product_col: 'Product'},
                 template='plotly_white',
                 color_discrete_sequence=[color])
    return fig


def plot_product_history(df: pd.DataFrame, col_map: Dict, product_name: str) -> Optional[go.Figure]:
    """Plot historical performance of a specific product."""
    date_col = col_map.get('date')
    product_col = col_map.get('product')
    rev_col = col_map.get('revenue')
    if not all([date_col, product_col, rev_col]):
        return None
    if not all(c in df.columns for c in [date_col, product_col, rev_col]):
        return None
    
    prod_df = df[df[product_col] == product_name]
    if prod_df.empty:
        return None
    
    monthly = prod_df.groupby(prod_df[date_col].dt.to_period('M')).agg({rev_col: 'sum'}).reset_index()
    monthly[date_col] = monthly[date_col].dt.to_timestamp()
    
    fig = px.line(monthly, x=date_col, y=rev_col,
                  title=f'Monthly Revenue: {product_name}',
                  labels={date_col: 'Month', rev_col: 'Revenue'},
                  template='plotly_white')
    fig.update_traces(line=dict(width=2.5, color='#2E86AB'), mode='lines+markers')
    fig.update_layout(hovermode='x unified')
    return fig


def plot_region_comparison(df: pd.DataFrame, col_map: Dict, metric: str = 'revenue') -> Optional[go.Figure]:
    """Plot region comparison for a given metric."""
    region_col = col_map.get('region')
    metric_col = col_map.get(metric)
    if not region_col or not metric_col or region_col not in df.columns or metric_col not in df.columns:
        return None
    
    region_data = df.groupby(region_col).agg({metric_col: 'sum'}).reset_index()
    region_data = region_data.sort_values(metric_col, ascending=False)
    
    fig = px.bar(region_data, x=region_col, y=metric_col,
                 title=f'{metric.title()} by Region',
                 template='plotly_white',
                 color=region_col,
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(showlegend=False)
    return fig


def plot_sales_rep_performance(df: pd.DataFrame, col_map: Dict) -> Optional[go.Figure]:
    """Plot sales representative performance."""
    rep_col = col_map.get('sales_rep')
    rev_col = col_map.get('revenue')
    if not rep_col or not rev_col or rep_col not in df.columns or rev_col not in df.columns:
        return None
    
    rep_data = df.groupby(rep_col).agg({rev_col: 'sum'}).reset_index()
    rep_data = rep_data.sort_values(rev_col, ascending=True)
    
    fig = px.bar(rep_data, x=rev_col, y=rep_col, orientation='h',
                 title='Sales Representative Performance (Revenue)',
                 labels={rev_col: 'Total Revenue', rep_col: 'Sales Representative'},
                 template='plotly_white',
                 color_discrete_sequence=['#6F42C1'])
    return fig


def get_rep_summary(df: pd.DataFrame, col_map: Dict) -> Optional[pd.DataFrame]:
    """Get summary table for sales representatives."""
    rep_col = col_map.get('sales_rep')
    rev_col = col_map.get('revenue')
    profit_col = col_map.get('profit')
    qty_col = col_map.get('quantity')
    
    if not rep_col or rep_col not in df.columns:
        return None
    
    agg_dict = {'Transactions': (rep_col, 'count')}
    if rev_col and rev_col in df.columns:
        agg_dict['Total Revenue'] = (rev_col, 'sum')
    if profit_col and profit_col in df.columns:
        agg_dict['Total Profit'] = (profit_col, 'sum')
    if qty_col and qty_col in df.columns:
        agg_dict['Total Quantity'] = (qty_col, 'sum')
    
    result = df.groupby(rep_col).agg(
        **agg_dict
    ).reset_index()
    
    if 'Total Revenue' in result.columns:
        result = result.sort_values('Total Revenue', ascending=False)
        result['Total Revenue'] = result['Total Revenue'].round(2)
    if 'Total Profit' in result.columns:
        result['Total Profit'] = result['Total Profit'].round(2)
    
    result = result.rename(columns={rep_col: 'Sales Representative'})
    return result
