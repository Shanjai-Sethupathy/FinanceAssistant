import logging
from typing import List, Dict
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# Assuming you have an APIAgent (like the AlphaVantageAgent) to fetch data
class AlphaVantageAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def _fetch_data(self, function: str, symbol: str, params: dict = {}) -> pd.DataFrame:
        import requests
        base_url = "https://www.alphavantage.co/query"
        payload = {"function": function, "symbol": symbol, "apikey": self.api_key, **params}
        try:
            response = requests.get(base_url, params=payload)
            response.raise_for_status()
            data = response.json()

            if "Error Message" in data:
                raise ValueError(f"Alpha Vantage API Error: {data['Error Message']}")

            if function in ["TIME_SERIES_DAILY", "TIME_SERIES_WEEKLY", "TIME_SERIES_MONTHLY"]:
                time_series_key = list(data.keys())[1]
                if time_series_key not in data:
                    raise KeyError(f"Key '{time_series_key}' not found in Alpha Vantage response.")
                df = pd.DataFrame.from_dict(data[time_series_key], orient='index')
                df.index = pd.to_datetime(df.index)
                df.columns = ["open", "high", "low", "close", "volume"]
                df = df.astype(float)
                return df
            elif function == "GLOBAL_QUOTE":
                if "Global Quote" not in data:
                    raise KeyError("'Global Quote' not found in Alpha Vantage response.")
                quote_data = data["Global Quote"]
                df = pd.DataFrame([quote_data])
                df = df.rename(columns={
                    "01. symbol": "symbol",
                    "02. open": "open",
                    "03. high": "high",
                    "04. low": "low",
                    "05. price": "price",
                    "06. volume": "volume",
                    "07. latest trading day": "latest_trading_day",
                    "08. previous close": "previous_close",
                    "09. change": "change",
                    "10. change percent": "change_percent"
                })
                df['latest_trading_day'] = pd.to_datetime(df['latest_trading_day'])
                return df
            else:
                return pd.DataFrame(data)
        except requests.exceptions.RequestException as e:
            raise  # Re-raise the exception to be caught by the caller
        except KeyError as e:
            raise
        except ValueError as e:
            raise

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisAgent:
    def __init__(self, api_agent: AlphaVantageAgent):
        self.api_agent = api_agent

    def _get_historical_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        try:
            df = self.api_agent._fetch_data(function="TIME_SERIES_DAILY", symbol=symbol, params={"outputsize": "full"})
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            return df
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()

    def _get_latest_quote(self, symbol: str) -> pd.DataFrame:
        try:
            df = self.api_agent._fetch_data(function="GLOBAL_QUOTE", symbol=symbol)
            return df
        except Exception as e:
            logger.error(f"Error fetching latest quote for {symbol}: {e}")
            return pd.DataFrame()

    def analyze_risk_exposure(self, stock_list: List[str], allocation_data: pd.DataFrame) -> dict:
        try:
            historical_data = {}
            for symbol in stock_list:
                historical_data[symbol] = self._get_historical_data(symbol)
                if historical_data[symbol].empty:
                    logger.warning(f"No data available for symbol {symbol}, skipping in risk analysis.")
                    stock_list = [s for s in stock_list if s != symbol]  # Remove the symbol

            if not stock_list:
                return {"error": "No data available for any of the provided stocks."}

            data = pd.DataFrame({symbol: historical_data[symbol]['close'] for symbol in stock_list})
            returns = data.pct_change().dropna()
            correlation_matrix = returns.corr()

            portfolio_returns = (returns * allocation_data.loc[stock_list].values).sum(axis=1)
            portfolio_risk = portfolio_returns.std()

            latest_prices = {}
            for symbol in stock_list:
                latest_quote_df = self._get_latest_quote(symbol)
                if not latest_quote_df.empty:
                    latest_prices[symbol] = latest_quote_df['price'].iloc[0]
                else:
                    latest_prices[symbol] = None

            previous_prices = data.iloc[-1] if len(data) > 0 else pd.Series(index=stock_list, data=[None] * len(stock_list))

            price_change = pd.Series(index=stock_list)
            for symbol in stock_list:
                if latest_prices[symbol] is not None and previous_prices[symbol] is not None:
                    price_change[symbol] = latest_prices[symbol] - previous_prices[symbol]
                else:
                    price_change[symbol] = None
            largest_change_stock = price_change.abs().idxmax()
            largest_change_value = price_change[largest_change_stock]

            total_allocation = allocation_data.sum().sum()
            asia_tech_allocation = allocation_data[stock_list].sum().sum()
            allocation_percentage = (asia_tech_allocation / total_allocation) * 100

            previous_day_allocation = allocation_data.shift(1)
            previous_day_allocation_percentage = (previous_day_allocation[stock_list].sum().sum() / total_allocation) * 100 if not previous_day_allocation.empty else allocation_percentage

            analysis_result = {
                "correlation_matrix": correlation_matrix.to_dict(),
                "portfolio_risk": portfolio_risk,
                "largest_change_stock": largest_change_stock,
                "largest_change_value": largest_change_value,
                "allocation_percentage": allocation_percentage,
                "previous_day_allocation_percentage": previous_day_allocation_percentage
            }
            return analysis_result
        except Exception as e:
            logger.error(f"Error analyzing risk exposure: {e}")
            return {}

# Real-time loop
if __name__ == "__main__":
    alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not alpha_vantage_key:
        raise ValueError("Alpha Vantage API key is required.")
    api_agent = AlphaVantageAgent(api_key=alpha_vantage_key)
    analysis_agent = AnalysisAgent(api_agent)

    stock_list = ["AAPL", "TSMC", "Samsung"]
    allocation_data = pd.DataFrame({
        "AAPL": [0.1],
        "TSMC": [0.05],
        "Samsung": [0.07],
        "Other1": [0.2],
        "Other2": [0.3],
        "Other3": [0.28]
    }, index=['portfolio_allocation'])

    while True:
        analysis_results = analysis_agent.analyze_risk_exposure(stock_list, allocation_data)
        print("\nAnalysis Results:")
        print(analysis_results)
        
        time.sleep(60)  # Wait for 1 minute before fetching new data
