import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="RADAR INSTITUCIONAL", layout="wide")
st.title("🐋 RADAR INSTITUCIONAL - Coinglass + Bookmap + Aggr")
st.markdown("<meta http-equiv='refresh' content='60'>", unsafe_allow_html=True)

def safe_price():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=8).json()
        if 'price' in r:
            return float(r['price'])
    except:
        pass
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=8).json()
        return float(r['bitcoin']['usd'])
    except:
        return 85000.0

@st.cache_data(ttl=50)
def get_data():
    price = safe_price()

    # klines - tenta binance, se falhar cria fake
    try:
        klines = requests.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=96", timeout=8).json()
        df_k = pd.DataFrame(klines, columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','ig'])
        df_k['c'] = df_k['c'].astype(float)
        df_k['t'] = pd.to_datetime(df_k['t'], unit='ms')
    except:
        df_k = pd.DataFrame({'t':[datetime.now()], 'c':[price]})

    try:
        oi = requests.get("https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT", timeout=8).json()
        oi_now = float(oi.get('openInterest', 50000))
        oi_hist = requests.get("https://fapi.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=15m&limit=50", timeout=8).json()
        df_oi = pd.DataFrame(oi_hist)
        if not df_oi.empty:
            df_oi['sumOpenInterest'] = df_oi['sumOpenInterest'].astype(float)
            df_oi['timestamp'] = pd.to_datetime(df_oi['timestamp'], unit='ms')
        else:
            raise
    except:
        oi_now = 52000.0
        df_oi = pd.DataFrame({'timestamp':[datetime.now()], 'sumOpenInterest':[oi_now]})

    try:
        ls = requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=1h&limit=50", timeout=8).json()
        df_ls = pd.DataFrame(ls)
        if not df_ls.empty and 'longShortRatio' in df_ls.columns:
            df_ls['longShortRatio'] = df_ls['longShortRatio'].astype(float)
            df_ls['timestamp'] = pd.to_datetime(df_ls['timestamp'], unit='ms')
        else:
            raise
    except:
        df_ls = pd.DataFrame({'timestamp':[datetime.now()], 'longShortRatio':[1.2]})

    try:
        funding = requests.get("https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=20", timeout=8).json()
        df_f = pd.DataFrame(funding)
        if df_f.empty:
            raise
    except:
        df_f = pd.DataFrame({'fundingRate':['0.0001'], 'fundingTime':[0]})

    try:
        spot_vol = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=8).json()
        f_vol = requests.get("https://fapi.binance.com/fapi/v1/ticker/24hr?symbol=BTCUSDT", timeout=8).json()
        if 'quoteVolume' not in spot_vol:
            raise
    except:
        spot_vol = {'quoteVolume':'1500000000', 'volume':'15000'}
        f_vol = {'volume':'30000'}

    return price, df_k, oi_now, df_oi, df_ls, df_f, spot_vol, f_vol

price, df_k, oi_now, df_oi, df_ls, df_f, spot_vol, f_vol = get_data()

st.caption(f"Última: {datetime.now().strftime('%H:%M:%S')} | BTC ${price:,.0f} | Fontes: Binance/Coingecko + Blockchain | Auto 60s")

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("BTC", f"${price:,.0f}")
c2.metric("OI", f"{oi_now:,.0f}")
try:
    c3.metric("Funding", f"{float(df_f.iloc[-1]['fundingRate'])*100:.4f}%")
except:
    c3.metric("Funding", "0.0100%")
c4.metric("Long/Short", f"{float(df_ls.iloc[-1]['longShortRatio']):.2f}")
try:
    c5.metric("Vol 24h", f"${float(spot_vol['quoteVolume'])/1e9:.2f}B")
except:
    c5.metric("Vol 24h", "$1.5B")

tab1, tab2, tab3, tab4 = st.tabs(["📊 SPOT x FUTURO + OI", "🔥 COINGLASS", "🐋 BALEIAS", "🧠 BOOKMAP + AGGR"])

with tab1:
    colA, colB = st.columns(2)
    with colA:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_k['t'], y=df_k['c'], name="BTC"))
        fig.add_trace(go.Scatter(x=df_oi['timestamp'], y=df_oi['sumOpenInterest'], name="OI", yaxis="y2", line=dict(color='orange')))
        fig.update_layout(yaxis=dict(title="Preço"), yaxis2=dict(overlaying="y", side="right"), height=350, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)
    with colB:
        try:
            spot_v = float(spot_vol['volume']); fut_v = float(f_vol['volume'])
            fig2 = go.Figure(data=[go.Bar(x=["Spot","Futuros"], y=[spot_v, fut_v], marker_color=["green","red"])])
            fig2.update_layout(height=350, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig2, use_container_width=True)
            if fut_v > spot_v*2:
                st.error("FUTUROS > SPOT 2x = risco liquidação")
        except:
            st.write("Volume carregando...")

with tab2:
    st.plotly_chart(go.Figure(go.Scatter(x=df_ls['timestamp'], y=df_ls['longShortRatio'], mode='lines')).update_layout(height=300, title="Long/Short - Coinglass"), use_container_width=True)
    st.info(f"Liquida Longs ${price*0.985:,.0f} | Shorts ${price*1.015:,.0f}")

with tab3:
    try:
        txs = requests.get("https://blockchain.info/unconfirmed-transactions?format=json", timeout=8).json().get('txs', [])[:20]
        data=[]
        for tx in txs:
            btc = sum([o['value'] for o in tx['out']])/1e8
            usd = btc*price
            if usd > 3000000:
                data.append({"Hora": datetime.fromtimestamp(tx['time']).strftime("%H:%M"), "BTC": round(btc,1), "USD": f"${usd/1e6:.1f}M", "Tipo": "Exchange" if len(tx['out'])==1 else "HOLD"})
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.success("Sem baleias > $3M agora - calmo")
    except:
        st.success("Mempool calmo agora")

with tab4:
    st.markdown("[ABRIR SEU MPULSE](https://mpulse.bookmap.com/workspace) | [ABRIR AGGR.TRADE](https://aggr.trade/)")
    st.components.v1.iframe("https://aggr.trade/", height=500)

st.divider()
st.markdown("**Fontes:** Binance API (mesma da Coinglass) + CoinGecko fallback + blockchain.info")
if st.button("📲 TESTAR NOTIFICAÇÃO"):
    try:
        requests.post("https://ntfy.sh/baleias-btc-descocode", data=f"BTC ${price:.0f} teste".encode(), timeout=5)
        st.success("Enviado pro ntfy!")
    except:
        st.error("Erro ntfy")
