import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import io
import time

# --- Page Configuration ---
st.set_page_config(page_title="NSE Pro Strategy Scanner", layout="wide")
st.title("📊 NSE 200-DMA & Trend Scanner")

# --- 1. Robust Ticker Fetching using Requests ---
@st.cache_data(ttl=86400) # Cache list for 24 hours
def get_tickers(index_choice):
    # Mapping for 2026 NSE CSV URLs
    urls = {
        "Nifty 50": "https://archives.nseindia.com/content/indices/ind_nifty50list.csv",
        "Nifty 200": "https://archives.nseindia.com/content/indices/ind_nifty200list.csv",
        "Nifty 500": "https://archives.nseindia.com/content/indices/ind_nifty500list.csv",
        "Total Market": "https://archives.nseindia.com/content/indices/ind_niftytotalmarket_list.csv"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://www.nseindia.com/"
    }

    try:
        # Step 1: Establish a session to handle potential cookies
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        
        # Step 2: Request the CSV
        response = session.get(urls[index_choice], headers=headers, timeout=10)
        
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            return df[['Symbol', 'Company Name']]
        else:
            st.error(f"NSE returned error code: {response.status_code}. Try again in a few minutes.")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return pd.DataFrame()

# --- 2. Caching the Individual Stock Scan ---
@st.cache_data(ttl=3600, show_spinner=False) 
def scan_stock(symbol):
    try:
        ticker = f"{symbol}.NS"
        # Using Ticker().history() avoids MultiIndex formatting issues from recent yfinance versions
        data = yf.Ticker(ticker).history(period="1y", interval="1d")
        
        if len(data) < 210: return None

        # Indicators
        data['200DMA'] = data['Close'].rolling(window=200).mean()
        data['50DMA'] = data['Close'].rolling(window=50).mean()
        data['Vol_Avg'] = data['Volume'].rolling(window=20).mean()
        
        curr = data.iloc[-1]
        
        # Logic: 7-Day Breakout Window
        last_week = data.tail(7)
        was_below = (last_week['Close'] < last_week['200DMA']).any()
        is_above = curr['Close'] > curr['200DMA']
        breakout_7d = was_below and is_above

        # Logic: Long-Term Uptrend
        uptrend = curr['Close'] > curr['50DMA'] and curr['50DMA'] > curr['200DMA']
        vol_ratio = float(curr['Volume'] / (curr['Vol_Avg'] if curr['Vol_Avg'] else 1))

        return {
            "Symbol": symbol,
            "Price": round(float(curr['Close']), 2),
            "Vol Ratio": round(vol_ratio, 2),
            "Vol Spike": "✅" if vol_ratio > 1.5 else "❌",
            "is_breakout": breakout_7d,
            "is_uptrend": uptrend
        }
    except Exception as e:
        # If you want to see errors in your terminal, uncomment the next line:
        # print(f"Error on {symbol}: {e}")
        return None

# --- UI Sidebar ---
st.sidebar.header("Configuration")
index_choice = st.sidebar.selectbox("Select Index", ["Nifty 50", "Nifty 200", "Nifty 500", "Total Market"])
run_button = st.sidebar.button("Launch Market Scan")

# --- Main Logic ---
if run_button:
    stock_list = get_tickers(index_choice)
    
    if not stock_list.empty:
        symbols = stock_list['Symbol'].tolist()
        results = []
        progress_bar = st.progress(0)
        status = st.empty()
        
        start_time = time.time()
        for i, s in enumerate(symbols):
            res = scan_stock(s)
            if res: results.append(res)
            progress_bar.progress((i + 1) / len(symbols))
            status.text(f"Scanning {i+1}/{len(symbols)}: {s}")

        st.success(f"Scan complete in {round(time.time() - start_time, 1)} seconds!")

        if results:
            df = pd.DataFrame(results)
            tab1, tab2 = st.tabs(["🔥 7-Day Breakouts", "🚀 Long-Term Leaders"])
            
            with tab1:
                b_df = df[df['is_breakout']].drop(columns=['is_breakout', 'is_uptrend'])
                st.dataframe(b_df.sort_values("Vol Ratio", ascending=False), use_container_width=True)

            with tab2:
                u_df = df[df['is_uptrend']].drop(columns=['is_breakout', 'is_uptrend'])
                st.dataframe(u_df.sort_values("Vol Ratio", ascending=False), use_container_width=True)
        else:
            st.warning("No matches found.")
    else:
        st.error("Still unable to fetch the list. NSE might be temporarily blocking requests.")