import fastapi
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import pandas as pd
import logging
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the FastAPI app
app = FastAPI()

class AlphaVantageAgent:
    """
    A simplified agent for fetching data from Alpha Vantage.
    """
    def __init__(self, api_key: str = alpha_vantage_api_key):
        """
        Initializes the AlphaVantageAgent.

        Args:
            api_key (str): The Alpha Vantage API key.
        """
        if not api_key:
            raise ValueError("Alpha Vantage API key is required.")
        self.api_key = api_key

    def _fetch_data(self, function: str, symbol: str, params: dict = {}) -> pd.DataFrame:
        """
        Fetches data from Alpha Vantage and returns a Pandas DataFrame.

        Args:
            function (str): The Alpha Vantage API function.
            symbol (str): The stock symbol.
            params (dict, optional): Additional parameters.

        Returns:
            pd.DataFrame: The data as a Pandas DataFrame.

        Raises:
            ValueError: For Alpha Vantage API errors.
            KeyError: If a key is missing in the response.
            requests.exceptions.RequestException: For network errors.
        """
        base_url = "https://www.alphavantage.co/query"
        payload = {"function": function, "symbol": symbol, "apikey": self.api_key, **params}
        try:
            response = requests.get(base_url, params=payload)
            response.raise_for_status()
            data = response.json()

            # Log the raw response (for debugging)
            logger.debug(f"Alpha Vantage response for {symbol} - {function}: {data}")

            if "Error Message" in data:
                raise ValueError(f"Alpha Vantage API Error: {data['Error Message']}")

            # Convert the JSON data to a Pandas DataFrame
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
                if not quote_data:
                    return pd.DataFrame()
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
                numeric_cols = ['open', 'high', 'low', 'price', 'volume', 'previous_close', 'change', 'change_percent']
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                return df
            elif function == "OVERVIEW":
                if "Symbol" not in data:
                    return pd.DataFrame()
                df = pd.DataFrame([data])
                numeric_cols = ['MarketCapitalization', 'EBITDA', 'PERatio', 'PEGRatio', 'BookValue',
                                'DividendYield', 'EPS', 'Revenue', 'GrossProfit', 'ProfitMargin',
                               'OperatingMarginTTM']

                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col].replace({',':''}), errors='coerce')
                return df
            else:
                return pd.DataFrame(data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from Alpha Vantage: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch data from Alpha Vantage: {e}")
        except KeyError as e:
            logger.error(f"KeyError in Alpha Vantage response: {e}")
            raise HTTPException(status_code=500, detail=f"Invalid data from Alpha Vantage: {e}")
        except ValueError as e:
            logger.error(f"ValueError: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    def get_stock_prices(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Gets the latest stock prices for a list of symbols.

        Args:
            symbols (List[str]): A list of stock symbols.

        Returns:
            Dict[str, pd.DataFrame]: A dictionary of stock prices.
        """
        results = {}
        for symbol in symbols:
            try:
                df = self._fetch_data(function="GLOBAL_QUOTE", symbol=symbol)
                results[symbol] = df
            except HTTPException as e:
                logger.error(f"Error getting stock price for {symbol}: {e.detail}")
                results[symbol] = pd.DataFrame()  # Store empty DataFrame on error
        return results

    def get_historical_data(self, symbol: str, interval: str = "1d", period: str = "1y") -> pd.DataFrame:
        """
        Gets historical stock data for a given symbol.

        Args:
            symbol (str): The stock symbol.
            interval (str, optional): The time interval.  Defaults to "1d".
            period: Not used
        Returns:
            pd.DataFrame: Historical data.
        """
        if interval not in ["1d", "1wk", "1mo"]:
            raise HTTPException(status_code=400, detail=f"Interval '{interval}' not supported. Use '1d', '1wk', or '1mo'.")
        try:
            if interval == "1d":
                function = "TIME_SERIES_DAILY"
            elif interval == "1wk":
                function = "TIME_SERIES_WEEKLY"
            elif interval == "1mo":
                function = "TIME_SERIES_MONTHLY"
            return self._fetch_data(function=function, symbol=symbol, params={"outputsize": "full"})
        except HTTPException as e:
            logger.error(f"Error getting historical data for {symbol}: {e.detail}")
            raise e # re-raise

    def get_company_overview(self, symbol: str) -> pd.DataFrame:
        """
        Gets company overview data for a given symbol.

        Args:
            symbol (str): The stock symbol.

        Returns:
            pd.DataFrame: Company overview data.
        """
        try:
            return self._fetch_data(function="OVERVIEW", symbol=symbol)
        except HTTPException as e:
            logger.error(f"Error getting company overview for {symbol}: {e.detail}")
            raise e # re-raise

# Initialize the AlphaVantageAgent
api_agent = AlphaVantageAgent()

# Define API endpoints using FastAPI
class StockPriceRequest(BaseModel):
    symbols: List[str]

class HistoricalDataRequest(BaseModel):
    symbol: str
    interval: str = "1d"
    period: str = "1y"  # Not used for AlphaVantage, but kept for consistency

class CompanyOverviewRequest(BaseModel):
    symbol: str

@app.post("/stock_prices", response_model=Dict[str, dict])
async def get_stock_prices(request: StockPriceRequest):
    """
    Endpoint to get stock prices for multiple symbols.
    """
    try:
        prices = api_agent.get_stock_prices(request.symbols)
        # Convert DataFrames to dictionaries before returning them in the response
        prices_dict = {symbol: df.to_dict(orient='records') if not df.empty else {} for symbol, df in prices.items()}
        return prices_dict
    except HTTPException as e:
        raise e

@app.post("/historical_data", response_model=dict)
async def get_historical_data(request: HistoricalDataRequest):
    """
    Endpoint to get historical stock data for a symbol.
    """
    try:
        data = api_agent.get_historical_data(request.symbol, request.interval, request.period)
        return data.to_dict(orient='records') if not data.empty else {} # Return as dict
    except HTTPException as e:
        raise e

@app.post("/company_overview", response_model=dict)
async def get_company_overview(request: CompanyOverviewRequest):
    """
    Endpoint to get company overview for a symbol.
    """
    try:
        overview = api_agent.get_company_overview(request.symbol)
        return overview.to_dict(orient='records') if not overview.empty else {}
    except HTTPException as e:
        raise e

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
