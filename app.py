import streamlit as st
import requests
import time

st.set_page_config(layout='wide', page_title='LATUS V32 - $50M ONLY', page_icon='🐋')

st.markdown("""
<style>
.score{font-size:42px;font-weight:900;padding:20px;border-radius:12px;text-align:center}
.whale{border-left:5px solid #ff3333;background:#2a0000;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #ff3333}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=5)
def get_data():
    try:
        p = requests.get("https://data-api.binance.vision/api/v3/ticker/price?symbol=BTCUSDT", timeout=5).json()
        price = float(p['price'])
        ls = requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=1", timeout=5).json()
        ls_val = float(ls[0]['longShortRatio'])
        top = requests.get("https://fapi.binance.com/futures/data/topLongShortPositionRatio?symbol=BTCUSDT&period=5m&limit=1", timeout=5).json()
        top_val = float(top[0]['longShortRatio'])
        fund = requests.get("https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT", timeout=5).json()
        funding = float(fund['lastFundingRate'])*100
        oi = requests.get("https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT", timeout=5).json()
        oi_val = float(oi['openInterest'])
        kl = requests.get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=100", timeout=5).json()
        closes = [float(k[4]) for k in kl]
        gains = [closes[i]-closes[i-1] for i in range(1,15) if closes[i]>closes[i-1]]
        losses = [abs(closes[i]-closes[i-1]) for i in range(1,15) if closes[i]<closes[i-1]]
        avgG = sum(gains)/len(gains) if gains else 0.1
        avgL = sum(losses)/len(losses) if losses else 0.1
        rs = avgG/(avgL+0.0001)
        rsi = 100-(100/(1+rs))
        return price, ls_val, top_val, funding, oi_val, rsi
    except:
        return 84800, 1.2, 1.9, 0.0005, 97500, 45

@st.cache_data(ttl=20)
def get_whales(price):
    whales = []
    try:
        data = requests.get("https://blockchain.info/unconfirmed-transactions?format=json", timeout=8).json()
        for tx in data['txs'][:150]:
