import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="PANORAMA - Radar", layout="wide", initial_sidebar_state="collapsed")

# CSS ESTILO LAATUS PANORAMA
st.markdown("""
<style>
body {background-color:#0e0e10}
.card {
  background:#1c1c1f; border-radius:12px; padding:16px; border:1px solid #2a2a2e;
}
.metric-title {font-size:13px; color:#8b8b8e; letter-spacing:1px}
.metric-value {font-size:28px; font-weight:700; color:white}
.metric-sub {font-size:12px}
.green {color:#00d395}.red {color:#ff4d4d}.yellow {color:#f5c518}
.stTabs [data-baseweb="tab"] {font-size:16px}
</style>
""", unsafe_allow_html=True)

# Header Laatus
st.markdown("""
<div style='display:flex; justify-content:space-between; align-items:center;'>
<h2 style='margin:0'>☀️ PANORAMA <span style='color:#f5c518'>INSTITUCIONAL</span> | BTC</h2>
<p style='color:#8b8b8e'>RADAR COINGLASS • BOOKMAP • AGGR • BALEIAS</p>
</div>
""", unsafe_allow_html=True)
st.markdown("<meta http-equiv='refresh' content='60'>", unsafe_allow_html=True)

BINANCE_SPOT = "https://data-api.binance.vision/api/v3"
BINANCE_FUT = "https://fapi.binance.com"

def safe_price():
    try:
        r = requests.get(f"{BINANCE_SPOT}/ticker/price?symbol=BTCUSDT", timeout=8).json()
        if 'price' in r: return float(r['price'])
    except: pass
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=8).json()
        return float(r['bitcoin']['usd'])
    except: return 115000.0

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
        oi_now = float(oi.get('openInterest', 50000))
        oi_hist = requests.get(f"{BINANCE_FUT}/futures/data/openInterestHist?symbol=BTCUSDT&period=15m&limit=50", timeout=8).json()
        df_oi = pd.DataFrame(oi_hist)
        df_oi['sumOpenInterest']=df_oi['sumOpenInterest'].astype(float)
        df_oi['timestamp']=pd.to_datetime(df_oi['timestamp'], unit='ms')
    except:
        oi_now=54000; df_oi=pd.DataFrame({'timestamp':[datetime.now()], 'sumOpenInterest':[oi_now]})
    try:
        ls = requests.get(f"{BINANCE_FUT}/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=1h&limit=48", timeout=8).json()
        df_ls = pd.DataFrame(ls)
        df_ls['longShortRatio']=df_ls['longShortRatio'].astype(float)
        df_ls['timestamp']=pd.to_datetime(df_ls['timestamp'], unit='ms')
    except:
        df_ls=pd.DataFrame({'timestamp':[datetime.now()], 'longShortRatio':[1.15]})
    try:
        funding = requests.get(f"{BINANCE_FUT}/fapi/v1/fundingRate?symbol=BTCUSDT&limit=20", timeout=8).json()
        df_f = pd.DataFrame(funding)
    except:
        df_f=pd.DataFrame({'fundingRate':['0.0001']})
    try:
        spot_vol = requests.get(f"{BINANCE_SPOT}/ticker/24hr?symbol=BTCUSDT", timeout=8).json()
        f_vol = requests.get(f"{BINANCE_FUT}/fapi/v1/ticker/24hr?symbol=BTCUSDT", timeout=8).json()
    except:
        spot_vol={'quoteVolume':'1800000000','volume':'15000','priceChangePercent':'2.1'}; f_vol={'volume':'32000'}
    return price, df_k, oi_now, df_oi, df_ls, df_f, spot_vol, f_vol

price, df_k, oi_now, df_oi, df_ls, df_f, spot_vol, f_vol = get_data()

# === CARDS ESTILO PANORAMA ===
ls_ratio = float(df_ls.iloc[-1]['longShortRatio'])
try: funding_rate = float(df_f.iloc[-1]['fundingRate'])*100
except: funding_rate = 0.01

# semáforos
sinal_ls = "green" if 0.9 < ls_ratio < 1.4 else "red"
sinal_fund = "green" if funding_rate < 0.02 else "red"
spot_v = float(spot_vol.get('volume', 15000)); fut_v = float(f_vol.get('volume', 30000))
sinal_vol = "green" if spot_v > fut_v*0.6 else "red"

c1,c2,c3,c4,c5 = st.columns(5)
with c1:
    st.markdown(f"<div class='card'><div class='metric-title'>BTC / USD</div><div class='metric-value'>${price:,.0f}</div><div class='metric-sub {sinal_vol}'>Vol 24h ${float(spot_vol.get('quoteVolume',0))/1e9:.2f}B</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='card'><div class='metric-title'>OPEN INTEREST</div><div class='metric-value'>{oi_now:,.0f}</div><div class='metric-sub yellow'>Futuros em aberto</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='card'><div class='metric-title'>LONG / SHORT</div><div class='metric-value'>{ls_ratio:.2f}</div><div class='metric-sub {sinal_ls}'>{'Neutro' if sinal_ls=='green' else 'Excesso Longs! Risco'}</div></div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='card'><div class='metric-title'>FUNDING RATE</div><div class='metric-value'>{funding_rate:.4f}%</div><div class='metric-sub {sinal_fund}'>{'Neutro' if sinal_fund=='green' else 'Longs pagando muito'}</div></div>", unsafe_allow_html=True)
with c5:
    st.markdown(f"<div class='card'><div class='metric-title'>FLUXO</div><div class='metric-value'>{'SPOT' if sinal_vol=='green' else 'FUTURO'}</div><div class='metric-sub {sinal_vol}'>{'Saudável' if sinal_vol=='green' else 'Especulativo'}</div></div>", unsafe_allow_html=True)

# GRAFICOS
tab1, tab2, tab3, tab4 = st.tabs(["📈 PANORAMA GERAL", "🎯 COINGLASS PRO", "🐋 BALEIAS", "🧠 ORDERFLOW"])

with tab1:
    colA, colB = st.columns([2,1])
    with colA:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_k['t'], y=df_k['c'], name="BTC Preço", line=dict(color='white', width=2)))
        fig.add_trace(go.Scatter(x=df_oi['timestamp'], y=df_oi['sumOpenInterest'], name="OI", yaxis="y2", line=dict(color='#f5c518')))
        fig.update_layout(template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f",
                           height=380, margin=dict(l=0,r=0,t=10,b=0),
                           yaxis=dict(title="Preço"), yaxis2=dict(overlaying="y", side="right", title="OI"))
        st.plotly_chart(fig, use_container_width=True)
    with colB:
        fig2 = go.Figure(data=[go.Bar(x=["Spot","Futuros"], y=[spot_v, fut_v], marker_color=["#00d395","#ff4d4d"])])
        fig2.update_layout(template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", height=380, margin=dict(l=0,r=0,t=10,b=0), title="Spot vs Futuros - Quem lidera?")
        st.plotly_chart(fig2, use_container_width=True)
        if fut_v > spot_v*2:
            st.error("⚠️ Alerta Panorama: Futuros dominando = topo de liquidação")
        else:
            st.success("✅ Panorama saudável: Spot liderando")

with tab2:
    c1,c2 = st.columns(2)
    c1.plotly_chart(go.Figure(go.Scatter(x=df_ls['timestamp'], y=df_ls['longShortRatio'], mode='lines+markers', line=dict(color='#f5c518'))).update_layout(template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", title="Long/Short Ratio - Coinglass", height=320), use_container_width=True)
    c2.plotly_chart(go.Figure(go.Scatter(x=pd.to_datetime(df_f['fundingTime'], unit='ms', errors='coerce'), y=df_f['fundingRate'].astype(float), mode='lines', line=dict(color='#00d395'))).update_layout(template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", title="Funding Rate", height=320), use_container_width=True)

with tab3:
    st.markdown("### 🐋 Caminho das Baleias > $3M")
    try:
        txs = requests.get("https://blockchain.info/unconfirmed-transactions?format=json", timeout=8).json().get('txs', [])[:25]
        data=[]
        for tx in txs:
            btc = sum([o['value'] for o in tx['out']])/1e8
            usd = btc*price
            if usd > 3000000:
                data.append({"HORA": datetime.fromtimestamp(tx['time']).strftime("%H:%M"), "BTC": f"{btc:.1f}", "USD": f"${usd/1e6:.1f}M", "DESTINO": "⚠️ EXCHANGE" if len(tx['out'])==1 else "Carteira fria", "RISCO": "VENDA" if len(tx['out'])==1 else "HOLD"})
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info("Nenhuma baleia grande agora - mercado calmo")
    except:
        st.info("Mempool calmo")

with tab4:
    st.markdown("[MPULSE BOOKMAP](https://mpulse.bookmap.com/workspace) • [AGGR.TRADE](https://aggr.trade/)")
    st.components.v1.iframe("https://aggr.trade/", height=600)

st.caption(f"Atualiza a cada 60s • Última {datetime.now().strftime('%H:%M:%S')} • Fonte direta Binance Vision + Blockchain • Estilo Laatus Panorama")
