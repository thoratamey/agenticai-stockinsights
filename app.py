# app.py

from flask import Flask, render_template, request
from yahooquery import Ticker
import pandas as pd
import plotly.graph_objects as go
from src.forecast_agent import stock_forecast_agent, stock_insight_agent
from src.insights import run_stock_agent
import os

# Suppress warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

app = Flask(__name__)

# ----------------------------
# Route 1: Home Page
# ----------------------------
@app.route("/")
def home():
    return render_template("home.html")


# ----------------------------
# Route 2: Forecast Page
# ----------------------------
@app.route("/forecast", methods=["GET", "POST"])
def forecast():
    forecast_data = None
    plot_html = None
    error = None
    insights_text = None

    if request.method == "POST":
        user_prompt = request.form.get("prompt")

        if user_prompt:
            try:
                # Run forecasting agent
                df_forecast, df_historical_data, arguments = stock_forecast_agent(prompt=user_prompt)
                stock_symbol = arguments["stock_symbol"]
                prediction_days = arguments.get("prediction_days", 10)

                # Create forecast dates
                last_date = pd.to_datetime(df_historical_data['ds'].iloc[-1])
                forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=prediction_days)

                # Plotly chart
                fig = go.Figure()

                # Historical data
                fig.add_trace(go.Scatter(
                    x=df_historical_data['ds'],
                    y=df_historical_data['y'],
                    mode='lines',
                    name='Historical Price',
                    line=dict(color='blue')
                ))

                # Forecast median
                fig.add_trace(go.Scatter(
                    x=forecast_dates,
                    y=df_forecast['forecast_median'],
                    mode='lines',
                    name='Median Forecast',
                    line=dict(color='orange')
                ))

                # Forecast range
                fig.add_trace(go.Scatter(
                    x=forecast_dates.tolist() + forecast_dates[::-1].tolist(),
                    y=df_forecast['forecast_high'].tolist() + df_forecast['forecast_lower'][::-1].tolist(),
                    fill='toself',
                    name='Forecast Range (Low-High)',
                    fillcolor='rgba(255,165,0,0.3)',
                    line=dict(color='rgba(255,165,0,0)')
                ))

                # Layout
                fig.update_layout(
                    title=f"{stock_symbol} Historical Data and Forecast",
                    xaxis_title="Date",
                    yaxis_title="Price",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    template="plotly_white"
                )

                # Convert chart to HTML
                plot_html = fig.to_html(full_html=False)

                # Prepare forecast data for table
                df_forecast['date'] = forecast_dates
                forecast_data = df_forecast[['ticker', 'date', 'forecast_median', 'forecast_lower', 'forecast_high']].to_dict(orient="records")

                # Generate insights
                insights_text = stock_insight_agent(stock_symbol, df_historical_data, df_forecast)

            except Exception as e:
                error = str(e)

    return render_template(
        "forecast.html",
        plot_html=plot_html,
        forecast_data=forecast_data,
        insights_text=insights_text,
        error=error
    )


# ----------------------------
# Route 3: Insights Page
# ----------------------------
@app.route("/insights", methods=["GET", "POST"])
def insights():
    insight = None
    error = None

    if request.method == "POST":
        user_query = request.form.get("prompt")
        if user_query:
            try:
                insight = run_stock_agent(user_query)
            except Exception as e:
                error = str(e)

    return render_template("insights.html", insight=insight, error=error)


# ----------------------------
# Run the app
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)
