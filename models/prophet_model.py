from prophet import Prophet
import pandas as pd
import numpy as np

def forecast(df, periods=30):
    """
    Generate baseline forecast using Prophet
    """
    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True,
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10.0,
        interval_width=0.95
    )
    model.fit(df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast

def forecast_with_scenario(df, periods=30, scenario_config=None):
    """
    Generate forecast with What-If scenario applied
    
    Args:
        df: Historical data DataFrame with 'ds' and 'y' columns
        periods: Number of periods to forecast
        scenario_config: Dict with scenario parameters
            - type: 'spike', 'gradual', 'event'
            - magnitude: Percentage change (e.g., 10 for 10%)
            - start_day: Day to start applying scenario (1-based)
            - duration: Duration for gradual changes
            - recovery_days: Recovery period for events
    """
    if scenario_config is None:
        return forecast(df, periods)
    
    # Get baseline forecast
    baseline = forecast(df, periods)
    
    # Apply scenario modifications
    modified_forecast = baseline.copy()
    
    scenario_type = scenario_config.get('type', 'spike')
    magnitude = scenario_config.get('magnitude', 0) / 100  # Convert to decimal
    start_day = scenario_config.get('start_day', 1)
    duration = scenario_config.get('duration', 7)
    recovery_days = scenario_config.get('recovery_days', 5)
    
    # Calculate start index (accounting for historical data)
    start_index = len(df) + start_day - 1
    
    if start_index >= len(modified_forecast):
        return modified_forecast
    
    if scenario_type == 'spike':
        # One-time spike with exponential decay
        for i in range(start_index, len(modified_forecast)):
            days_after = i - start_index
            decay_factor = np.exp(-days_after / 10)
            base_price = baseline.loc[i, 'yhat']
            spike_amount = base_price * magnitude * decay_factor
            
            modified_forecast.loc[i, 'yhat'] += spike_amount
            modified_forecast.loc[i, 'yhat_lower'] += spike_amount * 0.8
            modified_forecast.loc[i, 'yhat_upper'] += spike_amount * 1.2
    
    elif scenario_type == 'gradual':
        # Gradual change over specified duration
        end_index = min(start_index + duration, len(modified_forecast))
        
        for i in range(start_index, end_index):
            progress = (i - start_index + 1) / duration
            current_change = magnitude * progress
            base_price = baseline.loc[i, 'yhat']
            
            modified_forecast.loc[i, 'yhat'] = base_price * (1 + current_change)
            modified_forecast.loc[i, 'yhat_lower'] = baseline.loc[i, 'yhat_lower'] * (1 + current_change * 0.8)
            modified_forecast.loc[i, 'yhat_upper'] = baseline.loc[i, 'yhat_upper'] * (1 + current_change * 1.2)
        
        # Maintain the change for remaining periods
        if end_index < len(modified_forecast):
            final_change = magnitude
            for i in range(end_index, len(modified_forecast)):
                base_price = baseline.loc[i, 'yhat']
                modified_forecast.loc[i, 'yhat'] = base_price * (1 + final_change)
                modified_forecast.loc[i, 'yhat_lower'] = baseline.loc[i, 'yhat_lower'] * (1 + final_change * 0.8)
                modified_forecast.loc[i, 'yhat_upper'] = baseline.loc[i, 'yhat_upper'] * (1 + final_change * 1.2)
    
    elif scenario_type == 'event':
        # Market event with recovery
        recovery_end = min(start_index + recovery_days, len(modified_forecast))
        
        for i in range(start_index, len(modified_forecast)):
            if i < recovery_end:
                # During recovery period
                recovery_progress = (i - start_index) / recovery_days
                current_change = magnitude * (1 - recovery_progress)
            else:
                # After recovery
                current_change = 0
            
            base_price = baseline.loc[i, 'yhat']
            modified_forecast.loc[i, 'yhat'] = base_price * (1 + current_change)
            modified_forecast.loc[i, 'yhat_lower'] = baseline.loc[i, 'yhat_lower'] * (1 + current_change * 0.8)
            modified_forecast.loc[i, 'yhat_upper'] = baseline.loc[i, 'yhat_upper'] * (1 + current_change * 1.2)
    
    return modified_forecast

class WhatIfAnalyzer:
    """
    Class to handle multiple What-If scenarios and comparisons
    """
    
    def __init__(self, historical_data):
        self.historical_data = historical_data
        self.baseline_forecast = None
        self.scenarios = {}
    
    def generate_baseline(self, periods=30):
        """Generate baseline forecast"""
        self.baseline_forecast = forecast(self.historical_data, periods)
        return self.baseline_forecast
    
    def add_scenario(self, name, scenario_config, periods=30):
        """Add a What-If scenario"""
        scenario_forecast = forecast_with_scenario(
            self.historical_data, 
            periods, 
            scenario_config
        )
        self.scenarios[name] = {
            'forecast': scenario_forecast,
            'config': scenario_config
        }
        return scenario_forecast
    
    def compare_scenarios(self, metrics=['final_price', 'max_price', 'min_price', 'volatility']):
        """Compare all scenarios against baseline"""
        if self.baseline_forecast is None:
            raise ValueError("Generate baseline forecast first")
        
        results = {}
        baseline_data = self.baseline_forecast['yhat']
        
        # Baseline metrics
        results['baseline'] = self._calculate_metrics(baseline_data, metrics)
        
        # Scenario metrics
        for name, scenario in self.scenarios.items():
            scenario_data = scenario['forecast']['yhat']
            results[name] = self._calculate_metrics(scenario_data, metrics)
            
            # Calculate differences from baseline
            results[name]['vs_baseline'] = {
                'final_price_diff': scenario_data.iloc[-1] - baseline_data.iloc[-1],
                'final_price_pct': ((scenario_data.iloc[-1] - baseline_data.iloc[-1]) / baseline_data.iloc[-1]) * 100
            }
        
        return results
    
    def _calculate_metrics(self, data, metrics):
        """Calculate specified metrics for forecast data"""
        result = {}
        
        if 'final_price' in metrics:
            result['final_price'] = data.iloc[-1]
        
        if 'max_price' in metrics:
            result['max_price'] = data.max()
        
        if 'min_price' in metrics:
            result['min_price'] = data.min()
        
        if 'volatility' in metrics:
            result['volatility'] = data.std()
        
        if 'avg_price' in metrics:
            result['avg_price'] = data.mean()
        
        return result
    
    def get_scenario_summary(self, scenario_name):
        """Get detailed summary of a specific scenario"""
        if scenario_name not in self.scenarios:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        
        scenario = self.scenarios[scenario_name]
        config = scenario['config']
        forecast_data = scenario['forecast']['yhat']
        
        summary = {
            'name': scenario_name,
            'type': config.get('type', 'unknown'),
            'magnitude': config.get('magnitude', 0),
            'start_day': config.get('start_day', 1),
            'final_price': forecast_data.iloc[-1],
            'max_impact': forecast_data.max(),
            'min_impact': forecast_data.min(),
            'description': self._generate_description(config)
        }
        
        return summary
    
    def _generate_description(self, config):
        """Generate human-readable description of scenario"""
        scenario_type = config.get('type', 'spike')
        magnitude = config.get('magnitude', 0)
        start_day = config.get('start_day', 1)
        
        descriptions = {
            'spike': f"{abs(magnitude)}% {'spike' if magnitude > 0 else 'drop'} on day {start_day} with recovery",
            'gradual': f"Gradual {abs(magnitude)}% {'increase' if magnitude > 0 else 'decrease'} over {config.get('duration', 7)} days",
            'event': f"Market event: {abs(magnitude)}% {'positive' if magnitude > 0 else 'negative'} impact with {config.get('recovery_days', 5)}-day recovery"
        }
        
        return descriptions.get(scenario_type, "Custom scenario")

# Utility functions for common scenarios
def create_market_crash_scenario(crash_percent=-20, start_day=5, recovery_days=14):
    """Create a market crash scenario"""
    return {
        'type': 'event',
        'magnitude': crash_percent,
        'start_day': start_day,
        'recovery_days': recovery_days
    }

def create_earnings_beat_scenario(surprise_percent=15, start_day=10):
    """Create an earnings beat scenario"""
    return {
        'type': 'spike',
        'magnitude': surprise_percent,
        'start_day': start_day
    }

def create_sector_rotation_scenario(rotation_percent=8, duration=20, start_day=1):
    """Create a sector rotation scenario"""
    return {
        'type': 'gradual',
        'magnitude': rotation_percent,
        'start_day': start_day,
        'duration': duration
    }