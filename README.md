# 📈 AgenticAI Stock Insights

An intelligent web application that predicts future stock trends and generates human-readable insights — combining **data science** and **AI-powered language models** into one interactive dashboard.

---

## 🚀 Overview

This project uses **Flask**, **Plotly**, and **LLM agents** to forecast stock prices and summarize insights in natural language.  
It allows users to input any stock ticker (e.g., AAPL, TSLA) and receive:
- 📊 **Forecasted stock prices** for upcoming days  
- 🧠 **AI-generated explanations** of market trends  
- 🌐 **Interactive visualization** of historical vs. predicted data

The app functions like an **AI financial analyst**, turning raw market data into actionable insights.

---

## 🧩 System Architecture

User → Frontend (HTML/JS)
↓
Flask App (app.py)
↓
┌─────────────────────┐
│ Forecast Agent │ → Predicts future stock prices
│ (forecast_agent.py) │
└─────────────────────┘
↓
┌─────────────────────┐
│ Insight Agent │ → Generates natural-language summary
│ (insights.py) │
└─────────────────────┘
↓
Interactive Chart + Report


---

## ⚙️ Features

✅ Forecasts future stock prices using machine learning  
✅ Generates textual insights powered by AI models  
✅ Fetches real-time historical data via **Yahoo Finance API**  
✅ Interactive **Plotly charts** for visual analysis  
✅ Simple and responsive frontend (HTML, CSS, JS)  
✅ Modular agent-based design for scalability  

---

## 🧠 Logical Flow

### 1️⃣ `app.py` — The Controller  
- Handles Flask routing and user input.  
- Connects user queries to backend agents.  
- Combines forecast results + insights into a clean dashboard.

### 2️⃣ `forecast_agent.py` — The Prediction Brain  
- Extracts stock symbol and prediction days from user prompt.  
- Fetches historical stock data using **Yahoo Finance**.  
- Runs time-series forecasting to project future prices.  
- Returns structured forecast data and historical trends.

### 3️⃣ `insights.py` — The Explanation Brain  
- Takes the forecast output or user query.  
- Uses a **language model (LLM)** to write concise, human-readable insights.  
- Explains why the forecast behaves a certain way (trend analysis, possible reasons, etc.).

### 4️⃣ Frontend (HTML + CSS + JS)  
- Provides a clean UI to enter prompts and view results.  
- Displays Plotly charts for visual comparison.  
- Shows tabular forecast and AI-generated textual summary.

---

## 🖼️ Sample Output

### 📊 Forecast Visualization
An interactive chart displaying:
- Blue Line → Historical stock prices  
- Orange Line → Forecasted prices for future days  

### 🧾 AI Insight Example
> “Tesla stock shows an upward momentum driven by consistent volume growth.  
> The model predicts moderate gains over the next 10 days, reflecting a bullish short-term outlook.”

---

## 🧰 Tech Stack

| Component | Technology Used |
|------------|----------------|
| Backend | Flask (Python) |
| Forecasting | Prophet / Time-series model |
| Data Source | Yahoo Finance API |
| Visualization | Plotly |
| AI Insights | LLM (e.g., Hugging Face / OpenAI) |
| Frontend | HTML, CSS, JavaScript |


## Example Prompts

Try these queries on the homepage:

“Predict Tesla stock for the next 10 days”

“Forecast Apple share prices for 1 week”

“Explain Microsoft stock performance this month”

##🌟 Future Enhancements

🔍 Add sentiment analysis from financial news

📱 Mobile-optimized responsive layout

💬 Support for multiple tickers comparison

📈 Integration with live trading dashboards

🧩 LLM fine-tuning for domain-specific stock insights
