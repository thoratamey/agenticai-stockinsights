import requests
import json
import torch
from chronos import ChronosPipeline
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from yahooquery import Ticker
from typing import Dict, Tuple
import os

# Disable HuggingFace symlink warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Force CPU on Windows
device = "cpu"


# --------------------------------------------------------------------------
# 1️⃣ FORECAST FUNCTION
# --------------------------------------------------------------------------
def get_stock_forecast(stock_symbol: str, prediction_days: int = 10) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Forecast stock prices using Chronos model and Yahoo data."""

    # Fetch historical data
    ticker_data = Ticker(stock_symbol)
    hist_df = ticker_data.history(period="1y", interval="1d")

    if hist_df.empty:
        raise ValueError(f"No historical data found for {stock_symbol}")

    # Prepare historical dataframe
    df_historical_data = hist_df.reset_index()
    df_historical_data = df_historical_data.rename(columns={"date": "ds", "close": "y"})
    df_historical_data = df_historical_data[["ds", "y"]].copy()
    df_historical_data['unique_id'] = stock_symbol

    # Load Chronos model
    pipeline = ChronosPipeline.from_pretrained(
        "amazon/chronos-t5-small",
        device_map=device,
        torch_dtype=torch.bfloat16,
    )

    # Prepare input
    historical_data = df_historical_data['y'].tolist()
    context = torch.tensor(historical_data, dtype=torch.float32)

    # Predict
    forecasts = pipeline.predict(context, prediction_days)

    # Convert to DataFrame
    df_forecast = pd.DataFrame()
    for ts_key, forecast in zip([stock_symbol], forecasts):
        low, median, high = np.quantile(forecast.numpy(), [0.1, 0.5, 0.9], axis=0)
        df_forecast = pd.DataFrame({
            'forecast_lower': low,
            'forecast_median': median,
            'forecast_high': high,
            'ticker': ts_key
        })

    return df_forecast, df_historical_data


# --------------------------------------------------------------------------
# 2️⃣ FORECAST AGENT (LLM to parse user prompt)
# --------------------------------------------------------------------------
def stock_forecast_agent(prompt: str) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
    """Uses OpenAI GPT model to extract stock symbol and forecast duration from user prompt."""

    api_key = ""
    endpoint = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Define structured output schema
    function_schema = {
        "name": "get_stock_forecast",
        "description": "Get stock price forecast for a given number of days",
        "parameters": {
            "type": "object",
            "properties": {
                "stock_symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol, e.g. 'AAPL', 'TSLA'."
                },
                "prediction_days": {
                    "type": "integer",
                    "description": "Number of days to forecast ahead."
                }
            },
            "required": ["stock_symbol"]
        }
    }

    messages = [
        {"role": "user", "content": prompt}
    ]

    data = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "functions": [function_schema],
        "function_call": "auto"
    }

    # Send request
    response = requests.post(endpoint, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        raise RuntimeError(f"OpenAI API request failed ({response.status_code}): {response.text}")

    result = response.json()
    function_call = result["choices"][0].get("message", {}).get("function_call")

    if not function_call:
        raise ValueError(result["choices"][0]["message"]["content"])

    arguments = json.loads(function_call["arguments"])
    stock_symbol = arguments["stock_symbol"]
    prediction_days = arguments.get("prediction_days", 10)

    # Generate forecast using Chronos
    df_forecast, df_historical_data = get_stock_forecast(stock_symbol, prediction_days)

    return df_forecast, df_historical_data, arguments


# --------------------------------------------------------------------------
# 3️⃣ INSIGHT AGENT (LLM to generate textual insights)
# --------------------------------------------------------------------------
def stock_insight_agent(stock_symbol: str, df_historical: pd.DataFrame, df_forecast: pd.DataFrame) -> str:
    """Generates professional stock insights using GPT based on forecast + historical data."""

    api_key = ""
    endpoint = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Prepare compact summaries
    recent_prices = df_historical['y'].tail(30).tolist()
    forecast_median = df_forecast['forecast_median'].tolist()
    forecast_high = df_forecast['forecast_high'].tolist()
    forecast_low = df_forecast['forecast_lower'].tolist()

    messages = [
        {
            "role": "system",
            "content": "You are an experienced financial market analyst generating AI-based insights."
        },
        {
            "role": "user",
            "content": (
                f"Analyze stock {stock_symbol} using the following data:\n"
                f"Recent historical closing prices (last 30 days): {recent_prices}\n"
                f"Forecasted median prices: {forecast_median}\n"
                f"Forecasted high prices: {forecast_high}\n"
                f"Forecasted low prices: {forecast_low}\n\n"
                "Generate a short analytical report (3–5 sentences) including:\n"
                "- Trend direction (upward/downward/stable)\n"
                "- Short-term buy/sell/hold recommendation\n"
                "- Volatility and confidence assessment\n"
                "- Short-term risk or cautionary note"
            )
        }
    ]

    data = {
        "model": "gpt-4o-mini",
        "messages": messages
    }

    response = requests.post(endpoint, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        raise RuntimeError(f"OpenAI API request failed ({response.status_code}): {response.text}")

    result = response.json()
    insights_text = result["choices"][0]["message"]["content"].strip()

    return insights_text
