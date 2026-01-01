import requests
import pandas as pd
import yfinance as yf
from typing import Dict, List
import time

class NSEDataFetcher:
    """Fetches real-time data from NSE India"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        self.session = requests.Session()
        
    def get_sectoral_indices(self) -> Dict[str, str]:
        """Returns mapping of sectoral indices to their symbols"""
        return {
            "NIFTY BANK": "NIFTY BANK",
            "NIFTY IT": "NIFTY IT",
            "NIFTY AUTO": "NIFTY AUTO",
            "NIFTY FMCG": "NIFTY FMCG",
            "NIFTY METAL": "NIFTY METAL",
            "NIFTY PHARMA": "NIFTY PHARMA",
            "NIFTY FINANCIAL SERVICES": "NIFTY FINANCIAL SERVICES",
            "NIFTY ENERGY": "NIFTY ENERGY",
            "NIFTY REALTY": "NIFTY REALTY",
            "NIFTY MEDIA": "NIFTY MEDIA"
        }
    
    def get_fo_stocks_by_sector(self) -> Dict[str, List[str]]:
        """
        Returns F&O stocks organized by sector
        Fetched from NSE publicly available F&O segment
        """
        fo_stocks = {
            "NIFTY BANK": [
                "HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK", 
                "INDUSINDBK", "BANKBARODA", "PNB", "FEDERALBNK", "IDFCFIRSTB"
            ],
            "NIFTY IT": [
                "TCS", "INFY", "HCLTECH", "WIPRO", "TECHM", 
                "LTIM", "PERSISTENT", "COFORGE", "MPHASIS", "LTTS"
            ],
            "NIFTY AUTO": [
                "TATAMOTORS", "M&M", "MARUTI", "BAJAJ-AUTO", "EICHERMOT",
                "HEROMOTOCO", "TVSMOTOR", "ASHOKLEY", "ESCORTS", "BALKRISIND"
            ],
            "NIFTY FMCG": [
                "ITC", "HINDUNILVR", "NESTLEIND", "BRITANNIA", "TATACONSUM",
                "DABUR", "GODREJCP", "MARICO", "COLPAL", "VBL"
            ],
            "NIFTY METAL": [
                "TATASTEEL", "JINDALSTEL", "HINDALCO", "VEDL", "NMDC",
                "JSWSTEEL", "HINDZINC", "SAIL", "NATIONALUM", "RATNAMANI"
            ],
            "NIFTY PHARMA": [
                "SUNPHARMA", "CIPLA", "DRREDDY", "DIVISLAB", "TORNTPHARM",
                "LUPIN", "BIOCON", "ALKEM", "AUROPHARMA", "LALPATHLAB"
            ],
            "NIFTY FINANCIAL SERVICES": [
                "HDFCBANK", "ICICIBANK", "SBIN", "BAJFINANCE", "KOTAKBANK",
                "AXISBANK", "HDFCLIFE", "SBILIFE", "ICICIGI", "BAJAJFINSV"
            ],
            "NIFTY ENERGY": [
                "RELIANCE", "ONGC", "NTPC", "POWERGRID", "ADANIGREEN",
                "ADANIPOWER", "TATAPOWER", "ADANITRANS", "IOC", "BPCL"
            ],
            "NIFTY REALTY": [
                "DLF", "GODREJPROP", "OBEROIRLTY", "BRIGADE", "PRESTIGE",
                "PHOENIXLTD", "SOBHA", "MAHLIFE"
            ],
            "NIFTY MEDIA": [
                "ZEEL", "PVRINOX", "SUNTV", "HATHWAY", "DISHTVIND",
                "TV18BRDCST", "NETWORK18"
            ]
        }
        return fo_stocks
    
    def fetch_stock_data(self, ticker: str) -> Dict:
        """Fetch stock data using yfinance"""
        try:
            stock = yf.Ticker(f"{ticker}.NS")
            info = stock.info
            
            return {
                'symbol': ticker,
                'name': info.get('longName', ticker),
                'market_cap': info.get('marketCap', 0),
                'current_price': info.get('currentPrice', 0),
                'sector': info.get('sector', 'N/A'),
                'pe_ratio': info.get('trailingPE', 0),
                'volume': info.get('volume', 0)
            }
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return None
    
    def get_sector_stocks(self, sector_name: str) -> pd.DataFrame:
        """Fetch all stocks for a given sector"""
        fo_stocks = self.get_fo_stocks_by_sector()
        tickers = fo_stocks.get(sector_name, [])
        
        stocks_data = []
        for ticker in tickers:
            data = self.fetch_stock_data(ticker)
            if data and data['market_cap'] > 0:
                stocks_data.append(data)
            time.sleep(0.1)  # Rate limiting
        
        df = pd.DataFrame(stocks_data)
        if not df.empty:
            df = df.sort_values('market_cap', ascending=False)
            df['market_cap_cr'] = (df['market_cap'] / 10000000).round(2)
        
        return df
