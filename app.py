import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scripts.process_data import clean_data
from models.prophet_model import forecast
import numpy as np

st.set_page_config(page_title="Predictive Analytics Dashboard", layout="wide")

st.title("📈 Predictive Stock Forecast Dashboard")

# Main controls
col1, col2 = st.columns([2, 1])

with col1:
    symbol = st.selectbox("Select Stock Symbol", ["AAPL", "MSFT", "GOOGL", "TSLA"])
    fullname_symbol = {"AAPL": "Apple Inc.", "MSFT": "Microsoft Corp.", "GOOGL": "Alphabet Inc.", "TSLA": "Tesla Inc."}
    name = fullname_symbol.get(symbol, "Unknown Company")
    days = st.slider("Forecast Days", 7, 90, 30)

# What-If Analysis Sidebar
st.sidebar.header("📊 What-If Analysis")
st.sidebar.markdown("Simulate hypothetical scenarios and see their impact on forecasted prices.")

# What-If Controls
whatif_enabled = st.sidebar.checkbox("Enable What-If Analysis", value=True)

if whatif_enabled:
    spike_percent = st.sidebar.slider(
        "Price Change (%)", 
        min_value=-50, 
        max_value=50, 
        value=0, 
        step=1,
        help="Positive values simulate price increases, negative values simulate drops"
    )
    
    spike_day_offset = st.sidebar.slider(
        "Apply Change on Day", 
        min_value=1, 
        max_value=days, 
        value=max(1, days//2),
        help="Day in the forecast period to apply the price change"
    )
    
    # Scenario type selection
    scenario_type = st.sidebar.selectbox(
        "Scenario Type",
        ["One-time Spike/Drop", "Gradual Change", "Market Event"],
        help="Choose how the price change should be applied"
    )
    
    # Additional parameters based on scenario type
    if scenario_type == "Gradual Change":
        duration = st.sidebar.slider(
            "Change Duration (Days)",
            min_value=1,
            max_value=min(30, days),
            value=7,
            help="Number of days over which the change occurs"
        )
    elif scenario_type == "Market Event":
        recovery_days = st.sidebar.slider(
            "Recovery Period (Days)",
            min_value=1,
            max_value=min(14, days - spike_day_offset),
            value=5,
            help="Days for price to recover after the event"
        )

# Load and process data
try:
    file_path = f"data/raw/{symbol}_daily.csv"
    df = clean_data(file_path)
    predicted = forecast(df, periods=days)
    
    # Create What-If forecast if enabled
    if whatif_enabled and spike_percent != 0:
        # Create a copy of the baseline forecast
        modified_forecast = predicted.copy()
        
        # Apply the scenario based on type
        if scenario_type == "One-time Spike/Drop":
            # Apply spike to a single day and let it propagate
            spike_index = spike_day_offset - 1 + len(df)  # Adjust for historical data
            if spike_index < len(modified_forecast):
                base_price = modified_forecast.loc[spike_index, 'yhat']
                spike_amount = base_price * (spike_percent / 100)
                
                # Apply spike and gradual normalization
                for i in range(spike_index, len(modified_forecast)):
                    days_after = i - spike_index
                    decay_factor = np.exp(-days_after / 10)  # Exponential decay
                    modified_forecast.loc[i, 'yhat'] += spike_amount * decay_factor
                    modified_forecast.loc[i, 'yhat_lower'] += spike_amount * decay_factor * 0.8
                    modified_forecast.loc[i, 'yhat_upper'] += spike_amount * decay_factor * 1.2
        
        elif scenario_type == "Gradual Change":
            # Apply gradual change over specified duration
            start_index = spike_day_offset - 1 + len(df)
            end_index = min(start_index + duration, len(modified_forecast))
            
            for i in range(start_index, end_index):
                progress = (i - start_index + 1) / duration
                current_change = spike_percent * progress / 100
                base_price = predicted.loc[i, 'yhat']
                
                modified_forecast.loc[i, 'yhat'] = base_price * (1 + current_change)
                modified_forecast.loc[i, 'yhat_lower'] = predicted.loc[i, 'yhat_lower'] * (1 + current_change * 0.8)
                modified_forecast.loc[i, 'yhat_upper'] = predicted.loc[i, 'yhat_upper'] * (1 + current_change * 1.2)
        
        elif scenario_type == "Market Event":
            # Apply sudden change with recovery
            start_index = spike_day_offset - 1 + len(df)
            recovery_end = min(start_index + recovery_days, len(modified_forecast))
            
            for i in range(start_index, len(modified_forecast)):
                if i < recovery_end:
                    # During recovery period
                    recovery_progress = (i - start_index) / recovery_days
                    current_change = spike_percent * (1 - recovery_progress) / 100
                else:
                    # After recovery
                    current_change = 0
                
                base_price = predicted.loc[i, 'yhat']
                modified_forecast.loc[i, 'yhat'] = base_price * (1 + current_change)
                modified_forecast.loc[i, 'yhat_lower'] = predicted.loc[i, 'yhat_lower'] * (1 + current_change * 0.8)
                modified_forecast.loc[i, 'yhat_upper'] = predicted.loc[i, 'yhat_upper'] * (1 + current_change * 1.2)

    # Create the main chart
    fig = go.Figure()
    
    # Add historical data
    fig.add_trace(go.Scatter(
        x=df['ds'], 
        y=df['y'], 
        name='Historical Data',
        line=dict(color='blue', width=2),
        hovertemplate='Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
    ))
    
    # Add baseline forecast
    fig.add_trace(go.Scatter(
        x=predicted['ds'], 
        y=predicted['yhat'], 
        name='Baseline Forecast',
        line=dict(color='green', width=2),
        hovertemplate='Date: %{x}<br>Forecast: $%{y:.2f}<extra></extra>'
    ))
    
    # Add confidence intervals for baseline
    fig.add_trace(go.Scatter(
        x=predicted['ds'],
        y=predicted['yhat_upper'],
        fill=None,
        mode='lines',
        line_color='rgba(0,100,80,0)',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=predicted['ds'],
        y=predicted['yhat_lower'],
        fill='tonexty',
        mode='lines',
        line_color='rgba(0,100,80,0)',
        name='Confidence Interval',
        fillcolor='rgba(0,100,80,0.2)',
        hovertemplate='Date: %{x}<br>Lower: $%{y:.2f}<extra></extra>'
    ))
    
    # Add What-If forecast if enabled
    if whatif_enabled and spike_percent != 0:
        fig.add_trace(go.Scatter(
            x=modified_forecast['ds'], 
            y=modified_forecast['yhat'], 
            name='What-If Forecast',
            line=dict(color='red', width=2, dash='dash'),
            hovertemplate='Date: %{x}<br>What-If: $%{y:.2f}<extra></extra>'
        ))
    
    # Update layout
    fig.update_layout(
        title=f"{name} Stock Forecast with What-If Analysis",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=600,
        showlegend=True,
        hovermode='x unified'
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Display metrics and analysis
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_price = df['y'].iloc[-1]
        st.metric(
            label="Current Price",
            value=f"${current_price:.2f}"
        )
    
    with col2:
        baseline_final = predicted['yhat'].iloc[-1]
        baseline_change = ((baseline_final - current_price) / current_price) * 100
        st.metric(
            label="Baseline Forecast",
            value=f"${baseline_final:.2f}",
            delta=f"{baseline_change:.1f}%"
        )
    
    with col3:
        if whatif_enabled and spike_percent != 0:
            whatif_final = modified_forecast['yhat'].iloc[-1]
            whatif_change = ((whatif_final - current_price) / current_price) * 100
            delta_vs_baseline = whatif_final - baseline_final
            st.metric(
                label="What-If Forecast",
                value=f"${whatif_final:.2f}",
                delta=f"${delta_vs_baseline:.2f} vs baseline"
            )
        else:
            st.metric(
                label="What-If Forecast",
                value="Disabled",
                delta="Enable to see impact"
            )
    
    # Analysis summary
    if whatif_enabled and spike_percent != 0:
        st.subheader("📋 Scenario Analysis Summary")
        
        impact_amount = modified_forecast['yhat'].iloc[-1] - predicted['yhat'].iloc[-1]
        impact_percent = (impact_amount / predicted['yhat'].iloc[-1]) * 100
        
        scenario_desc = {
            "One-time Spike/Drop": f"a {abs(spike_percent)}% {'spike' if spike_percent > 0 else 'drop'} on day {spike_day_offset} with exponential recovery",
            "Gradual Change": f"a gradual {abs(spike_percent)}% {'increase' if spike_percent > 0 else 'decrease'} over {duration if 'duration' in locals() else 0} days starting on day {spike_day_offset}",
            "Market Event": f"a {abs(spike_percent)}% {'positive' if spike_percent > 0 else 'negative'} market event on day {spike_day_offset} with {recovery_days if 'recovery_days' in locals() else 0}-day recovery"
        }
        
        st.write(f"**Scenario:** {scenario_desc[scenario_type]}")
        st.write(f"**Final Impact:** ${impact_amount:.2f} ({impact_percent:+.1f}%) difference from baseline forecast")
        
        if abs(impact_percent) > 5:
            st.warning(f"⚠️ This scenario shows a significant {abs(impact_percent):.1f}% impact on the final forecast price.")
        elif abs(impact_percent) > 2:
            st.info(f"ℹ️ This scenario shows a moderate {abs(impact_percent):.1f}% impact on the final forecast price.")
        else:
            st.success(f"✅ This scenario shows a minor {abs(impact_percent):.1f}% impact on the final forecast price.")

except FileNotFoundError:
    st.error(f"Data file not found for {symbol}. Please ensure the data file exists at: {file_path}")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check your data files and model configuration.")

# Help section
with st.expander("ℹ️ How to use What-If Analysis"):
    st.markdown("""
    **What-If Analysis** allows you to simulate different market scenarios and see their impact on stock price forecasts:
    
    1. **Enable What-If Analysis** in the sidebar
    2. **Set Price Change (%)**: Choose how much the price should change (positive for increases, negative for drops)
    3. **Select Application Day**: Choose when in the forecast period the change should occur
    4. **Choose Scenario Type**:
       - **One-time Spike/Drop**: Sudden change with gradual recovery
       - **Gradual Change**: Slow change over several days
       - **Market Event**: Sudden change with defined recovery period
    5. **Compare Results**: The red dashed line shows your scenario vs. the green baseline forecast
    
    Use this to test questions like:
    - "What if there's a 10% market crash next week?"
    - "How would a gradual 5% increase over 10 days affect the forecast?"
    - "What's the impact of a major announcement causing a 15% spike?"
    """)