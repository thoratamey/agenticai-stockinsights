# src/insights.py

import os
from yahooquery import Ticker
from langchain.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# 🔐 Keep your OpenAI API key here only
OPENAI_API_KEY = ""
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, api_key=OPENAI_API_KEY)

# ------------------ Tool Definition ------------------
def get_stock_insight(ticker: str) -> str:
    """Fetch stock data using yahooquery and return summarized insights."""
    try:
        t = Ticker(ticker)
        summary = t.summary_detail.get(ticker, {})
        financials = t.financial_data.get(ticker, {})
        profile = t.asset_profile.get(ticker, {})

        if not summary:
            return f"⚠️ No summary data found for {ticker}. Try again later."

        insights = {
            "Company Summary": profile.get("longBusinessSummary", "N/A"),
            "Market Cap": summary.get("marketCap", "N/A"),
            "PE Ratio": summary.get("trailingPE", "N/A"),
            "Dividend Yield": summary.get("dividendYield", "N/A"),
            "Price to Book": summary.get("priceToBook", "N/A"),
            "Revenue Growth": financials.get("revenueGrowth", "N/A"),
        }

        formatted = "\n".join([f"{k}: {v}" for k, v in insights.items()])
        return f"📊 Insights for {ticker}:\n\n{formatted}"
        return insight
    except Exception as e:
        return f"❌ Error fetching data: {e}"

# Define LangChain Tool
stock_tool = Tool(
    name="StockInsightTool",
    func=get_stock_insight,
    description="Fetches insights for a given stock ticker symbol using Yahoo Finance data via yahooquery."
)

tools = [stock_tool]

# ------------------ FIXED Prompt Template ------------------
prompt = PromptTemplate.from_template(
    """
You are an Agentic Financial Data Analyst.
Your job is to analyze stock symbols and fetch insights using the tools provided.

You have access to the following tools:
{tools}

Tool names you can call: {tool_names}

Use this reasoning format step-by-step:

Question: the user's input
Thought: what you are thinking
Action: the tool name (e.g., StockInsightTool)
Action Input: the ticker symbol
Observation: result of the tool
Final Answer: concise summary for the user

Question: {input}
{agent_scratchpad}
"""
)



# ------------------ Agent Setup ------------------
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# ------------------ Function for Flask ------------------
def run_stock_agent(query: str):
    """Run the LangChain agent and return its final output."""
    result = executor.invoke({"input": query})
    return result.get("output", "⚠️ No insight generated.")
