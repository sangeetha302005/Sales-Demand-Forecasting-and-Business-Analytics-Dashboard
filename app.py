"""Sales Demand Forecasting & Business Analytics Dashboard."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_cleaning import load_and_prepare, get_data_summary, identify_columns
from src.eda import (
    create_kpi_metrics, plot_monthly_revenue_trend, plot_monthly_profit_trend,
    plot_revenue_vs_profit, plot_sales_by_region, plot_daily_sales,
    plot_yearly_sales, plot_quantity_trend, plot_category_performance,
    plot_top_products, plot_product_history, plot_region_comparison,
    plot_sales_rep_performance, get_rep_summary
)
from src.forecasting import run_forecast_pipeline
from src.business_insights import generate_insights

# ───────────── Page Configuration ─────────────
st.set_page_config(
    page_title="Sales Demand Forecasting Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ───────────── Custom CSS ─────────────
st.markdown("""
<style>
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white !important;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .kpi-card h3 {
        margin: 0;
        font-size: 14px;
        opacity: 0.9;
        color: white !important;
    }
    .kpi-card h2 {
        margin: 5px 0 0 0;
        font-size: 28px;
        color: white !important;
    }
    .kpi-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .kpi-blue {
        background: linear-gradient(135deg, #2E86AB 0%, #5DADE2 100%);
    }
    .kpi-orange {
        background: linear-gradient(135deg, #F2994A 0%, #F2C94C 100%);
    }
    .kpi-purple {
        background: linear-gradient(135deg, #6C63FF 0%, #B06AB3 100%);
    }
    .kpi-red {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    .insight-card {
        background: rgba(46, 134, 171, 0.1);
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2E86AB;
        margin-bottom: 10px;
        color: inherit;
    }
    /* KPI metric cards — theme-aware */
    div[data-testid="stMetric"] {
        background-color: rgba(46, 134, 171, 0.12);
        border-radius: 8px;
        padding: 10px 15px;
        border-left: 4px solid #2E86AB;
    }
    div[data-testid="stMetric"] label {
        color: inherit !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: inherit !important;
    }
</style>
""", unsafe_allow_html=True)


# ───────────── Helper Functions ─────────────
def format_currency(value):
    """Format a number as currency."""
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:,.1f}M"
    elif abs(value) >= 1_000:
        return f"${value/1_000:,.1f}K"
    return f"${value:,.2f}"


def format_number(value):
    """Format a number with commas."""
    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:,.1f}M"
    elif abs(value) >= 1_000:
        return f"{value/1_000:,.1f}K"
    return f"{value:,.0f}"


def render_kpi_card(title, value, css_class="kpi-card"):
    """Render a KPI card with HTML."""
    st.markdown(f"""
    <div class="{css_class}">
        <h3>{title}</h3>
        <h2>{value}</h2>
    </div>
    """, unsafe_allow_html=True)


# ───────────── Sidebar ─────────────
st.sidebar.title("📊 Sales Dashboard")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Navigate to",
    ["📋 Executive Overview", "📈 Sales Analysis", "🛍️ Product Analysis",
     "🌍 Regional Analysis", "👤 Sales Rep Analysis",
     "🔮 Demand Forecasting", "📊 Model Evaluation", "💡 Business Insights"],
    index=0
)

st.sidebar.markdown("---")

# ───────────── Data Loading ─────────────
st.sidebar.subheader("📂 Data Source")

data_source = st.sidebar.radio(
    "Choose data source",
    ["Sample Dataset", "Upload CSV", "Upload Excel"],
    index=0
)

df = None
column_map = None
operations = []

try:
    if data_source == "Sample Dataset":
        sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'sample_sales_data.csv')
        if os.path.exists(sample_path):
            df, column_map, operations = load_and_prepare(file_path=sample_path)
        else:
            st.error("Sample dataset not found. Please place 'sample_sales_data.csv' in the 'data/' folder or upload your own data.")
            st.stop()
    
    elif data_source == "Upload CSV":
        uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=['csv'])
        if uploaded_file is not None:
            df, column_map, operations = load_and_prepare(uploaded_file=uploaded_file)
        else:
            st.info("👆 Please upload a CSV file to begin.")
            st.stop()
    
    elif data_source == "Upload Excel":
        uploaded_file = st.sidebar.file_uploader("Upload Excel file", type=['xlsx', 'xls'])
        if uploaded_file is not None:
            df, column_map, operations = load_and_prepare(uploaded_file=uploaded_file)
        else:
            st.info("👆 Please upload an Excel file to begin.")
            st.stop()

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

if df is None:
    st.stop()

# ───────────── Sidebar Filters ─────────────
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filters")

# Date filter
date_col = column_map.get('date')
if date_col and date_col in df.columns:
    min_date = df[date_col].min().date()
    max_date = df[date_col].max().date()
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        df = df[(df[date_col].dt.date >= date_range[0]) & (df[date_col].dt.date <= date_range[1])]

# Category filter
cat_col = column_map.get('category')
if cat_col and cat_col in df.columns:
    categories = ['All'] + sorted(df[cat_col].dropna().unique().tolist())
    selected_cat = st.sidebar.selectbox("Category", categories)
    if selected_cat != 'All':
        df = df[df[cat_col] == selected_cat]

# Region filter
region_col = column_map.get('region')
if region_col and region_col in df.columns:
    regions = ['All'] + sorted(df[region_col].dropna().unique().tolist())
    selected_region = st.sidebar.selectbox("Region", regions)
    if selected_region != 'All':
        df = df[df[region_col] == selected_region]

# Product filter
product_col = column_map.get('product')
if product_col and product_col in df.columns:
    products = ['All'] + sorted(df[product_col].dropna().unique().tolist())
    selected_product = st.sidebar.selectbox("Product", products)
    if selected_product != 'All':
        df = df[df[product_col] == selected_product]

# Sales Rep filter
rep_col = column_map.get('sales_rep')
if rep_col and rep_col in df.columns:
    reps = ['All'] + sorted(df[rep_col].dropna().unique().tolist())
    selected_rep = st.sidebar.selectbox("Sales Representative", reps)
    if selected_rep != 'All':
        df = df[df[rep_col] == selected_rep]

# Show filtered data count
st.sidebar.markdown(f"**Showing {len(df):,} records**")


# ───────────────────────────────────────────────
# PAGE: Executive Overview
# ───────────────────────────────────────────────
if page == "📋 Executive Overview":
    st.title("📋 Executive Overview")
    st.markdown("A high-level summary of sales performance.")
    
    metrics = create_kpi_metrics(df, column_map)
    
    # KPI Row
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.metric("Total Revenue", format_currency(metrics['total_revenue']))
    with c2:
        st.metric("Total Profit", format_currency(metrics['total_profit']))
    with c3:
        st.metric("Total Quantity", format_number(metrics['total_quantity']))
    with c4:
        st.metric("Total Orders", format_number(metrics['total_orders']))
    with c5:
        st.metric("Avg Order Value", format_currency(metrics['avg_order_value']))
    with c6:
        st.metric("Avg Selling Price", format_currency(metrics['avg_selling_price']))
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    with col1:
        fig = plot_monthly_revenue_trend(df, column_map)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = plot_monthly_profit_trend(df, column_map)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    with col1:
        fig = plot_revenue_vs_profit(df, column_map)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = plot_sales_by_region(df, column_map)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Data Summary
    with st.expander("📊 Dataset Summary"):
        summary = get_data_summary(df)
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Rows", f"{summary['rows']:,}")
        sc2.metric("Columns", summary['columns'])
        sc3.metric("Missing Values", summary['total_missing'])
        sc4.metric("Duplicates", summary['duplicates'])
        
        st.markdown("**Column Types:**")
        st.json(summary['dtypes'])
        
        st.markdown("**Sample Data:**")
        st.dataframe(df.head(10), use_container_width=True)
    
    # Cleaning Log
    with st.expander("🧹 Data Cleaning Log"):
        for op in operations:
            st.markdown(f"✅ {op}")


# ───────────────────────────────────────────────
# PAGE: Sales Analysis
# ───────────────────────────────────────────────
elif page == "📈 Sales Analysis":
    st.title("📈 Sales Analysis")
    st.markdown("Detailed sales trends and patterns.")
    
    # Quick KPIs
    metrics = create_kpi_metrics(df, column_map)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", format_currency(metrics['total_revenue']))
    c2.metric("Total Profit", format_currency(metrics['total_profit']))
    c3.metric("Total Quantity", format_number(metrics['total_quantity']))
    
    st.markdown("---")
    
    # Daily Sales
    fig = plot_daily_sales(df, column_map)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Monthly and Yearly
    col1, col2 = st.columns(2)
    with col1:
        fig = plot_monthly_revenue_trend(df, column_map)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = plot_yearly_sales(df, column_map)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Profit and Quantity
    col1, col2 = st.columns(2)
    with col1:
        fig = plot_monthly_profit_trend(df, column_map)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = plot_quantity_trend(df, column_map)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Category Performance
    fig = plot_category_performance(df, column_map)
    if fig:
        st.plotly_chart(fig, use_container_width=True)


# ───────────────────────────────────────────────
# PAGE: Product Analysis
# ───────────────────────────────────────────────
elif page == "🛍️ Product Analysis":
    st.title("🛍️ Product Analysis")
    st.markdown("Product-level performance insights.")
    
    col1, col2 = st.columns(2)
    with col1:
        fig = plot_top_products(df, column_map, top_n=10, ascending=False)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = plot_top_products(df, column_map, top_n=10, ascending=True)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Product detail
    p_col = column_map.get('product')
    if p_col and p_col in df.columns:
        st.markdown("---")
        st.subheader("🔍 Product Deep Dive")
        product_list = sorted(df[p_col].dropna().unique().tolist())
        selected = st.selectbox("Select a product to inspect", product_list, key="product_deep_dive")
        
        if selected:
            prod_df = df[df[p_col] == selected]
            rev_col = column_map.get('revenue')
            profit_col = column_map.get('profit')
            qty_col = column_map.get('quantity')
            
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Transactions", f"{len(prod_df):,}")
            if rev_col and rev_col in prod_df.columns:
                mc2.metric("Total Revenue", format_currency(prod_df[rev_col].sum()))
            if profit_col and profit_col in prod_df.columns:
                mc3.metric("Total Profit", format_currency(prod_df[profit_col].sum()))
            if qty_col and qty_col in prod_df.columns:
                mc4.metric("Total Quantity", format_number(prod_df[qty_col].sum()))
            
            fig = plot_product_history(df, column_map, selected)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    # Category performance
    st.markdown("---")
    fig = plot_category_performance(df, column_map)
    if fig:
        st.plotly_chart(fig, use_container_width=True)


# ───────────────────────────────────────────────
# PAGE: Regional Analysis
# ───────────────────────────────────────────────
elif page == "🌍 Regional Analysis":
    st.title("🌍 Regional Analysis")
    st.markdown("Geographic performance breakdown.")
    
    r_col = column_map.get('region')
    if r_col and r_col in df.columns:
        # Region KPIs
        rev_col = column_map.get('revenue')
        profit_col = column_map.get('profit')
        qty_col = column_map.get('quantity')
        
        col1, col2 = st.columns(2)
        with col1:
            fig = plot_region_comparison(df, column_map, metric='revenue')
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = plot_region_comparison(df, column_map, metric='profit')
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        fig = plot_region_comparison(df, column_map, metric='quantity')
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Regional ranking table
        st.subheader("🏆 Regional Ranking")
        agg_dict = {}
        if rev_col and rev_col in df.columns:
            agg_dict[rev_col] = 'sum'
        if profit_col and profit_col in df.columns:
            agg_dict[profit_col] = 'sum'
        if qty_col and qty_col in df.columns:
            agg_dict[qty_col] = 'sum'
        
        if agg_dict:
            region_table = df.groupby(r_col).agg(agg_dict).reset_index()
            region_table['Transactions'] = df.groupby(r_col).size().values
            if rev_col in agg_dict:
                region_table = region_table.sort_values(rev_col, ascending=False)
            st.dataframe(region_table, use_container_width=True, hide_index=True)
    else:
        st.warning("No region column found in the dataset.")


# ───────────────────────────────────────────────
# PAGE: Sales Rep Analysis
# ───────────────────────────────────────────────
elif page == "👤 Sales Rep Analysis":
    st.title("👤 Sales Representative Analysis")
    
    sr_col = column_map.get('sales_rep')
    if sr_col and sr_col in df.columns:
        st.markdown("Performance comparison of sales representatives.")
        
        fig = plot_sales_rep_performance(df, column_map)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Summary table
        st.subheader("📋 Summary Table")
        rep_table = get_rep_summary(df, column_map)
        if rep_table is not None:
            st.dataframe(rep_table, use_container_width=True, hide_index=True)
    else:
        st.warning("No sales representative column found in the dataset. "
                   "Upload a dataset with a 'Sales_Representative' or similar column to use this feature.")


# ───────────────────────────────────────────────
# PAGE: Demand Forecasting
# ───────────────────────────────────────────────
elif page == "🔮 Demand Forecasting":
    st.title("🔮 Demand Forecasting")
    st.markdown("Forecast future demand using statistical models.")
    
    # Forecast settings
    fc_col1, fc_col2 = st.columns(2)
    with fc_col1:
        freq = st.selectbox("Forecast Frequency", ['Monthly', 'Daily'], index=0)
    freq_code = 'M' if freq == 'Monthly' else 'D'
    
    with st.spinner("Running forecast pipeline..."):
        results = run_forecast_pipeline(df, column_map, freq=freq_code)
    
    if not results['success']:
        st.warning(results['message'])
    else:
        st.success(results['message'])
        
        # Historical time series
        ts = results['time_series']
        st.subheader("📈 Historical Demand")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ts.index, y=ts['Revenue'], mode='lines',
                                 name='Historical Revenue', line=dict(color='#2E86AB', width=2)))
        fig.update_layout(title='Historical Revenue Time Series',
                          xaxis_title='Date', yaxis_title='Revenue',
                          template='plotly_white', hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        
        # Train/Test Split Visualization
        train = results['train']
        test = results['test']
        
        # Actual vs Predicted
        st.subheader("🎯 Actual vs Predicted")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=train.index, y=train['Revenue'], mode='lines',
                                 name='Training Data', line=dict(color='#2E86AB', width=2)))
        fig.add_trace(go.Scatter(x=test.index, y=test['Revenue'], mode='lines',
                                 name='Actual (Test)', line=dict(color='#28A745', width=2)))
        
        if results['baseline_forecast'] is not None:
            bf = results['baseline_forecast']
            fig.add_trace(go.Scatter(x=bf.index, y=bf['Predicted'], mode='lines',
                                     name='Moving Average', line=dict(color='#F18F01', width=2, dash='dash')))
        
        if results['model_forecast'] is not None:
            mf = results['model_forecast']
            fig.add_trace(go.Scatter(x=mf.index, y=mf['Predicted'], mode='lines',
                                     name=mf['Model'].iloc[0], line=dict(color='#DC3545', width=2, dash='dot')))
        
        fig.update_layout(title='Actual vs Predicted',
                          xaxis_title='Date', yaxis_title='Revenue',
                          template='plotly_white', hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        
        # Future Forecast
        if results['future_forecast'] is not None:
            st.subheader("🔮 Future Forecast")
            future = results['future_forecast']
            
            fig = go.Figure()
            # Historical tail
            tail_len = min(12, len(ts))
            tail = ts.iloc[-tail_len:]
            fig.add_trace(go.Scatter(x=tail.index, y=tail['Revenue'], mode='lines',
                                     name='Historical', line=dict(color='#2E86AB', width=2)))
            # Forecast
            fig.add_trace(go.Scatter(x=future['Date'], y=future['Forecast'], mode='lines+markers',
                                     name='Forecast', line=dict(color='#DC3545', width=2)))
            # Confidence interval
            fig.add_trace(go.Scatter(
                x=pd.concat([future['Date'], future['Date'].iloc[::-1]]),
                y=pd.concat([future['Upper_CI'], future['Lower_CI'].iloc[::-1]]),
                fill='toself', fillcolor='rgba(220,53,69,0.1)',
                line=dict(color='rgba(255,255,255,0)'),
                name='95% Confidence Interval'
            ))
            fig.update_layout(title='Future Demand Forecast',
                              xaxis_title='Date', yaxis_title='Revenue',
                              template='plotly_white', hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
            
            # Forecast Table
            st.subheader("📋 Forecast Table")
            display_future = future.copy()
            display_future['Date'] = display_future['Date'].dt.strftime('%Y-%m-%d')
            for col in ['Forecast', 'Lower_CI', 'Upper_CI']:
                display_future[col] = display_future[col].round(2)
            st.dataframe(display_future, use_container_width=True, hide_index=True)


# ───────────────────────────────────────────────
# PAGE: Model Evaluation
# ───────────────────────────────────────────────
elif page == "📊 Model Evaluation":
    st.title("📊 Model Evaluation")
    st.markdown("Compare forecasting model performance.")
    
    freq = st.selectbox("Evaluation Frequency", ['Monthly', 'Daily'], index=0, key='eval_freq')
    freq_code = 'M' if freq == 'Monthly' else 'D'
    
    with st.spinner("Evaluating models..."):
        results = run_forecast_pipeline(df, column_map, freq=freq_code)
    
    if not results['success']:
        st.warning(results['message'])
    else:
        # Metrics comparison
        st.subheader("📏 Evaluation Metrics")
        
        metrics_data = []
        if results['baseline_metrics']:
            metrics_data.append({
                'Model': 'Moving Average (Baseline)',
                **results['baseline_metrics']
            })
        if results['model_metrics']:
            model_name = results['model_forecast']['Model'].iloc[0] if results['model_forecast'] is not None else 'Exp. Smoothing'
            metrics_data.append({
                'Model': model_name,
                **results['model_metrics']
            })
        
        if metrics_data:
            metrics_df = pd.DataFrame(metrics_data)
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)
            
            # Explain metrics
            st.markdown("---")
            st.subheader("📖 Understanding the Metrics")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""**MAE (Mean Absolute Error)**
                
The average absolute difference between predicted and actual values.

Lower is better. Easy to interpret — it's in the same unit as revenue.""")
            
            with col2:
                st.markdown("""**RMSE (Root Mean Squared Error)**
                
Similar to MAE but penalizes large errors more heavily.

Lower is better. Useful for detecting if the model makes occasional big mistakes.""")
            
            with col3:
                st.markdown("""**MAPE (Mean Absolute Percentage Error)**
                
The average percentage error of predictions.

Lower is better. Gives a sense of error relative to the actual values.

- < 10%: Excellent
- 10-20%: Good
- 20-50%: Reasonable
- \> 50%: Poor""")
            
            # Visual comparison
            st.markdown("---")
            st.subheader("📊 Visual Comparison")
            
            fig = go.Figure()
            for metric_row in metrics_data:
                fig.add_trace(go.Bar(
                    name=metric_row['Model'],
                    x=['MAE', 'RMSE'],
                    y=[metric_row['MAE'], metric_row['RMSE']]
                ))
            fig.update_layout(title='Model Comparison (MAE & RMSE)',
                              barmode='group', template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
            
            # MAPE comparison
            fig2 = go.Figure()
            for metric_row in metrics_data:
                fig2.add_trace(go.Bar(
                    name=metric_row['Model'],
                    x=['MAPE (%)'],
                    y=[metric_row['MAPE']]
                ))
            fig2.update_layout(title='Model Comparison (MAPE %)',
                               barmode='group', template='plotly_white')
            st.plotly_chart(fig2, use_container_width=True)


# ───────────────────────────────────────────────
# PAGE: Business Insights
# ───────────────────────────────────────────────
elif page == "💡 Business Insights":
    st.title("💡 Business Insights")
    st.markdown("Automatically generated insights from your sales data.")
    
    insights = generate_insights(df, column_map)
    
    if not insights:
        st.info("Not enough data to generate insights. Try loading a dataset with more columns.")
    else:
        for i, insight in enumerate(insights):
            st.markdown(f"""
            <div class="insight-card">
                <strong>{insight['icon']} {insight['title']}</strong><br>
                {insight['detail']}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.info(f"📊 **{len(insights)} insights** generated from {len(df):,} records.")


# ───────────── Footer ─────────────
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='text-align: center; color: #888; font-size: 12px;'>"
    "Sales Demand Forecasting Dashboard<br>"
    "Built with Streamlit & Plotly"
    "</div>",
    unsafe_allow_html=True
)
