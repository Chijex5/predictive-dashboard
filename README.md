# 📈 Predictive Stock Forecast Dashboard

A powerful, interactive Streamlit dashboard for stock price forecasting with advanced What-If analysis capabilities. This application combines historical stock data analysis with predictive modeling to help users understand potential future price movements and test various market scenarios.

## ✨ Features

### 🎯 Core Functionality
- **Real-time Stock Forecasting**: Generate predictions for AAPL, MSFT, GOOGL, and TSLA
- **Flexible Forecast Periods**: Predict anywhere from 7 to 90 days into the future
- **Interactive Visualizations**: Beautiful, responsive charts with hover details
- **Confidence Intervals**: Visual representation of forecast uncertainty

### 🔮 What-If Analysis Engine
The dashboard's standout feature is its sophisticated What-If analysis system that allows users to simulate various market scenarios:

#### Scenario Types
1. **One-time Spike/Drop**
   - Simulate sudden price movements with exponential recovery
   - Perfect for testing impact of earnings announcements, breaking news, or market shocks

2. **Gradual Change**
   - Model slow, sustained price movements over time
   - Ideal for analyzing long-term trends or gradual market shifts

3. **Market Event**
   - Simulate major market events with defined recovery periods
   - Great for testing resilience against market crashes or boom cycles

#### Customizable Parameters
- **Price Change**: Adjust impact from -50% to +50%
- **Timing Control**: Choose exactly when the scenario occurs
- **Duration Settings**: Control how long effects last
- **Recovery Modeling**: Define bounce-back periods for market events

### 📊 Interactive Dashboard Elements
- **Real-time Metrics**: Current price, baseline forecast, and What-If comparisons
- **Smart Alerts**: Automatic warnings for significant forecast deviations
- **Scenario Comparison**: Side-by-side baseline vs. What-If analysis
- **Impact Analysis**: Detailed breakdown of scenario effects

## 🛠️ Technical Stack

- **Frontend**: Streamlit for interactive web interface
- **Visualization**: Plotly for dynamic, responsive charts
- **Data Processing**: Pandas for efficient data manipulation
- **Forecasting**: Prophet model for time series prediction
- **Numerical Computing**: NumPy for mathematical operations

## 📁 Project Structure

```
predictive-dashboard/
├── app.py                 # Main Streamlit application
├── data/
│   └── raw/
│       ├── AAPL_daily.csv
│       ├── GOOGL_daily.csv
│       ├── MSFT_daily.csv
│       └── TSLA_daily.csv
├── models/
│   └── prophet_model.py   # Forecasting model implementation
├── scripts/
│   ├── fetch_data.py      # Data acquisition scripts
│   ├── process_data.py    # Data cleaning and preprocessing
│   └── update_data.py     # Data refresh utilities
|── utils/
|   └── config.py          # Configuration settings
|
└── requirements.txt
```

## 🚀 Getting Started

### Prerequisites
```bash
pip install -r requirements.txt
```

### Installation
1. Clone this repository
2. Install required dependencies
3. Ensure your data files are in the `data/raw/` directory
4. Run the application:
   ```bash
   streamlit run app.py
   ```

### Data Requirements
The dashboard expects CSV files with daily stock data containing:
- Date column (`ds`)
- Price column (`y`)
- Standard OHLCV format is recommended

## 🎮 How to Use

### Basic Forecasting
1. **Select Stock**: Choose from AAPL, MSFT, GOOGL, or TSLA
2. **Set Forecast Period**: Use the slider to choose 7-90 days
3. **View Results**: Analyze the baseline forecast and confidence intervals

### What-If Analysis
1. **Enable Analysis**: Check "Enable What-If Analysis" in the sidebar
2. **Configure Scenario**:
   - Set price change percentage (-50% to +50%)
   - Choose when the change occurs
   - Select scenario type (Spike/Drop, Gradual, Market Event)
3. **Compare Results**: View the red dashed line against the green baseline
4. **Analyze Impact**: Review the detailed scenario summary

### Example Use Cases
- **Earnings Season**: "What if AAPL drops 8% after earnings on day 15?"
- **Market Volatility**: "How would a gradual 12% increase over 2 weeks affect TSLA?"
- **Black Swan Events**: "What's the impact of a 25% market crash with 7-day recovery?"

## 📈 Understanding the Visualizations

### Chart Elements
- **Blue Line**: Historical stock prices
- **Green Line**: Baseline forecast without scenarios
- **Red Dashed Line**: What-If forecast with applied scenarios
- **Shaded Area**: Confidence intervals showing forecast uncertainty

### Metrics Panel
- **Current Price**: Last known trading price
- **Baseline Forecast**: Predicted price without scenarios
- **What-If Forecast**: Predicted price with scenario applied
- **Delta Values**: Change indicators and comparisons

## 🔧 Customization Options

### Adding New Stocks
1. Add stock data CSV to `data/raw/`
2. Update the `symbol` selectbox in `app.py`
3. Add company name to `fullname_symbol` dictionary

### Extending Scenarios
The What-If engine is designed for easy expansion:
- Add new scenario types in the `scenario_type` selectbox
- Implement scenario logic in the main processing loop
- Customize mathematical models for different market behaviors

## 🎯 Key Benefits

### For Traders & Investors
- **Risk Assessment**: Test portfolio resilience against various scenarios
- **Entry/Exit Planning**: Optimize timing based on forecast analysis
- **Scenario Planning**: Prepare for different market conditions

### For Analysts & Researchers
- **Model Validation**: Compare forecast accuracy across different conditions
- **Sensitivity Analysis**: Understand how external factors affect predictions
- **Hypothesis Testing**: Validate market theories with simulated data

### For Educators & Students
- **Interactive Learning**: Hands-on experience with financial forecasting
- **Scenario Simulation**: Understand market dynamics through experimentation
- **Visual Analytics**: Learn from intuitive, interactive visualizations

## ⚠️ Important Notes

### Limitations
- Forecasts are based on historical patterns and may not predict unprecedented events
- What-If scenarios are simulations and should not be used as sole investment guidance
- Model accuracy depends on data quality and market conditions

### Best Practices
- Use multiple scenario types to test robustness
- Combine with fundamental analysis for better insights
- Regularly update data for accurate forecasting
- Consider external factors not captured in historical data

## 🤝 Contributing

We welcome contributions! Areas for improvement:
- Additional forecasting models
- New scenario types
- Enhanced visualization options
- Performance optimizations
- Extended stock universe

## 📄 License

This project is available under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Streamlit for rapid prototyping
- Powered by Facebook's Prophet for robust forecasting
- Visualizations created with Plotly for interactive charts

---

**Ready to forecast the future?** 🚀 Launch the dashboard and start exploring What-If scenarios today!