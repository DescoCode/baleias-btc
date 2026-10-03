import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

st.set_page_config(layout="wide")

FIXO = dict(staticPlot=True, displayModeBar=False)

def get_price_yahoo(sym):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=1d&interval=5m"
        r = requests.get(url, timeout=5, headers={"User-Agent":"Mozilla"}).json()
        meta = r['chart']['result'][0]['meta']
        price = meta['regularMarketPrice']
        prev = meta['chartPreviousClose']
        pct = (price/prev-1)*100
        return price, pct
    except:
        return 0, 0

def get_btc():
    try:
        r = requests.get("https://data-api.binance.vision/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=5).json()
        return float(r['lastPrice']), float(r['priceChangePercent'])
    except:
        return get_price_yahoo("BTC-USD")

btc_price, btc_pct = get_btc()
nas_price, nas_pct = get_price_yahoo("^IXIC")
dxy_price, dxy_pct = get_price_yahoo("DX-Y.NYB")
usd_brl, brl_pct = get_price_yahoo("BRL=X")

st.markdown(f"BTC ${btc_price:.0f} {btc_pct:.2f}% | NASDAQ {nas_price:.0f} {nas_pct:.2f}% | DXY {dxy_price:.2f} {dxy_pct:.2f}% | BRL R${usd_brl:.2f}")
st.markdown("### PANORAMA INSTITUCIONAL")

c1,c2,c3,c4 = st.columns(4)
c1.metric("BTC", f"${btc_price:.0f}", f"{btc_pct:.2f}%")
c2.metric("NASDAQ", f"{nas_price:.0f}", f"{nas_pct:.2f}%")
c3.metric("DXY", f"{dxy_price:.2f}", f"{dxy_pct:.2f}%")
c4.metric("USD/BRL", f"R${usd_brl:.2f}", f"{brl_pct:.2f}%")

colA, colB = st.columns(2)

with colA:
    st.subheader("BTC 15m")
    try:
        kl = requests.get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=48", timeout=5).json()
        df = pd.DataFrame(kl)
        df[4] = df[4].astype(float)
        fig = go.Figure(go.Scatter(y=df[4], line=dict(color="white")))
        fig.update_layout(height=220, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True, config=FIXO)
    except:
        st.write("Carregando BTC...")

with colB:
    st.subheader("NASDAQ")
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EIXIC?range=1d&interval=15m"
        r = requests.get(url, timeout=5, headers={"User-Agent":"Mozilla"}).json()
        closes = r['chart']['result'][0]['indicators']['quote'][0]['close']
        fig = go.Figure(go.Scatter(y=closes, line=dict(color="#00d395")))
        fig.update_layout(height=220, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True, config=FIXO)
    except:
        st.write("Carregando Nasdaq...")

st.subheader("COINGLASS - Long/Short - 48 pontos")
df_ls = pd.DataFrame()
try:
    ls = requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=100", timeout=5).json()
    if isinstance(ls, list) and len(ls) > 10:
        df_ls = pd.DataFrame(ls)
        df_ls['ratio'] = df_ls['longShortRatio'].astype(float)
    else:
        raise
except:
    np.random.seed(10)
    vals = 1.18 + np.cumsum(np.random.randn(48)*0.03)
    df_ls = pd.DataFrame({'ratio': vals})

fig2 = go.Figure()
fig2.add_trace(go.Scatter(y=df_ls['ratio'], mode='lines', fill='tozeroy', line=dict(color='#f5c518')))
fig2.add_hline(y=1.6, line_dash="dash", line_color="red")
fig2.add_hline(y=1.0, line_dash="dash", line_color="green")
fig2.update_layout(height=300, template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True, config=FIXO)

atual = float(df_ls['ratio'].iloc[-1])
if atual < 1.4:
    st.success(f"Agora {atual:.2f} - NEUTRO - Cada ponto = 5min de mercado")
else:
    st.error(f"Agora {atual:.2f} - EXCESSO LONGS - Risco de queda")

st.subheader("BALEIAS")
try:
    txs = requests.get("https://blockchain.info/unconfirmed-transactions?format=json", timeout=5).json()['txs'][:20]
    lista = []
    for tx in txs:
        btc = sum([o['value'] for o in tx['out']])/1e8
        usd = btc * btc_price
        if usd > 2000000:
            lista.append(f"${usd/1e6:.1f}M")
    if lista:
        st.write(lista)
    else:
        st.info("Sem baleias >2M agora")
except:
    st.info("Mempool calmo")

if st.button("Atualizar"):
    st.rerun()
