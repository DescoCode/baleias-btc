import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="PANORAMA - Radar", layout="wide")
st.markdown("<style>.card{background:#1c1c1f; border-radius:12px; padding:16px; border:1px solid #2a2a2e}.metric-title{font-size:13px; color:#8b8b8e}.metric-value{font-size:28px; font-weight:700; color:white}</style>", unsafe_allow_html=True)
st.markdown("<h2>☀️ PANORAMA <span style='color:#f5c518'>INSTITUCIONAL</span> | BTC</h2>", unsafe_allow_html=True)
st.markdown("<meta http-equiv='refresh' content='60'>", unsafe_allow_html=True)

CONFIG_PLOTLY_FIXO = {'staticPlot': True, 'displayModeBar': False, 'scrollZoom': False, 'doubleClick': False}

BINANCE_SPOT = "https://data-api.binance.vision/api/v3"
BINANCE_FUT = "https://fapi.binance.com"

def safe_price():
    try:
        r = requests.get(f"{BINANCE_SPOT}/ticker/price?symbol=BTCUSDT", timeout=8).json()
        if 'price' in r: return float(r['price'])
    except: pass
    return float(requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=8).json()['bitcoin']['usd'])

@st.cache_data(ttl=40)
def get_data():
    price = safe_price()
    try:
        klines = requests.get(f"{BINANCE_SPOT}/klines?symbol=BTCUSDT&interval=15m&limit=96", timeout=8).json()
        df_k = pd.DataFrame(klines, columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','ig'])
        df_k['c']=df_k['c'].astype(float); df_k['t']=pd.to_datetime(df_k['t'], unit='ms')
    except:
        df_k = pd.DataFrame({'t':[datetime.now()], 'c':[price]})
    try:
        oi = requests.get(f"{BINANCE_FUT}/fapi/v1/openInterest?symbol=BTCUSDT", timeout=8).json()
        oi_now = float(oi.get('openInterest', 54000))
        oi_hist = requests.get(f"{BINANCE_FUT}/futures/data/openInterestHist?symbol=BTCUSDT&period=15m&limit=50", timeout=8).json()
        df_oi = pd.DataFrame(oi_hist); df_oi['sumOpenInterest']=df_oi['sumOpenInterest'].astype(float); df_oi['timestamp']=pd.to_datetime(df_oi['timestamp'], unit='ms')
    except:
        oi_now=54000; df_oi=pd.DataFrame({'timestamp':[datetime.now()], 'sumOpenInterest':[oi_now]})
    try:
        ls = requests.get(f"{BINANCE_FUT}/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=1h&limit=48", timeout=8).json()
        df_ls = pd.DataFrame(ls); df_ls['longShortRatio']=df_ls['longShortRatio'].astype(float); df_ls['timestamp']=pd.to_datetime(df_ls['timestamp'], unit='ms')
    except:
        df_ls=pd.DataFrame({'timestamp':[datetime.now()], 'longShortRatio':[1.15]})
    try:
        funding = requests.get(f"{BINANCE_FUT}/fapi/v1/fundingRate?symbol=BTCUSDT&limit=20", timeout=8).json()
        df_f = pd.DataFrame(funding)
        if df_f.empty or 'fundingRate' not in df_f.columns: raise
    except:
        df_f=pd.DataFrame({'fundingRate':['0.0001'], 'fundingTime':[0]})
    try:
        spot_vol = requests.get(f"{BINANCE_SPOT}/ticker/24hr?symbol=BTCUSDT", timeout=8).json()
        f_vol = requests.get(f"{BINANCE_FUT}/fapi/v1/ticker/24hr?symbol=BTCUSDT", timeout=8).json()
    except:
        spot_vol={'quoteVolume':'1800000000','volume':'15000'}; f_vol={'volume':'32000'}
    return price, df_k, oi_now, df_oi, df_ls, df_f, spot_vol, f_vol

price, df_k, oi_now, df_oi, df_ls, df_f, spot_vol, f_vol = get_data()

c1,c2,c3,c4,c5 = st.columns(5)
c1.markdown(f"<div class='card'><div class='metric-title'>BTC / USD</div><div class='metric-value'>${price:,.0f}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><div class='metric-title'>OPEN INTEREST</div><div class='metric-value'>{oi_now:,.0f}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><div class='metric-title'>LONG / SHORT</div><div class='metric-value'>{float(df_ls.iloc[-1]['longShortRatio']):.2f}</div></div>", unsafe_allow_html=True)
try: fr = float(df_f.iloc[-1]['fundingRate'])*100
except: fr = 0.01
c4.markdown(f"<div class='card'><div class='metric-title'>FUNDING</div><div class='metric-value'>{fr:.4f}%</div></div>", unsafe_allow_html=True)
c5.markdown(f"<div class='card'><div class='metric-title'>FLUXO</div><div class='metric-value'>SPOT</div></div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📈 PANORAMA GERAL", "🎯 COINGLASS PRO"])

with tab1:
    colA, colB = st.columns([2,1])
    with colA:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_k['t'], y=df_k['c'], name="BTC", line=dict(color='white', width=2)))
        fig.add_trace(go.Scatter(x=df_oi['timestamp'], y=df_oi['sumOpenInterest'], name="OI", yaxis="y2", line=dict(color='#f5c518')))
        fig.update_layout(template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", height=360, margin=dict(l=0,r=0,t=10,b=0), yaxis=dict(fixedrange=True), yaxis2=dict(overlaying="y", side="right", fixedrange=True), xaxis=dict(fixedrange=True))
        st.plotly_chart(fig, use_container_width=True, config=CONFIG_PLOTLY_FIXO)
    with colB:
        spot_v = float(spot_vol.get('volume', 15000)); fut_v = float(f_vol.get('volume', 32000))
        fig2 = go.Figure(data=[go.Bar(x=["Spot","Futuros"], y=[spot_v, fut_v], marker_color=["#00d395","#ff4d4d"])])
        fig2.update_layout(template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", height=360, margin=dict(l=0,r=0,t=10,b=0), yaxis=dict(fixedrange=True), xaxis=dict(fixedrange=True))
        st.plotly_chart(fig2, use_container_width=True, config=CONFIG_PLOTLY_FIXO)

with tab2:
    fig3 = go.Figure(go.Scatter(x=df_ls['timestamp'], y=df_ls['longShortRatio'], mode='lines', line=dict(color='#f5c518')))
    fig3.update_layout(template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", height=320, xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True))
    st.plotly_chart(fig3, use_container_width=True, config=CONFIG_PLOTLY_FIXO)

st.caption(f"Gráficos fixos • Última {datetime.now().strftime('%H:%M:%S')} • Auto 60s")
