import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

st.set_page_config(page_title="RADAR INSTITUCIONAL", layout="wide")
st.title("🐋 RADAR INSTITUCIONAL - Coinglass + Bookmap + Aggr")

@st.cache_data(ttl=45)
def get_data():
    price = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=10).json()['price'])
    klines = requests.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=96", timeout=10).json()
    df_k = pd.DataFrame(klines, columns=['t','o','h','l','c','v','ct','qv','n','tb','tq','ig'])
    df_k['c'] = df_k['c'].astype(float); df_k['v'] = df_k['v'].astype(float)
    df_k['t'] = pd.to_datetime(df_k['t'], unit='ms')

    oi = requests.get("https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT", timeout=10).json()
    oi_hist = requests.get("https://fapi.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=15m&limit=50", timeout=10).json()
    df_oi = pd.DataFrame(oi_hist); df_oi['sumOpenInterest'] = df_oi['sumOpenInterest'].astype(float)
    df_oi['timestamp'] = pd.to_datetime(df_oi['timestamp'], unit='ms')

    ls = requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=1h&limit=50", timeout=10).json()
    df_ls = pd.DataFrame(ls); df_ls['longShortRatio'] = df_ls['longShortRatio'].astype(float)
    df_ls['timestamp'] = pd.to_datetime(df_ls['timestamp'], unit='ms')

    funding = requests.get("https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=20", timeout=10).json()
    df_f = pd.DataFrame(funding)

    spot_vol = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=10).json()
    f_vol = requests.get("https://fapi.binance.com/fapi/v1/ticker/24hr?symbol=BTCUSDT", timeout=10).json()

    return price, df_k, float(oi['openInterest']), df_oi, df_ls, df_f, spot_vol, f_vol

price, df_k, oi_now, df_oi, df_ls, df_f, spot_vol, f_vol = get_data()

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("BTC", f"${price:,.0f}")
c2.metric("Open Interest", f"{oi_now:,.0f} BTC")
c3.metric("Funding", f"{float(df_f.iloc[-1].fundingRate)*100:.4f}%")
c4.metric("Long/Short", f"{df_ls.iloc[-1].longShortRatio:.2f}")
c5.metric("Vol Spot 24h", f"${float(spot_vol['quoteVolume'])/1e9:.2f}B")

tab1, tab2, tab3, tab4 = st.tabs(["📊 SPOT x FUTURO + OI", "🔥 LIQUIDAÇÕES COINGLASS", "🐋 BALEIAS - CAMINHO", "🧠 BOOKMAP + AGGR.TRADE"])

with tab1:
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Preço + Open Interest")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_k['t'], y=df_k['c'], name="BTC Preço", yaxis="y1"))
        fig.add_trace(go.Scatter(x=df_oi['timestamp'], y=df_oi['sumOpenInterest'], name="OI", yaxis="y2", line=dict(color='orange')))
        fig.update_layout(yaxis=dict(title="Preço"), yaxis2=dict(title="OI", overlaying="y", side="right"), height=400, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)
    with colB:
        st.subheader("Volume Spot vs Futuro")
        spot_v = float(spot_vol['volume']); fut_v = float(f_vol['volume'])
        fig2 = go.Figure(data=[go.Bar(x=["Spot","Futuros"], y=[spot_v, fut_v], marker_color=["green","red"])])
        fig2.update_layout(height=400, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig2, use_container_width=True)
        if fut_v > spot_v*2:
            st.error("⚠️ FUTUROS 2x maior que SPOT: Risco de liquidação!")
        else:
            st.success("Spot liderando - saudável")

with tab2:
    st.subheader("Coinglass - Long x Short + Funding")
    c1,c2 = st.columns(2)
    c1.plotly_chart(go.Figure(go.Scatter(x=df_ls['timestamp'], y=df_ls['longShortRatio'], mode='lines+markers')).update_layout(title="Long/Short Ratio", height=300), use_container_width=True)
    c2.plotly_chart(go.Figure(go.Scatter(x=pd.to_datetime(df_f['fundingTime'], unit='ms'), y=df_f['fundingRate'].astype(float), mode='lines')).update_layout(title="Funding Rate", height=300), use_container_width=True)
    st.info(f"Longs liquidam em: ${price*0.985:,.0f} / ${price*0.97:,.0f} | Shorts liquidam em: ${price*1.015:,.0f} / ${price*1.03:,.0f}")

with tab3:
    st.subheader("Caminho das Baleias > $5M")
    try:
        txs = requests.get("https://blockchain.info/unconfirmed-transactions?format=json", timeout=10).json()['txs'][:30]
        data=[]
        for tx in txs:
            btc = sum([o['value'] for o in tx['out']])/1e8
            usd = btc*price
            if usd > 5000000:
                data.append({"Hora": datetime.fromtimestamp(tx['time']).strftime("%H:%M"), "BTC": round(btc,1), "USD": f"${usd/1e6:.1f}M", "USD_raw": usd, "Para": "Exchange" if len(tx['out'])==1 else f"{len(tx['out'])} wallets", "Risco": "VENDA" if len(tx['out'])==1 else "HOLD"})
        df_w = pd.DataFrame(data).sort_values("USD_raw", ascending=False) if data else pd.DataFrame()
        if not df_w.empty:
            st.dataframe(df_w.drop(columns=['USD_raw']), use_container_width=True)
            if df_w.iloc[0]['Risco']=="VENDA":
                st.warning(f"🚨 BALEIA {df_w.iloc[0]['USD']} indo pra EXCHANGE!")
        else:
            st.success("Sem baleias > $5M agora")
    except:
        st.write("API mempool instável no momento")

with tab4:
    st.subheader("Seu fluxo institucional")
    st.markdown("[ABRIR SEU BOOKMAP MPULSE](https://mpulse.bookmap.com/workspace) | [ABRIR AGGR.TRADE](https://aggr.trade/)")
    st.markdown("**Como usar:** OI subindo + Long/Short >1.6 no radar = olha iceberg de venda no MPulse. Baleia pra Exchange no radar + bolha vermelha grande no Aggr = venda confirmada.")
    st.components.v1.iframe("https://aggr.trade/", height=550)

st.divider()

# --- FONTES + AUTO UPDATE ---
st.markdown("""
**📡 Fontes diretas (sem pagar Coinglass):**
- `api.binance.com` = Spot
- `fapi.binance.com` = Open Interest, Long/Short, Funding, Volume Futuros (mesmo dado que Coinglass PRO)
- `blockchain.info` = Baleias mempool
""")

if st.button("📲 TESTAR NOTIFICAÇÃO"):
    try:
        requests.post("https://ntfy.sh/baleias-btc-descocode", data=f"🐋 BTC ${price:.0f} | OI {oi_now:.0f} | LS {df_ls.iloc[-1].longShortRatio:.2f}".encode(), timeout=5)
        st.toast("Enviado! Olha seu ntfy")
    except:
        st.error("Erro ntfy")

# CONTADOR AUTO UPDATE
st.markdown("---")
placeholder = st.empty()
for i in range(45, 0, -1):
    placeholder.caption(f"🔄 Atualiza sozinho em {i}s | Última atualização: {datetime.now().strftime('%H:%M:%S')} - Fontes: Binance + Blockchain - ao vivo")
    time.sleep(1)
placeholder.caption("🔄 Atualizando...")
st.rerun()
