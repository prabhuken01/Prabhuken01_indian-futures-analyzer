import yfinance as yf
import pandas as pd

# Indian F&O stocks by sector (NSE tickers)
SECTORAL_STOCKS = {
    "NIFTY IT": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "LTIM.NS", "COFORGE.NS"],
    "NIFTY BANK": ["HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "AXISBANK.NS", "INDUSINDBK.NS", "BANDHANBNK.NS"],
    "NIFTY AUTO": ["MARUTI.NS", "M&M.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "TVSMOTOR.NS"],
    "NIFTY PHARMA": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "APOLLOHOSP.NS", "BIOCON.NS", "LUPIN.NS"],
    "NIFTY FMCG": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS", "GODREJCP.NS", "MARICO.NS"],
    "NIFTY METAL": ["TATASTEEL.NS", "HINDALCO.NS", "JSWSTEEL.NS", "VEDL.NS", "NATIONALUM.NS", "NMDC.NS", "SAIL.NS"],
    "NIFTY ENERGY": ["RELIANCE.NS", "ONGC.NS", "POWERGRID.NS", "NTPC.NS", "COALINDIA.NS", "BPCL.NS", "IOC.NS"]
}

def get_sector_stocks(sector):
    """Fetch stock data for a given sector"""
    try:
        stocks = SECTORAL_STOCKS.get(sector, [])
        if not stocks:
            return pd.DataFrame()
        
        data_list = []
        
        for ticker in stocks:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="1d")
                
                if not hist.empty:
                    data_list.append({
                        'Symbol': ticker.replace('.NS', ''),
                        'Company': info.get('longName', ticker),
                        'Price': round(hist['Close'].iloc[-1], 2),
                        'Market Cap': info.get('marketCap', 0),
                        'Volume': hist['Volume'].iloc[-1]
                    })
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")
                continue
        
        if data_list:
            df = pd.DataFrame(data_list)
            df = df.sort_values('Market Cap', ascending=False)
            return df
        
        return pd.DataFrame()
        
    except Exception as e:
        print(f"Error in get_sector_stocks: {e}")
        return pd.DataFrame()

def get_available_sectors():
    """Return list of available sectors"""
    return list(SECTORAL_STOCKS.keys())
