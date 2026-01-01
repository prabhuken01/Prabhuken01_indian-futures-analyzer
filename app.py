import streamlit as st
import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator
import plotly.graph_objects as go
from nse_data import NSEDataFetcher
import time

# Page Configuration
st.set_page_config(
    page_title="Indian Sectoral Futures Analyzer",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B35;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
    }
    .stButton>button {
        background-color: #667eea;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'fetcher' not in st.session_state:
    st.session_state.fetcher = NSEDataFetcher()

# Helper Functions
def get_rsi(ticker: str, interval: str, period: str) -> float:
    """Calculate RSI for given timeframe"""
    try:
        data = yf.download(f"{ticker}.NS", period=period, interval=interval, progress=False)
        if data.empty or len(data) < 14:
            return None
        
        rsi_indicator = RSIIndicator(close=data['Close'].squeeze(), window=14)
        rsi_value = rsi_indicator.rsi().iloc[-1]
        return round(rsi_value, 2) if pd.notna(rsi_value) else None
    except Exception as e:
        return None

def get_rsi_signal(rsi: float) -> tuple:
    """Returns signal and color based on RSI"""
    if rsi is None:
        return "N/A", "gray"
    elif rsi > 70:
        return "🔴 Overbought", "red"
    elif rsi < 30:
        return "🟢 Oversold", "green"
    else:
        return "⚪ Neutral", "blue"

def create_rsi_gauge(rsi_value: float, title: str):
    """Create a gauge chart for RSI"""
    if rsi_value is None:
        return None
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rsi_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 70], 'color': "lightyellow"},
                {'range': [70, 100], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': rsi_value
            }
        }
    ))
    
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10))
    return fig

# Main App
def main():
    # Header
    st.markdown('<div class="main-header">🇮🇳 Indian Sectoral Futures Analyzer</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/8/82/NSE_Logo.svg/1200px-NSE_Logo.svg.png", width=200)
        st.header("📊 Settings")
        
        # Sector Selection
        sectors = list(st.session_state.fetcher.get_sectoral_indices().keys())
        selected_sector = st.selectbox(
            "🎯 Select Sectoral Index",
            sectors,
            help="Choose an NSE sectoral index to analyze"
        )
        
        st.markdown("---")
        
        # Filters
        st.subheader("🔍 Filters")
        min_market_cap = st.number_input(
            "Min Market Cap (Cr)",
            min_value=0,
            value=0,
            step=1000,
            help="Filter companies by minimum market capitalization"
        )
        
        show_only_tradable = st.checkbox(
            "Show only F&O stocks",
            value=True,
            help="Display only stocks with Futures & Options"
        )
        
        st.markdown("---")
        
        # Info
        st.info("""
        **Data Sources:**
        - NSE India (via yfinance)
        - Real-time market data
        - Technical indicators (TA-Lib)
        
        **RSI Legend:**
        - 🟢 < 30: Oversold
        - ⚪ 30-70: Neutral
        - 🔴 > 70: Overbought
        """)
        
        # Fetch Button
        fetch_data = st.button("🔄 Refresh Data", use_container_width=True)
    
    # Main Content
    if selected_sector:
        st.header(f"📈 {selected_sector}")
        
        # Fetch data
        with st.spinner('🔄 Fetching live NSE data...'):
            df = st.session_state.fetcher.get_sector_stocks(selected_sector)
        
        if df.empty:
            st.warning("⚠️ No data available for this sector.")
            return
        
        # Apply filters
        if min_market_cap > 0:
            df = df[df['market_cap_cr'] >= min_market_cap]
        
        # Display Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Companies", len(df))
        with col2:
            avg_mcap = df['market_cap_cr'].mean()
            st.metric("💰 Avg Market Cap (Cr)", f"₹{avg_mcap:,.0f}")
        with col3:
            total_mcap = df['market_cap_cr'].sum()
            st.metric("📈 Total Market Cap (Cr)", f"₹{total_mcap:,.0f}")
        with col4:
            avg_pe = df['pe_ratio'].replace(0, pd.NA).mean()
            st.metric("📊 Avg P/E Ratio", f"{avg_pe:.2f}" if pd.notna(avg_pe) else "N/A")
        
        st.markdown("---")
        
        # Companies Table
        st.subheader("🏢 Companies (Sorted by Market Cap)")
        
        # Prepare display dataframe
        display_df = df[['symbol', 'name', 'market_cap_cr', 'current_price', 'pe_ratio', 'volume']].copy()
        display_df.columns = ['Symbol', 'Company Name', 'Market Cap (Cr)', 'Price (₹)', 'P/E Ratio', 'Volume']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400,
            hide_index=True
        )
        
        st.markdown("---")
        
        # Stock Analysis Section
        st.subheader("🔍 Detailed Technical Analysis")
        
        selected_stock = st.selectbox(
            "Select a stock for technical analysis:",
            df['symbol'].tolist(),
            format_func=lambda x: f"{x} - {df[df['symbol']==x]['name'].values[0]}"
        )
        
        if selected_stock:
            st.markdown(f"### 📊 {selected_stock} Analysis")
            
            with st.spinner('📊 Calculating technical indicators...'):
                # Fetch RSI data
                rsi_1h = get_rsi(selected_stock, "1h", "5d")
                rsi_1d = get_rsi(selected_stock, "1d", "3mo")
                
                # Display RSI Gauges
                col1, col2 = st.columns(2)
                
                with col1:
                    if rsi_1h:
                        fig_1h = create_rsi_gauge(rsi_1h, "RSI - 1 Hour")
                        st.plotly_chart(fig_1h, use_container_width=True)
                        signal_1h, color_1h = get_rsi_signal(rsi_1h)
                        st.markdown(f"**Signal:** :{color_1h}[{signal_1h}]")
                    else:
                        st.warning("1H RSI data unavailable")
                
                with col2:
                    if rsi_1d:
                        fig_1d = create_rsi_gauge(rsi_1d, "RSI - 1 Day")
                        st.plotly_chart(fig_1d, use_container_width=True)
                        signal_1d, color_1d = get_rsi_signal(rsi_1d)
                        st.markdown(f"**Signal:** :{color_1d}[{signal_1d}]")
                    else:
                        st.warning("1D RSI data unavailable")
                
                # Summary Table
                st.markdown("#### 📋 Technical Summary")
                summary_data = {
                    'Timeframe': ['1 Hour', '1 Day'],
                    'RSI Value': [rsi_1h if rsi_1h else 'N/A', rsi_1d if rsi_1d else 'N/A'],
                    'Signal': [get_rsi_signal(rsi_1h)[0], get_rsi_signal(rsi_1d)[0]]
                }
                summary_df = pd.DataFrame(summary_data)
                st.table(summary_df)
                
                # Trading Recommendation
                st.markdown("#### 💡 Quick Interpretation")
                
                if rsi_1h and rsi_1d:
                    if rsi_1h > 70 and rsi_1d > 70:
                        st.error("⚠️ **Strong Overbought Signal** - Consider taking profits")
                    elif rsi_1h < 30 and rsi_1d < 30:
                        st.success("✅ **Strong Oversold Signal** - Potential buying opportunity")
                    elif rsi_1h > 70 and rsi_1d < 50:
                        st.warning("📊 **Mixed Signals** - Short-term overbought, long-term neutral")
                    elif rsi_1h < 30 and rsi_1d > 50:
                        st.info("📊 **Short-term Dip** - Possible intraday opportunity")
                    else:
                        st.info("📊 **Neutral Zone** - Wait for clearer signals")

if __name__ == "__main__":
    main()
