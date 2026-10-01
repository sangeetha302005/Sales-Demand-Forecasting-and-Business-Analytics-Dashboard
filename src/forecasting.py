"""Demand forecasting module with baseline and statistical models."""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


def _normalize_freq(freq: str) -> str:
    """Normalize frequency aliases for cross-pandas compatibility.
    
    Pandas 3.x removed 'M','Q','Y'; pandas 2.x doesn't know 'ME','QE','YE'.
    This detects the version and maps to the correct alias.
    """
    pd_major = int(pd.__version__.split('.')[0])
    if pd_major >= 3:
        # pandas 3.x: use new aliases
        _MAP = {'M': 'ME', 'Q': 'QE', 'Y': 'YE', 'A': 'YE'}
    else:
        # pandas 2.x: use legacy aliases
        _MAP = {'ME': 'M', 'QE': 'Q', 'YE': 'Y'}
    return _MAP.get(freq, freq)


def prepare_time_series(df: pd.DataFrame, col_map: Dict, freq: str = 'ME') -> Optional[pd.DataFrame]:
    """Prepare time series data for forecasting.
    
    Args:
        df: Cleaned DataFrame
        col_map: Column mapping dictionary
        freq: 'D' for daily, 'ME' for monthly (month-end)
    
    Returns:
        DataFrame with date index and revenue values, or None if insufficient data.
    """
    date_col = col_map.get('date')
    rev_col = col_map.get('revenue')
    
    if not date_col or not rev_col:
        return None
    if date_col not in df.columns or rev_col not in df.columns:
        return None
    
    freq = _normalize_freq(freq)
    
    ts = df.groupby(pd.Grouper(key=date_col, freq=freq)).agg({rev_col: 'sum'}).reset_index()
    ts.columns = ['Date', 'Revenue']
    ts = ts.set_index('Date')
    ts = ts.asfreq(freq, fill_value=0)
    
    # Need at least 6 data points
    if len(ts) < 6:
        return None
    
    return ts


def train_test_split_ts(ts: pd.DataFrame, test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split time series into train and test sets chronologically."""
    split_idx = int(len(ts) * (1 - test_size))
    split_idx = max(3, split_idx)  # Ensure at least 3 training points
    train = ts.iloc[:split_idx]
    test = ts.iloc[split_idx:]
    return train, test


def moving_average_forecast(train: pd.DataFrame, test: pd.DataFrame, window: int = 3) -> pd.DataFrame:
    """Generate moving average baseline forecast."""
    last_values = train['Revenue'].iloc[-window:]
    ma_value = last_values.mean()
    
    forecast = pd.DataFrame(index=test.index)
    forecast['Predicted'] = ma_value
    forecast['Actual'] = test['Revenue']
    forecast['Model'] = 'Moving Average'
    
    return forecast


def exponential_smoothing_forecast(train: pd.DataFrame, test: pd.DataFrame,
                                    seasonal_periods: Optional[int] = None) -> pd.DataFrame:
    """Generate Holt-Winters / Exponential Smoothing forecast."""
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    
    train_values = train['Revenue']
    
    # Determine if we have enough data for seasonal model
    use_seasonal = False
    if seasonal_periods and len(train_values) >= 2 * seasonal_periods:
        use_seasonal = True
    
    try:
        if use_seasonal:
            model = ExponentialSmoothing(
                train_values,
                trend='add',
                seasonal='add',
                seasonal_periods=seasonal_periods,
                initialization_method='estimated'
            )
        else:
            model = ExponentialSmoothing(
                train_values,
                trend='add',
                seasonal=None,
                initialization_method='estimated'
            )
        
        fitted = model.fit(optimized=True)
        predictions = fitted.forecast(len(test))
        
        forecast = pd.DataFrame(index=test.index)
        forecast['Predicted'] = predictions.values
        forecast['Actual'] = test['Revenue'].values
        forecast['Model'] = 'Exponential Smoothing'
        
        return forecast
    
    except Exception:
        # Fallback to simple exponential smoothing
        try:
            from statsmodels.tsa.holtwinters import SimpleExpSmoothing
            model = SimpleExpSmoothing(train_values, initialization_method='estimated')
            fitted = model.fit(optimized=True)
            predictions = fitted.forecast(len(test))
            
            forecast = pd.DataFrame(index=test.index)
            forecast['Predicted'] = predictions.values
            forecast['Actual'] = test['Revenue'].values
            forecast['Model'] = 'Simple Exp. Smoothing'
            
            return forecast
        except Exception:
            return None


def calculate_metrics(actual: pd.Series, predicted: pd.Series) -> Dict[str, float]:
    """Calculate forecast evaluation metrics."""
    actual = actual.values
    predicted = predicted.values
    
    # Remove any NaN
    mask = ~(np.isnan(actual) | np.isnan(predicted))
    actual = actual[mask]
    predicted = predicted[mask]
    
    if len(actual) == 0:
        return {'MAE': 0, 'RMSE': 0, 'MAPE': 0}
    
    mae = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    
    # MAPE - avoid division by zero
    non_zero = actual != 0
    if non_zero.sum() > 0:
        mape = np.mean(np.abs((actual[non_zero] - predicted[non_zero]) / actual[non_zero])) * 100
    else:
        mape = 0
    
    return {
        'MAE': round(mae, 2),
        'RMSE': round(rmse, 2),
        'MAPE': round(mape, 2)
    }


def generate_future_forecast(ts: pd.DataFrame, periods: int = 3, freq: str = 'M',
                              seasonal_periods: Optional[int] = None) -> Optional[pd.DataFrame]:
    """Generate future forecast beyond available data."""
    from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing
    
    train_values = ts['Revenue']
    
    use_seasonal = False
    if seasonal_periods and len(train_values) >= 2 * seasonal_periods:
        use_seasonal = True
    
    try:
        if use_seasonal:
            model = ExponentialSmoothing(
                train_values,
                trend='add',
                seasonal='add',
                seasonal_periods=seasonal_periods,
                initialization_method='estimated'
            )
        else:
            model = ExponentialSmoothing(
                train_values,
                trend='add',
                seasonal=None,
                initialization_method='estimated'
            )
        
        fitted = model.fit(optimized=True)
        predictions = fitted.forecast(periods)
        
        # Generate confidence intervals (approximate)
        residuals = train_values - fitted.fittedvalues
        std_resid = residuals.std()
        
        future = pd.DataFrame({
            'Date': predictions.index,
            'Forecast': predictions.values,
            'Lower_CI': (predictions.values - 1.96 * std_resid),
            'Upper_CI': (predictions.values + 1.96 * std_resid)
        })
        future['Lower_CI'] = future['Lower_CI'].clip(lower=0)
        
        return future
    
    except Exception:
        try:
            model = SimpleExpSmoothing(train_values, initialization_method='estimated')
            fitted = model.fit(optimized=True)
            predictions = fitted.forecast(periods)
            
            residuals = train_values - fitted.fittedvalues
            std_resid = residuals.std()
            
            future = pd.DataFrame({
                'Date': predictions.index,
                'Forecast': predictions.values,
                'Lower_CI': (predictions.values - 1.96 * std_resid),
                'Upper_CI': (predictions.values + 1.96 * std_resid)
            })
            future['Lower_CI'] = future['Lower_CI'].clip(lower=0)
            
            return future
        except Exception:
            return None


def run_forecast_pipeline(df: pd.DataFrame, col_map: Dict, freq: str = 'ME') -> Dict:
    """Run the complete forecasting pipeline.
    
    Returns a dictionary with all forecast results.
    """
    results = {
        'success': False,
        'message': '',
        'time_series': None,
        'train': None,
        'test': None,
        'baseline_forecast': None,
        'model_forecast': None,
        'baseline_metrics': None,
        'model_metrics': None,
        'future_forecast': None,
    }
    
    # Normalize the frequency alias
    raw_freq = freq
    freq = _normalize_freq(freq)
    
    # 1. Prepare time series
    ts = prepare_time_series(df, col_map, freq=freq)
    if ts is None:
        results['message'] = 'Insufficient data for forecasting. Need a date and revenue column with at least 6 data points.'
        return results
    
    results['time_series'] = ts
    
    # 2. Train/test split
    train, test = train_test_split_ts(ts, test_size=0.2)
    results['train'] = train
    results['test'] = test
    
    if len(test) < 1:
        results['message'] = 'Not enough data points for train/test split.'
        return results
    
    # 3. Determine seasonal periods
    is_monthly = freq in ('ME', 'M', 'MS')
    is_daily = freq == 'D'
    seasonal_periods = 12 if is_monthly else (7 if is_daily else None)
    
    # 4. Baseline: Moving Average
    window = min(3, len(train))
    baseline = moving_average_forecast(train, test, window=window)
    results['baseline_forecast'] = baseline
    results['baseline_metrics'] = calculate_metrics(baseline['Actual'], baseline['Predicted'])
    
    # 5. Model: Exponential Smoothing
    model_fc = exponential_smoothing_forecast(train, test, seasonal_periods=seasonal_periods)
    if model_fc is not None:
        results['model_forecast'] = model_fc
        results['model_metrics'] = calculate_metrics(model_fc['Actual'], model_fc['Predicted'])
    
    # 6. Future forecast
    future_periods = 30 if is_daily else 3
    future = generate_future_forecast(ts, periods=future_periods, freq=freq,
                                       seasonal_periods=seasonal_periods)
    results['future_forecast'] = future
    
    results['success'] = True
    results['message'] = 'Forecasting completed successfully.'
    
    return results
