import streamlit as st
import pandas as pd
import yfinance as yf
from nse_data import get_sector_stocks, get_available_sectors
import time

# Add caching to reduce API calls
@st.cache_data(ttl=300)  # Cache for 5 minutes
def calculate_rsi(data, period=14):
    """Calculate RSI"""
    try:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    except:
        return None

def get_rsi_signal(rsi):
    """Get signal based on RSI"""
    if rsi is None or pd.isna(rsi):
        return "⚪ No Data"
    if rsi < 30:
        return "🟢 Oversold"
    elif rsi > 70:
        return "🔴 Overbought"
    else:
        return "🟡 Neutral"

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_data_with_retry(ticker, max_retries=3):
    """Fetch stock data with retry logic"""
    for attempt in range(max_retries):
        try:
            stock = yf.Ticker(ticker)
            
            hist_1h = stock.history(period="5d", interval="1h")
            hist_1d = stock.history(period="3mo")
            
            rsi_1h = calculate_rsi(hist_1h) if len(hist_1h) > 14 else None
            rsi_1d = calculate_rsi(hist_1d) if len(hist_1d) > 14 else None
            
            return rsi_1h, rsi_1d
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait 1 second before retry
                continue
            return None, None

st.set_page_config(page_title="Indian F&O Stocks Analyzer", layout="wide")

st.title("📊 Indian Sectoral Futures Analyzer")
st.markdown("**Real-time NSE Stock Analysis with RSI Indicators**")

# Info banner
st.info("💡 **Tip:** Data is cached for 5 minutes. If you see errors, wait a minute and try again.")

# Sector selection
sectors = get_available_sectors()
selected_sector = st.selectbox("🔍 Select Sector:", sectors)

if st.button("📈 Fetch Data", type="primary"):
    with st.spinner("Fetching data from Yahoo Finance... This may take 30-60 seconds"):
        df = get_sector_stocks(selected_sector)
        
        if df.empty:
            st.error("❌ No data available. Yahoo Finance might be temporarily unavailable.")
            st.info("🔄 **Try:** Wait 1-2 minutes and click 'Fetch Data' again.")
        else:
            st.success(f"✅ Found {len(df)} stocks in {selected_sector}")
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            rsi_data = []
            total_stocks = len(df)
            
            for idx, (_, row) in enumerate(df.iterrows()):
                status_text.text(f"Processing {row['Symbol']}... ({idx+1}/{total_stocks})")
                progress_bar.progress((idx + 1) / total_stocks)
                
                try:
                    ticker = row['Symbol'] + '.NS'
                    rsi_1h, rsi_1d = fetch_stock_data_with_retry(ticker)
                    
                    rsi_data.append({
                        'Symbol': row['Symbol'],
                        'Company': row['Company'][:30],  # Truncate long names
                        'Price (₹)': row['Price'],
                        'Market Cap (Cr)': round(row['Market Cap'] / 10000000, 2),
                        'RSI (1H)': round(rsi_1h, 2) if rsi_1h else 'N/A',
                        'Signal (1H)': get_rsi_signal(rsi_1h),
                        'RSI (1D)': round(rsi_1d, 2) if rsi_1d else 'N/A',
                        'Signal (1D)': get_rsi_signal(rsi_1d)
                    })
                    
                    time.sleep(0.5)  # Small delay to avoid rate limiting
                    
                except Exception as e:
                    st.warning(f"⚠️ Skipped {row['Symbol']}: {str(e)}")
                    continue
            
            status_text.empty()
            progress_bar.empty()
            
            if rsi_data:
                result_df = pd.DataFrame(rsi_data)
                
                # Display statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Stocks", len(result_df))
                with col2:
                    oversold = len([s for s in result_df['Signal (1D)'] if '🟢' in str(s)])
                    st.metric("Oversold (1D)", oversold)
                with col3:
                    overbought = len([s for s in result_df['Signal (1D)'] if '🔴' in str(s)])
                    st.metric("Overbought (1D)", overbought)
                
                st.dataframe(
                    result_df,
                    use_container_width=True,
                    height=400
                )
                
                st.success("✅ Data loaded successfully!")
            else:
                st.error("❌ Could not fetch data for any stocks. Please try again later.")

st.markdown("---")
st.caption("📊 Data: Yahoo Finance | ⏱️ Cached for 5 mins | 🔄 Refresh to update")

# Sidebar info
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    **Features:**
    - Real-time NSE stock prices
    - RSI indicators (1H & 1D)
    - Market cap sorting
    - Buy/Sell signals
    
    **Note:** Data delays may occur due to API limitations.
    """)
