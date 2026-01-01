import yfinance as yf
import pandas as pd

# Indian F&O stocks by sector
SECTORAL_STOCKS = {
    "NIFTY IT": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "NIFTY BANK": ["HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "AXISBANK.NS"],
    "NIFTY AUTO": ["MARUTI.NS", "M&M.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "NIFTY PHARMA": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "APOLLOHOSP.NS"],
    "NIFTY FMCG": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS"],
}

def get_sector_stocks(sector):
    """Fetch stock data for given sector using yfinance"""
    stocks = SECTORAL_STOCKS.get(sector, [])
    if not stocks:
        return pd.DataFrame()
    
    data_list = []
    
    for ticker in stocks:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            info = stock.info
            
            if not hist.empty:
                data_list.append({
                    'Symbol': ticker.replace('.NS', ''),
                    'Company': info.get('longName', ticker.replace('.NS', '')),
                    'Price': round(hist['Close'].iloc[-1], 2),
                    'Market Cap': info.get('marketCap', 0)
                })
        except:
            continue
    
    if data_list:
        df = pd.DataFrame(data_list)
        df = df.sort_values('Market Cap', ascending=False)
        return df
    
    return pd.DataFrame()

def get_available_sectors():
    """Return available sectors"""
    return list(SECTORAL_STOCKS.keys())
