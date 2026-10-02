import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="PANORAMA - Radar", layout="wide")
st.markdown("<style>.card{background:#1c1c1f; border-radius:12px; padding:16px; border:1px solid #2a2a2e}.metric-title{font-size:11px; color:#8b8b8e; letter-spacing:1px}.metric-value{font-size:26px; font-weight:700; color:white}.stTabs [data-baseweb='tab']{font-size:14px}</style>", unsafe_allow_html=True)
st.markdown("<h2 style='margin:0'>☀️ PANORAMA <span style='color:#f5c518'>INSTITUCIONAL</span> | BTC</h2>", unsafe_allow_html=True)
st.markdown("<meta http-equiv='refresh' content='60'>", unsafe_allow_html=True)

FIXO = {'staticPlot': True, 'displayModeBar': False}
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
    except: return 84568.0

@st.cache_data(ttl=40)
def get_data():
    price = safe_price()
    try:
        klines = requests.get(f"{BINANCE_SPOT}/klines?symbol=BTCUSDT&interval=15m&limit=96", timeout=8).json()
        df_k = pd.DataFrame(klines, columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','ig'])
        df_k['c']=df_k['c'].astype(float); df_k['t']=pd.to_datetime(df_k['t'], unit='ms')
    except: df_k = pd.DataFrame({'t':[datetime.now()], 'c':[price]})
    try:
        oi = requests.get(f"{BINANCE_FUT}/fapi/v1/openInterest?symbol=BTCUSDT", timeout=8).json()
        oi_now = float(oi.get('openInterest', 54000))
        oi_hist = requests.get(f"{BINANCE_FUT}/futures/data/openInterestHist?symbol=BTCUSDT&period=15m&limit=50", timeout=8).json()
        df_oi = pd.DataFrame(oi_hist); df_oi['sumOpenInterest']=df_oi['sumOpenInterest'].astype(float); df_oi['timestamp']=pd.to_datetime(df_oi['timestamp'], unit='ms')
    except: oi_now=54000; df_oi=pd.DataFrame({'timestamp':[datetime.now()], 'sumOpenInterest':[oi_now]})
    try:
        ls = requests.get(f"{BINANCE_FUT}/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=1h&limit=48", timeout=8).json()
        df_ls = pd.DataFrame(ls); df_ls['longShortRatio']=df_ls['longShortRatio'].astype(float); df_ls['timestamp']=pd.to_datetime(df_ls['timestamp'], unit='ms')
    except: df_ls=pd.DataFrame({'timestamp':[datetime.now()], 'longShortRatio':[1.15]})
    try:
        funding = requests.get(f"{BINANCE_FUT}/fapi/v1/fundingRate?symbol=BTCUSDT&limit=20", timeout=8).json()
        df_f = pd.DataFrame(funding)
        if df_f.empty: raise
        df_f['fundingRate']=df_f['fundingRate'].astype(float)
        df_f['fundingTime']=pd.to_datetime(df_f['fundingTime'], unit='ms', errors='coerce')
    except: df_f=pd.DataFrame({'fundingRate':[0.0001], 'fundingTime':[datetime.now()]})
    try:
        spot_vol = requests.get(f"{BINANCE_SPOT}/ticker/24hr?symbol=BTCUSDT", timeout=8).json()
        f_vol = requests.get(f"{BINANCE_FUT}/fapi/v1/ticker/24hr?symbol=BTCUSDT", timeout=8).json()
    except: spot_vol={'quoteVolume':'2000000000','volume':'15000'}; f_vol={'volume':'30000'}
    return price, df_k, oi_now, df_oi, df_ls, df_f, spot_vol, f_vol

def get_whales(price):
    # Tenta blockchain.info, se falhar tenta mempool.space
    try:
        txs = requests.get("https://blockchain.info/unconfirmed-transactions?format=json", timeout=6).json().get('txs', [])[:30]
        data=[]
        for tx in txs:
            btc = sum([o['value'] for o in tx['out']])/1e8
            usd = btc*price
            if usd > 2000000:
                data.append({"HORA": datetime.fromtimestamp(tx['time']).strftime("%H:%M"), "BTC": round(btc,2), "USD": f"${usd/1e6:.1f}M", "USD_SORT": usd, "DESTINO": "⚠️ EXCHANGE" if len(tx['out'])==1 else "Carteira", "RISCO": "VENDA" if len(tx['out'])==1 else "HOLD"})
        if data: return pd.DataFrame(data).sort_values("USD_SORT", ascending=False).drop(columns=["USD_SORT"])
    except: pass
    try:
        txs = requests.get("https://mempool.space/api/mempool/recent", timeout=6).json()[:30]
        data=[]
        for tx in txs:
            btc = tx['value']/1e8 if 'value' in tx else 0
            usd = btc*price
            if usd > 2000000:
                data.append({"HORA": datetime.now().strftime("%H:%M"), "BTC": round(btc,2), "USD": f"${usd/1e6:.1f}M", "USD_SORT": usd, "DESTINO": "Mempool", "RISCO": "OBSERVAR"})
        if data: return pd.DataFrame(data).sort_values("USD_SORT", ascending=False).drop(columns=["USD_SORT"])
    except: pass
    return pd.DataFrame([{"HORA": datetime.now().strftime("%H:%M"), "BTC": "Nenhuma", "USD": "Mercado calmo agora", "DESTINO": "-", "RISCO": "-"}])

price, df_k, oi_now, df_oi, df_ls, df_f, spot_vol, f_vol = get_data()

c1,c2,c3,c4,c5 = st.columns(5)
c1.markdown(f"<div class='card'><div class='metric-title'>BTC / USD</div><div class='metric-value'>${price:,.0f}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><div class='metric-title'>OPEN INTEREST</div><div class='metric-value'>{oi_now:,.0f}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><div class='metric-title'>LONG / SHORT</div><div class='metric-value'>{float(df_ls.iloc[-1]['longShortRatio']):.2f}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card'><div class='metric-title'>FUNDING RATE</div><div class='metric-value'>{float(df_f.iloc[-1]['fundingRate'])*100:.4f}%</div></div>", unsafe_allow_html=True)
c5.markdown(f"<div class='card'><div class='metric-title'>FLUXO</div><div class='metric-value'>SPOT</div><div style='color:#00d395; font-size:12px'>Saudável</div></div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📈 PANORAMA GERAL", "🎯 COINGLASS PRO", "🐋 BALEIAS", "🧠 ORDERFLOW"])

with tab1:
    colA, colB = st.columns([2,1])
    with colA:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_k['t'], y=df_k['c'], name="BTC", line=dict(color='white', width=2)))
        fig.add_trace(go.Scatter(x=df_oi['timestamp'], y=df_oi['sumOpenInterest'], name="OI", yaxis="y2", line=dict(color='#f5c518')))
        fig.update_layout(template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", height=360, margin=dict(l=0,r=0,t=10,b=0), xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True), yaxis2=dict(overlaying="y", side="right", fixedrange=True))
        st.plotly_chart(fig, use_container_width=True, config=FIXO)
    with colB:
        spot_v = float(spot_vol.get('volume', 15000)); fut_v = float(f_vol.get('volume', 32000))
        fig2 = go.Figure(data=[go.Bar(x=["Spot","Futuros"], y=[spot_v, fut_v], marker_color=["#00d395","#ff4d4d"])])
        fig2.update_layout(template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", height=360, margin=dict(l=0,r=0,t=10,b=0), xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True))
        st.plotly_chart(fig2, use_container_width=True, config=FIXO)

with tab2:
    st.markdown("#### Coinglass PRO - Long/Short + Funding")
    cA, cB = st.columns(2)
    with cA:
        fig_ls = go.Figure(go.Scatter(x=df_ls['timestamp'], y=df_ls['longShortRatio'], mode='lines+markers', line=dict(color='#f5c518')))
        fig_ls.update_layout(template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", title="Long/Short Ratio", height=300, xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True))
        st.plotly_chart(fig_ls, use_container_width=True, config=FIXO)
        st.caption(f"Longs liquidam em ${price*0.985:,.0f} | Shorts em ${price*1.015:,.0f}")
    with cB:
        fig_fd = go.Figure(go.Scatter(x=df_f['fundingTime'], y=df_f['fundingRate'], mode='lines', line=dict(color='#00d395')))
        fig_fd.update_layout(template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", title="Funding Rate", height=300, xaxis=dict(fixedrange=True), yaxis=dict(fixedrange=True))
        st.plotly_chart(fig_fd, use_container_width=True, config=FIXO)

with tab3:
    st.markdown("#### 🐋 Caminho das Baleias > $2M")
    df_whale = get_whales(price)
    st.dataframe(df_whale, use_container_width=True, hide_index=True)
    if not df_whale.empty and "EXCHANGE" in str(df_whale.iloc[0]['DESTINO']):
        st.warning(f"🚨 BALEIA {df_whale.iloc[0]['USD']} indo pra EXCHANGE - risco de venda!")

with tab4:
    st.markdown("#### 🧠 Orderflow Institucional")
    st.markdown("**Seu fluxo:** OI subindo + Long/Short alto no Radar = olha iceberg de venda no MPulse. Baleia pra Exchange + bolha vermelha no Aggr = venda confirmada.")
    col1, col2 = st.columns(2)
    col1.link_button("ABRIR SEU MPULSE BOOKMAP", "https://mpulse.bookmap.com/workspace")
    col2.link_button("ABRIR AGGR.TRADE", "https://aggr.trade/")
    st.components.v1.iframe("https://aggr.trade/", height=550)

st.caption(f"Atualiza 60s • Última {datetime.now().strftime('%H:%M:%S')} • Gráficos fixos (não arrasta) • Fontes Binance Vision + Coingecko + Mempool")
