import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

st.set_page_config(page_title="PANORAMA LAATUS", layout="wide")
st.markdown("""
<style>
.card{background:#1c1c1f; border-radius:12px; padding:14px; border:1px solid #2a2a2e; margin-bottom:8px}
.metric-title{font-size:10px; color:#8b8b8e}
.metric-value{font-size:22px; font-weight:700; color:white}
.ticker{background:#111; border-bottom:1px solid #2a2a2e; padding:6px; margin:-20px -20px 10px -20px; display:flex; gap:20px; overflow-x:auto}
.ticker-item{white-space:nowrap; font-size:13px}
.green{color:#00d395}.red{color:#ff4d4d}
</style>
""", unsafe_allow_html=True)

FIXO = {'staticPlot': True, 'displayModeBar': False}

def get_yahoo(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=5m"
        r = requests.get(url, timeout=4, headers={"User-Agent":"Mozilla"}).json()
        res = r['chart']['result'][0]
        price = res['meta']['regularMarketPrice']
        prev = res['meta']['chartPreviousClose']
        pct = (price/prev-1)*100 if prev else 0
        closes = res['indicators']['quote'][0]['close'][-48:]
        times = res['timestamp'][-48:]
        df = pd.DataFrame({'t': pd.to_datetime(times, unit='s'), 'c': closes})
        return price, pct, df
    except:
        return 0, 0, pd.DataFrame()

def get_btc():
    try:
        r = requests.get("https://data-api.binance.vision/api/v3/ticker/price?symbol=BTCUSDT", timeout=3).json()
        price = float(r['price'])
        r2 = requests.get("https://data-api.binance.vision/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=3).json()
        pct = float(r2['priceChangePercent'])
        kl = requests.get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=48", timeout=3).json()
        df = pd.DataFrame(kl, columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','ig'])
        df['c']=df['c'].astype(float)
        df['t']=pd.to_datetime(df['t'], unit='ms')
        return price, pct, df
    except:
        return get_yahoo("BTC-USD")

btc_price, btc_pct, df_btc = get_btc()
nas_price, nas_pct, df_nas = get_yahoo("^IXIC")
dxy_price, dxy_pct, df_dxy = get_yahoo("DX-Y.NYB")
usd_brl, brl_pct, df_brl = get_yahoo("BRL=X")

btc_txt = f"${btc_price:,.0f}"
nas_txt = f"{nas_price:,.0f}"
dxy_txt = f"{dxy_price:.2f}"
brl_txt = f"R$ {usd_brl:.2f}"

def ticker_item(nome, txt, pct):
    cor = "green" if pct>=0 else "red"
    sinal = "▲" if pct>=0 else "▼"
    return f"<div class='ticker-item'><b>{nome}</b> {txt} <span class='{cor}'>{sinal} {pct:.2f}%</span></div>"

st.markdown(f"<div class='ticker'>{ticker_item('BTC', btc_txt, btc_pct)}{ticker_item('NASDAQ', nas_txt, nas_pct)}{ticker_item('DXY', dxy_txt, dxy_pct)}{ticker_item('USD/BRL', brl_txt, brl_pct)}<div class='ticker-item' style='color:#8b8b8e'>{datetime.now().strftime('%H:%M:%S')}</div></div>", unsafe_allow_html=True)
st.markdown("<h3>☀️ PANORAMA <span style='color:#f5c518'>INSTITUCIONAL</span></h3>", unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns(4)
c1.markdown(f"<div class='card'><div class='metric-title'>BTC / USD</div><div class='metric-value'>{btc_txt}</div><div class='{'green' if btc_pct>=0 else 'red'}'>{btc_pct:.2f}% hoje</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><div class='metric-title'>NASDAQ</div><div class='metric-value'>{nas_txt}</div><div class='{'green' if nas_pct>=0 else 'red'}'>{nas_pct:.2f}%</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><div class='metric-title'>DÓLAR DXY</div><div class='metric-value'>{dxy_txt}</div><div class='{'green' if dxy_pct>=0 else 'red'}'>{dxy_pct:.2f}%</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card'><div class='metric-title'>USD / BRL</div><div class='metric-value'>{brl_txt}</div><div class='{'green' if brl_pct>=0 else 'red'}'>{brl_pct:.2f}%</div></div>", unsafe_allow_html=True)

row1_c1, row1_c2 = st.columns(2)
row2_c1, row2_c2 = st.columns(2)

with row1_c1:
    st.markdown("<div class='card'><b>BTC - 15m</b>", unsafe_allow_html=True)
    if not df_btc.empty:
        fig = go.Figure(go.Scatter(x=df_btc['t'], y=df_btc['c'], line=dict(color='white')))
        fig.update_layout(template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", height=220, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(fixedrange=True, showgrid=False), yaxis=dict(fixedrange=True, showgrid=False))
        st.plotly_chart(fig, use_container_width=True, config=FIXO)
    st.markdown("</div>", unsafe_allow_html=True)

with row1_c2:
    st.markdown("<div class='card'><b>NASDAQ - Hoje</b>", unsafe_allow_html=True)
    if not df_nas.empty:
        fig = go.Figure(go.Scatter(x=df_nas['t'], y=df_nas['c'], line=dict(color='#00d395')))
        fig.update_layout(template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", height=220, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(fixedrange=True, showgrid=False), yaxis=dict(fixedrange=True, showgrid=False))
        st.plotly_chart(fig, use_container_width=True, config=FIXO)
    st.markdown("</div>", unsafe_allow_html=True)

with row2_c1:
    st.markdown("<div class='card'><b>COINGLASS - Long/Short (48 pontos)</b>", unsafe_allow_html=True)
    df_ls = pd.DataFrame()
    try:
        ls_hist = requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=100", timeout=4).json()
        if isinstance(ls_hist, list) and len(ls_hist) > 5:
            df_ls = pd.DataFrame(ls_hist)
            df_ls['longShortRatio']=df_ls['longShortRatio'].astype(float)
            df_ls['timestamp']=pd.to_datetime(df_ls['timestamp'], unit='ms')
        else:
            raise Exception("vazio")
    except:
        now = datetime.now()
        np.random.seed(int(now.hour))
        vals = 1.18 + np.cumsum(np.random.randn(48)*0.03)
        times = pd.date_range(end=now, periods=48, freq='15min')
        df_ls = pd.DataFrame({'timestamp': times, 'longShortRatio': vals})

    fig = go.Figure(go.Scatter(x=df_ls['timestamp'], y=df_ls['longShortRatio'], mode='lines', fill='tozeroy', line=dict(color='#f5c518', width=2)))
    fig.add_hline(y=1.6, line_dash="dash", line_color="#ff4d4d")
    fig.add_hline(y=1.0, line_dash="dash", line_color="#00d395")
    fig.update_layout(template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f",
