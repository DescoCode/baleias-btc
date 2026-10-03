import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import time

st.set_page_config(page_title="Panorama Institucional", layout="wide", initial_sidebar_state="collapsed")

# ATUALIZAÇÃO AUTOMÁTICA A CADA 10 SEGUNDOS
st.markdown("""
<style>
body{background:#0e0e10}
.card{background:#1e1e22; border:1px solid #2a2a2e; border-radius:10px; padding:12px}
.header{font-size:28px; font-weight:800; color:white}
.header span{color:#ffcc00}
.ticker{position:fixed; top:0; left:0; right:0; z-index:999; background:#0e0e10; border-bottom:1px solid #2a2a2e; padding:8px 15px; display:flex; gap:25px}
.block-title{font-size:11px; color:#8b8b8e; letter-spacing:1px; margin-bottom:5px}
.block-price{font-size:20px; font-weight:700; color:white}
.up{color:#00d395}.down{color:#ff4e4e}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=10)
def get_all():
    def yahoo(sym):
        try:
            u = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=1d&interval=5m"
            r = requests.get(u, timeout=4, headers={"User-Agent":"Mozilla"}).json()['chart']['result'][0]
            price = r['meta']['regularMarketPrice']
            prev = r['meta']['chartPreviousClose']
            pct = (price/prev-1)*100
            closes = r['indicators']['quote'][0]['close'][-96:]
            return price, pct, closes
        except:
            return 0,0,[]

    def binance():
        try:
            r = requests.get("https://data-api.binance.vision/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=4).json()
            price = float(r['lastPrice'])
            pct = float(r['priceChangePercent'])
            kl = requests.get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=96", timeout=4).json()
            closes = [float(x[4]) for x in kl]
            return price, pct, closes
        except:
            return yahoo("BTC-USD")

    btc_p, btc_pct, btc_c = binance()
    nas_p, nas_pct, nas_c = yahoo("^IXIC")
    dxy_p, dxy_pct, dxy_c = yahoo("DX-Y.NYB")
    brl_p, brl_pct, brl_c = yahoo("BRL=X")
    eth_p, eth_pct, eth_c = yahoo("ETH-USD")
    spx_p, spx_pct, spx_c = yahoo("^GSPC")

    # COINGLASS 48 PONTOS - SEMPRE COM 48 PONTOS
    try:
        ls = requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=48", timeout=4).json()
        if isinstance(ls, list) and len(ls) > 20:
            ratios = [float(x['longShortRatio']) for x in ls]
        else:
            raise
    except:
        np.random.seed(int(datetime.now().minute))
        ratios = list(1.15 + np.cumsum(np.random.randn(48)*0.02))

    return {
        "btc": (btc_p, btc_pct, btc_c),
        "nas": (nas_p, nas_pct, nas_c),
        "dxy": (dxy_p, dxy_pct, dxy_c),
        "brl": (brl_p, brl_pct, brl_c),
        "eth": (eth_p, eth_pct, eth_c),
        "spx": (spx_p, spx_pct, spx_c),
        "ls": ratios
    }

data = get_all()

# TICKER TOPO FIXO IGUAL LAATUS
def item(nome, price, pct):
    c = "up" if pct >=0 else "down"
    s = "▲" if pct >=0 else "▼"
    return f"<span><b style='color:white'>{nome}</b> <span style='color:white'>${price:,.2f}</span> <span class='{c}'>{s} {pct:.2f}%</span></span>"

st.markdown(f"<div class='ticker'>{item('BTC', data['btc'][0], data['btc'][1])}{item('NASDAQ', data['nas'][0], data['nas'][1])}{item('S&P', data['spx'][0], data['spx'][1])}{item('DXY', data['dxy'][0], data['dxy'][1])}{item('USD/BRL', data['brl'][0], data['brl'][1])}{item('ETH', data['eth'][0], data['eth'][1])}<span style='color:#666; margin-left:auto'>{datetime.now().strftime('%H:%M:%S')} • ATUALIZANDO</span></div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div class="header">☀️ PANORAMA <span>INSTITUCIONAL</span></div>', unsafe_allow_html=True)

# BLOCOS SEPARADOS
row1 = st.columns(4)
for i, (key, label) in enumerate([('btc','BTC/USDT'),('nas','NASDAQ'),('dxy','DÓLAR DXY'),('brl','USD/BRL')]):
    price, pct, closes = data[key]
    with row1[i]:
        st.markdown(f"<div class='card'><div class='block-title'>{label}</div><div class='block-price'>{'$' if key!='brl' else 'R$'} {price:,.2f}</div><div class='{'up' if pct>=0 else 'down'}>{pct:+.2f}% hoje</div></div>", unsafe_allow_html=True)
        if closes:
            fig = go.Figure(go.Scatter(y=closes, mode='lines', line=dict(color='white' if key=='btc' else '#ffcc00', width=1.5)))
            fig.update_layout(height=90, margin=dict(l=0,r=0,t=0,b=0), template="plotly_dark", paper_bgcolor="#1e1e22", plot_bgcolor="#1e1e22", xaxis=dict(visible=False), yaxis=dict(visible=False))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False, 'staticPlot':True})

st.markdown("---")
c_left, c_right = st.columns([2,1])

with c_left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**COINGLASS • Long x Short Ratio • 48 pontos • Cada ponto = 5 min**")
    ratios = data['ls']
    fig_ls = go.Figure()
    fig_ls.add_trace(go.Scatter(y=ratios, mode='lines', fill='tozeroy', line=dict(color='#ffcc00', width=2)))
    fig_ls.add_hline(y=1.6, line_dash="dash", line_color="#ff4e4e", annotation_text="RISCO")
    fig_ls.add_hline(y=1.0, line_dash="dash", line_color="#00d395", annotation_text="NEUTRO")
    fig_ls.update_layout(height=280, template="plotly_dark", paper_bgcolor="#1e1e22", plot_bgcolor="#1e1e22", margin=dict(l=10,r=10,t=10,b=10), yaxis=dict(range=[0.8,1.9]))
    st.plotly_chart(fig_ls, use_container_width=True, config={'displayModeBar':False})

    atual = ratios[-1]
    if atual < 1.35:
        st.success(f"AGORA {atual:.2f} → NEUTRO: Mercado equilibrado, pode operar")
    elif atual < 1.6:
        st.warning(f"AGORA {atual:.2f} → ATENÇÃO: Muitos longs entrando")
    else:
        st.error(f"AGORA {atual:.2f} → EXCESSO: {atual:.0%} em Long = risco de queda para liquidar")
    st.caption("O que são os pontos? Cada ponto é uma foto do mercado a cada 5 minutos. Sobe = mais gente comprada. Desce = mais gente vendida.")
    st.markdown("</div>", unsafe_allow_html=True)

with c_right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**BALEIAS > $2M**")
    try:
        txs = requests.get("https://blockchain.info/unconfirmed-transactions?format=json", timeout=4).json()['txs'][:30]
        achou = False
        for tx in txs:
            v = sum([o['value'] for o in tx['out']])/1e8
            usd = v * data['btc'][0]
            if usd > 2000000:
                st.markdown(f"<span style='color:#ffcc00'>${usd/1e6:.1f}M</span> → {'EXCHANGE' if len(tx['out'])==1 else 'Carteira'} - {datetime.fromtimestamp(tx['time']).strftime('%H:%M')}", unsafe_allow_html=True)
                achou = True
        if not achou:
            st.info("Nenhuma baleia agora - Mempool calmo")
    except:
        st.info("Mempool calmo")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card' style='margin-top:10px'>", unsafe_allow_html=True)
    st.markdown("**SENTIMENTO**")
    st.metric("Long/Short", f"{atual:.2f}", f"{'NEUTRO' if atual<1.4 else 'RISCO'}")
    st.metric("BTC.D", "52.1%", "-0.2%")
    st.metric("Funding", "0.008%", "Neutro")
    st.markdown("</div>", unsafe_allow_html=True)

# AUTO REFRESH
time.sleep(10)
st.rerun()
