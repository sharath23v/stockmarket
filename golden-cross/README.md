# NSE Pro Strategy Scanner

A Streamlit-based web application that scans National Stock Exchange (NSE) indices to identify potential trading opportunities based on moving average crossovers and volume spikes.

## Features

* **Real-time NSE Data Fetching:** Directly fetches the latest stock constituents for Nifty 50, Nifty 200, Nifty 500, and Nifty Total Market indices directly from the NSE archives.
* **Technical Analysis:** Calculates the 200-Day Moving Average (DMA), 50-DMA, and 20-Day average volume using Yahoo Finance (`yfinance`).
* **🔥 7-Day Breakouts:** Scans for stocks that have crossed above their 200-DMA within the last 7 trading days.
* **🚀 Long-Term Leaders:** Identifies stocks in a confirmed long-term uptrend (Current Price > 50-DMA > 200-DMA).
* **Volume Spikes:** Highlights stocks experiencing unusual trading volume (greater than 1.5x their 20-day average).
* **Smart Caching:** Utilizes Streamlit's caching features to reduce redundant network requests and avoid hitting API rate limits.

## Prerequisites & Installation

1. Ensure you have Python installed on your system.
2. Navigate to the project directory:
   ```bash
   cd /home/sharath/applications/stockmarket/golden-cross
   ```
3. Install the required Python dependencies:
   ```bash
   pip install streamlit yfinance pandas requests
   ```

## Usage

1. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```
2. Open your web browser to the provided local URL (usually `http://localhost:8501`).
3. Select your desired index from the left sidebar (e.g., Nifty 200 or Nifty 500).
4. Click **Launch Market Scan** and wait for the scanner to iterate through the stocks.
5. Review the matching stocks in the respective result tabs.

## Disclaimer

This software is strictly for educational and informational purposes only. It does not constitute financial advice. Always do your own research before making any trading or investment decisions.