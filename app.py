import streamlit as st
import pandas as pd
import yfinance as yf
from nse_data import get_sector_stocks, get_available_sectors

def calculate_rsi(data, period=14):
    """Calculate RSI"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def get_rsi_signal(rsi):
    """Get signal based on RSI"""
    if rsi < 30:
        return "🟢 Oversold (Buy)"
    elif rsi > 70:
        return "🔴 Overbought (Sell)"
    else:
        return "🟡 Neutral"

st.set_page_config(page_title="Indian F&O Stocks Analyzer", layout="wide")

st.title("📊 Indian Futures & Options Stocks Analyzer")
st.markdown("**Sectoral Analysis with RSI Indicators**")

# Sector selection
sectors = get_available_sectors()
selected_sector = st.selectbox("🔍 Select Sector:", sectors)

if st.button("📈 Fetch Data"):
    with st.spinner("Fetching data..."):
        df = get_sector_stocks(selected_sector)
        
        if df.empty:
            st.error("❌ No data available. Please try again.")
        else:
            st.success(f"✅ Found {len(df)} stocks in {selected_sector}")
            
            # Calculate RSI
            rsi_data = []
            for _, row in df.iterrows():
                try:
                    ticker = row['Symbol'] + '.NS'
                    stock = yf.Ticker(ticker)
                    
                    hist_1h = stock.history(period="5d", interval="1h")
                    hist_1d = stock.history(period="3mo")
                    
                    rsi_1h = calculate_rsi(hist_1h) if not hist_1h.empty else None
                    rsi_1d = calculate_rsi(hist_1d) if not hist_1d.empty else None
                    
                    rsi_data.append({
                        'Symbol': row['Symbol'],
                        'Company': row['Company'],
                        'Price': row['Price'],
                        'Market Cap (Cr)': round(row['Market Cap'] / 10000000, 2),
                        'RSI (1H)': round(rsi_1h, 2) if rsi_1h else 'N/A',
                        'Signal (1H)': get_rsi_signal(rsi_1h) if rsi_1h else 'N/A',
                        'RSI (1D)': round(rsi_1d, 2) if rsi_1d else 'N/A',
                        'Signal (1D)': get_rsi_signal(rsi_1d) if rsi_1d else 'N/A'
                    })
                except:
                    continue
            
            if rsi_data:
                result_df = pd.DataFrame(rsi_data)
                st.dataframe(result_df, use_container_width=True)
            else:
                st.warning("⚠️ Could not calculate RSI for any stocks.")

st.markdown("---")
st.caption("Data powered by Yahoo Finance | Real-time NSE stock data")
