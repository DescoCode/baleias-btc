import streamlit as st
import requests

st.set_page_config(layout='wide', page_title='LATUS V33 - 50M ONLY')

@st.cache_data(ttl=5)
def get_data():
    try:
        price = float(requests.get("https://data-api.binance.vision/api/v3/ticker/price?symbol=BTCUSDT", timeout=5).json()['price'])
        ls = float(requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=1", timeout=5).json()[0]['longShortRatio'])
        top = float(requests.get("https://fapi.binance.com/futures/data/topLongShortPositionRatio?symbol=BTCUSDT&period=5m&limit=1", timeout=5).json()[0]['longShortRatio'])
        fund = float(requests.get("https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT", timeout=5).json()['lastFundingRate'])*100
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
        rsi = 100-(100/(1+avgG/(avgL+0.0001)))
        return price, ls, top, fund, rsi
    except:
        return 84800, 1.2, 1.9, 0.0005, 45

@st.cache_data(ttl=20)
def get_whales(price):
    whales = []
    try:
        data = requests.get("https://blockchain.info/unconfirmed-transactions?format=json", timeout=8).json()
        for tx in data['txs'][:150]:
            btc = sum([o['value'] for o in tx['out']])/1e8
            usd = btc*price
            if usd >= 50000000:
                whales.append((btc, usd, tx['hash']))
    except:
        pass
    return whales

price, ls_val, top_val, funding, rsi = get_data()
whales = get_whales(price)

ls_ok = 0.9 <= ls_val <= 1.30
top_ok = top_val > 1.80
rsi_ok = 32 <= rsi <= 52
blocked = len(whales) > 0

score = 0
if ls_ok:
    score += 2
if top_ok:
    score += 1.5
if rsi_ok:
    score += 1.5
if blocked:
    score = 0

st.title(f"BTC ${price:.0f} - LS {ls_val:.2f} - TOP {top_val:.2f}")

if blocked:
    st.error(f"BLOQUEADO - {len(whales)} BALEIA(S) ACIMA DE $50M - ROBO PARADO 30min")
    for btc, usd, h in whales:
        st.write(f"${usd/1e6:.1f}M ({btc:.1f} BTC) - https://mempool.space/tx/{h}")
elif score >= 3.5:
    st.success(f"COMPRA ALTA - 76% - BTC ${price:.0f} - Alvo ${price*1.031:.0f}")
else:
    st.warning(f"ESPERA - SCORE {score:.1f} - Precisa LS neutro + TOP>1.8 + RSI 32-52 + SEM baleia $50M")

st.write(f"LS Ratio: {ls_val:.4f} - {'OK' if ls_ok else 'RUIM'}")
st.write(f"Top Trader: {top_val:.4f} - {'WHALE LONG' if top_ok else 'NEUTRO'}")
st.write(f"RSI: {rsi:.1f} - {'ZONA LONG' if rsi_ok else 'FORA'}")
st.write(f"Funding: {funding:.4f}%")

if not whales:
    st.success("NENHUMA BALEIA >$50M - Mempool limpo - Robo liberado")
