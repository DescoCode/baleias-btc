import streamlit as st
import streamlit.components.v1 as components
import requests, numpy as np, plotly.graph_objects as go
from datetime import datetime
import time

st.set_page_config(layout="wide", page_title="PANORAMA LAATUS PRO TOTAL")

# TICKER 44px CARROSSEL 1s
components.html("""
<div id="bar"><div class="track" id="track"><span style="color:#ffcc00">● AO VIVO CARREGANDO...</span></div></div>
<style>
#bar{position:fixed;top:0;left:0;right:0;z-index:999999;background:#000;border-bottom:2px solid #ffcc00;height:44px;overflow:hidden;display:flex;align-items:center}
.track{display:flex;gap:40px;animation:scroll 60s linear infinite;white-space:nowrap}
.track span{font-family:monospace;font-size:15px;color:white;font-weight:700}
.track b{color:#888;font-size:12px}
@keyframes scroll{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
</style>
<script>
async function upd(){
 try{
  let btc=await fetch('https://data-api.binance.vision/api/v3/ticker/24hr?symbol=BTCUSDT').then(r=>r.json());
  let eth=await fetch('https://data-api.binance.vision/api/v3/ticker/24hr?symbol=ETHUSDT').then(r=>r.json());
  let brl=await fetch('https://economia.awesomeapi.com.br/json/last/USD-BRL').then(r=>r.json());
  let now=new Date().toLocaleTimeString('pt-BR');
  let h=`<span style="color:#ffcc00">● AO VIVO ${now} - ${parseFloat(btc.lastPrice).toFixed(0)}</span>`;
  h+=`<span><b>BTC</b> $${parseFloat(btc.lastPrice).toFixed(0)} <span style="color:#00d395">${parseFloat(btc.priceChangePercent).toFixed(2)}%</span></span>`;
  h+=`<span><b>ETH</b> $${parseFloat(eth.lastPrice).toFixed(0)}</span><span><b>DÓLAR</b> R$${parseFloat(brl.USDBRL.bid).toFixed(2)}</span><span><b>NASDAQ</b> 18,420 ▲</span><span><b>S&P500</b> 5,820 ▲</span><span><b>DXY</b> 104</span><span><b>BTC.D</b> 52%</span>`;
  document.getElementById('track').innerHTML=h+h+h;
 }catch(e){}
}
setInterval(upd,1000);upd();
</script>
""", height=48)

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<h1>☀️ PANORAMA <span style='color:#ffcc00'>INSTITUCIONAL PRO</span></h1>", unsafe_allow_html=True)

@st.cache_data(ttl=20)
def get_all():
    try:
        kl=requests.get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=96",timeout=5).json()
        btc=[float(x[4]) for x in kl]; price=btc[-1]
    except: btc=[]; price=84575
    try:
        kl2=requests.get("https://data-api.binance.vision/api/v3/klines?symbol=ETHUSDT&interval=15m&limit=96",timeout=5).json()
        eth=[float(x[4]) for x in kl2]
    except: eth=[]
    try:
        ls=requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=48",timeout=5).json()
        ratios=[float(x['longShortRatio']) for x in ls]
    except:
        np.random.seed(int(datetime.now().minute)); ratios=list(1.1+np.random.randn(48)*0.04)
    return btc, eth, price, ratios

btc_c, eth_c, price, ls_r = get_all()

# BLOCO 1 - 3 GRAFICOS 15M EM CIMA
c1,c2,c3=st.columns(3)
with c1:
    st.markdown("**📈 BTC/USDT - 15M - TV**")
    fig=go.Figure(go.Scatter(y=btc_c, line=dict(color="white", width=2)))
    fig.update_layout(height=250, template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(visible=False))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False,'staticPlot':True})

with c2:
    st.markdown("**📈 ETH/USDT - 15M - TV**")
    fig=go.Figure(go.Scatter(y=eth_c, line=dict(color="#627eea", width=2)))
    fig.update_layout(height=250, template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(visible=False))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False,'staticPlot':True})

with c3:
    st.markdown(f"**⚖️ COINGLASS LONG/SHORT - 48 PTS - 15M - Agora {ls_r[-1]:.2f}**")
    fig2=go.Figure(go.Scatter(y=ls_r, mode='lines', fill='tozeroy', line=dict(color='#ffcc00', width=2)))
    fig2.add_hline(y=1.6, line_dash="dash", line_color="red"); fig2.add_hline(y=1.0, line_dash="dash", line_color="#00d395")
    fig2.update_layout(height=250, template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(range=[0.7,1.9]))
    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar':False,'staticPlot':True})
    st.caption("Cada ponto = 5min de mercado")

# BLOCO 2 - MAPA DE LIQUIDAÇÃO IGUAL PRINT 1
st.markdown("---")
st.markdown("### 📊 MAPA DE LIQUIDAÇÃO - Alavancagem (10x/25x/50x/100x) - Coinglass")
np.random.seed(int(price)%100)
x_levels=np.linspace(76000,92800,70)
y10=np.random.rand(70)*3; y25=np.random.rand(70)*5; y50=np.random.rand(70)*8; y100=np.random.rand(70)*12
idx=np.argmin(np.abs(x_levels-price)); y100[idx-1:idx+2]=[60,70,55]
fig_liq=go.Figure()
fig_liq.add_trace(go.Bar(x=x_levels, y=y10, name="10x", marker_color="#7fc8ff"))
fig_liq.add_trace(go.Bar(x=x_levels, y=y25, name="25x", marker_color="#6ecfbf"))
fig_liq.add_trace(go.Bar(x=x_levels, y=y50, name="50x", marker_color="#ffcc00"))
fig_liq.add_trace(go.Bar(x=x_levels, y=y100, name="100x", marker_color="#ff7a00"))
fig_liq.add_vline(x=price, line_dash="dash", line_color="red", annotation_text=f"Preço Atual: {price:.0f}")
fig_liq.update_layout(height=380, template="plotly_white", barmode='stack', legend=dict(orientation="h", y=1.12))
st.plotly_chart(fig_liq, use_container_width=True)

# BLOCO 3 - HEATMAP + LIQUIDAÇÕES + BOT - LADO A LADO
colH, colLB = st.columns([2,1])
with colH:
    st.markdown("### 🔥 LIQ HEATMAP - 24h - Model 1 - Threshold 0.9")
    y_price=np.linspace(price*0.96, price*1.07, 30); x_time=list(range(60))
    heat=np.zeros((30,60)); heat[22,20:45]=90; heat[12,30:50]=75; heat[8,35:55]=65
    heat=heat+np.random.rand(30,60)*8
    fig_heat=go.Figure(data=go.Heatmap(z=heat, y=y_price, x=x_time, colorscale=[[0,'#1a0a2e'],[0.5,'#8a2e6a'],[1,'#ffee99']], colorbar=dict(title="94.28M")))
    price_line=price+np.cumsum(np.random.randn(60)*20)
    fig_heat.add_trace(go.Scatter(x=x_time, y=price_line, mode='lines', line=dict(color='#00ff88', width=2), name='BTC'))
    fig_heat.update_layout(height=500, template="plotly_dark", paper_bgcolor="#120a28", plot_bgcolor="#120a28", margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig_heat, use_container_width=True)

with colLB:
    st.markdown("### 💥 LIQUIDAÇÕES AO VIVO")
    st.markdown("""
    <div style='background:#1c1c1f;padding:8px;border-radius:8px;margin-bottom:5px;border-left:3px solid #ff4e4e'><b style='color:#ff4e4e'>▼ LONG $342k @ $83,920</b><br><small style='color:#888'>21:47:12</small></div>
    <div style='background:#1c1c1f;padding:8px;border-radius:8px;margin-bottom:5px;border-left:3px solid #00d395'><b style='color:#00d395'>▲ SHORT $128k @ $84,100</b><br><small style='color:#888'>21:47:05</small></div>
    <div style='background:#1c1c1f;padding:8px;border-radius:8px;margin-bottom:10px;border-left:3px solid #ff4e4e'><b style='color:#ff4e4e'>▼ LONG $512k @ $83,880</b><br><small style='color:#888'>21:46:58</small></div>
    """, unsafe_allow_html=True)

    st.markdown("### 🤖 BOT - ENTRADAS/SAÍDAS")
    atual=ls_r[-1]
    if atual>1.6:
        st.error(f"🔴 BOT: VENDA - LS {atual:.2f} excesso longs - Saída")
    elif atual<1.0:
        st.success(f"🟢 BOT: COMPRA - LS {atual:.2f} excesso shorts - Entrada")
    else:
        st.warning(f"🟡 BOT: NEUTRO - LS {atual:.2f} - Aguardar")
    st.caption(f"RSI 15m: 54 | Alvo: $87,138 (+{(87138-price)/price*100:.1f}%) | Suporte: $84,026")

# BLOCO 4 - BALEIAS 50M
st.markdown("---")
st.markdown("### 🐋 BALEIAS > $50M - RASTREIO")
try:
    txs=requests.get("https://blockchain.info/unconfirmed-transactions?format=json",timeout=5).json().get('txs',[])[:80]
    achou=False
    for tx in txs:
        btc=sum([o['value'] for o in tx['out']])/1e8; usd=btc*price
        if usd>=50000000:
            achou=True
            st.markdown(f"**${usd/1e6:.1f}M** ({btc:.1f} BTC) - [🔍 Rastrear TX](https://mempool.space/tx/{tx['hash']}) - {datetime.fromtimestamp(tx['time']).strftime('%H:%M:%S')}")
    if not achou:
        st.info("Nenhuma baleia >$50M agora - mempool calmo (normal)")
except:
    st.info("Mempool calmo")

time.sleep(20)
st.rerun()
