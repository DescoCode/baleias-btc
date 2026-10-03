import streamlit as st
import requests

st.set_page_config(layout='wide', page_title='LATUS V32 - 50M ONLY', page_icon='🐋')

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
        gains = []
        losses = []
        for i in range(1,15):
            d = closes[-i] - closes[-i-1]
            if d > 0:
                gains.append(d)
            else:
                losses.append(abs(d))
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
        txs = data['txs'][:150]
        for tx in txs:
            btc = sum([o['value'] for o in tx['out']])/1e8
            usd = btc*price
            if usd >= 50000000:
                whales.append({"btc":btc, "usd":usd, "hash":tx['hash']})
    except:
        pass
    return whales

price, ls_val, top_val, funding, oi_val, rsi = get_data()
whales = get_whales(price)

ls_pass_long = 0.9 <= ls_val <= 1.30
ls_pass_short = ls_val >= 1.70
top_pass_long = top_val > 1.80
rsi_pass_long = 32 <= rsi <= 52
fund_pass = -0.02 < funding < 0.03
whale_block = len(whales) > 0

score = 0
if ls_pass_long:
    score += 2
if ls_pass_short:
    score -= 2
if top_pass_long:
    score += 1.5
if rsi_pass_long:
    score += 1.5
if fund_pass:
    score += 0.5
if whale_block:
    score = 0

winrate = 82 if abs(score) >= 4.5 else 76 if abs(score) >= 3.5 else 45

st.markdown(f"**BTC ${price:.0f} | LS {ls_val:.2f} | TOP {top_val:.2f} | RSI {rsi:.0f}**")

if whale_block:
    st.markdown(f"<div class='score' style='background:#2a0000;border:3px solid #ff3333;color:#ff3333'>BLOQUEADO - {len(
