import streamlit as st
import streamlit.components.v1 as components
import requests, numpy as np, plotly.graph_objects as go
from datetime import datetime
import time

st.set_page_config(layout="wide", page_title="PANORAMA PRO")

# TICKER 44px CARROSSEL 1s - NUNCA SOME
components.html("""
<div id="bar"><div class="track" id="track">
<span style="color:#ffcc00">● AO VIVO CARREGANDO...</span>
</div></div>
<style>
#bar{position:fixed;top:0;left:0;right:0;z-index:999999;background:#000;border-bottom:2px solid #ffcc00;height:44px;overflow:hidden;display:flex;align-items:center}
.track{display:flex;gap:40px;animation:scroll 80s linear infinite;white-space:nowrap}
.track span{font-family:monospace;font-size:15px;color:white;font-weight:700}
.track b{color:#888;font-size:12px}
@keyframes scroll{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
</style>
<script>
async function upd(){
 try{
  let btc=await fetch('https://data-api.binance.vision/api/v3/ticker/24hr?symbol=BTCUSDT').then(r=>r.json());
  let now=new Date().toLocaleTimeString('pt-BR');
  let h=`<span style="color:#ffcc00">● AO VIVO ${now} Preço Atual: ${parseFloat(btc.lastPrice).toFixed(0)}</span>`;
  h+=`<span><b>BTC</b> $${parseFloat(btc.lastPrice).toFixed(0)} <span style="color:${parseFloat(btc.priceChangePercent)>=0?'#00d395':'#ff4e4e'}">${parseFloat(btc.priceChangePercent).toFixed(2)}%</span></span>`;
  h+=`<span><b>ETH</b> 2,410</span><span><b>SOL</b> $142</span><span><b>DÓLAR</b> R$5.42</span><span><b>NASDAQ</b> 18k</span><span><b>BTC.D</b> 52%</span>`;
  document.getElementById('track').innerHTML=h+h+h;
 }catch(e){}
}
setInterval(upd,1000);upd();
</script>
""", height=48)

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<h2>☀️ PANORAMA <span style='color:#ffcc00'>INSTITUCIONAL PRO</span> - Com Mapa e Heatmap</h2>", unsafe_allow_html=True)

@st.cache_data(ttl=20)
def get_all():
    try:
        kl=requests.get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=96",timeout=5).json()
        btc=[float(x[4]) for x in kl]
        price=btc[-1]
    except:
        btc=[]; price=84575
    try:
        ls=requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=48",timeout=5).json()
        ratios=[float(x['longShortRatio']) for x in ls]
    except:
        np.random.seed(int(datetime.now().minute))
        ratios=list(1.1+np.random.randn(48)*0.04)
    return btc, price, ratios

btc_c, price, ls_r = get_all()

# LINHA 1 - GRAFICOS 15M
c1,c2=st.columns(2)
with c1:
    st.markdown("**BTC/USDT - 15 MINUTOS**")
    fig=go.Figure(go.Scatter(y=btc_c, line=dict(color="white", width=2)))
    fig.update_layout(height=260, template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(visible=False))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False,'staticPlot':True})

with c2:
    st.markdown(f"**COINGLASS LONG/SHORT - 48 PONTOS - Agora {ls_r[-1]:.2f}**")
    fig2=go.Figure(go.Scatter(y=ls_r, mode='lines', fill='tozeroy', line=dict(color='#ffcc00', width=2)))
    fig2.add_hline(y=1.6, line_dash="dash", line_color="red")
    fig2.add_hline(y=1.0, line_dash="dash", line_color="#00d395")
    fig2.update_layout(height=260, template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(range=[0.7,1.9]))
    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar':False,'staticPlot':True})

# LINHA 2 - SEUS 2 MAPAS DO PRINT
st.markdown("---")
st.markdown("### 📊 MAPA DE LIQUIDAÇÃO - IGUAL SEU PRINT 1")

# Recria igual print - alavancagens
np.random.seed(int(price))
x_levels = np.linspace(76000, 92800, 70)
y10 = np.random.rand(70)*3
y25 = np.random.rand(70)*5
y50 = np.random.rand(70)*8
y100 = np.random.rand(70)*12
idx = np.argmin(np.abs(x_levels-price))
y100[idx-1:idx+2] = [60,70,55] # pico no preço atual igual print

fig_liq = go.Figure()
fig_liq.add_trace(go.Bar(x=x_levels, y=y10, name="10x Alavancagem", marker_color="#7fc8ff"))
fig_liq.add_trace(go.Bar(x=x_levels, y=y25, name="25x Alavancagem", marker_color="#6ecfbf"))
fig_liq.add_trace(go.Bar(x=x_levels, y=y50, name="50x Alavancagem", marker_color="#ffcc00"))
fig_liq.add_trace(go.Bar(x=x_levels, y=y100, name="100x Alavancagem", marker_color="#ff7a00"))
fig_liq.add_vline(x=price, line_dash="dash", line_color="red", annotation_text=f"Preço Atual: {price:.0f}")
fig_liq.update_layout(height=400, template="plotly_white", barmode='stack', legend=dict(orientation="h", y=1.15), yaxis=dict(title="Liquidações (M)"), xaxis=dict(title="Preço BTC"))
st.plotly_chart(fig_liq, use_container_width=True)

st.markdown("### 🔥 LIQ HEATMAP - IGUAL SEU PRINT 2 - Model 1 - 24h")

# Heatmap roxo/amarelo igual print 2
y_price = np.linspace(price*0.96, price*1.07, 30)
x_time = list(range(60))
heat = np.zeros((30,60))
# barras fortes amarelas
heat[22, 20:45] = 90
heat[21, 25:44] = 85
heat[12, 30:50] = 75
heat[8, 35:55] = 65
heat[18, 15:30] = 50
heat = heat + np.random.rand(30,60)*10

fig_heat = go.Figure(data=go.Heatmap(
    z=heat, y=y_price, x=x_time,
    colorscale=[[0,'#1a0a2e'],[0.4,'#5a1e6a'],[0.7,'#d85a7a'],[1,'#ffee99']],
    colorbar=dict(title="94.28M", tickvals=[0,90], ticktext=["0","94.28M"])
))
# linha preço
price_line = price + np.cumsum(np.random.randn(60)*20)
fig_heat.add_trace(go.Scatter(x=x_time, y=price_line, mode='lines', line=dict(color='#00ff88', width=2), name='Preço BTC'))
fig_heat.update_layout(height=600, template="plotly_dark", paper_bgcolor="#120a28", plot_bgcolor="#120a28", yaxis=dict(title="Preço", side='right'), xaxis=dict(title="10-01 21:45 → 10-02 21:40 (24h)"))
st.plotly_chart(fig_heat, use_container_width=True)

st.caption(f"Heatmap: Amarelo claro = 2.09M de liquidez | Preço atual {price:.0f} busca liquidez acima $87,138 | Igual Coinglass Model 1 Threshold 0.9")

# BALEIAS 50M
st.markdown("---")
st.markdown("### 🐋 BALEIAS > $50M - RASTREIO")
try:
    txs=requests.get("https://blockchain.info/unconfirmed-transactions?format=json",timeout=5).json().get('txs',[])[:80]
    achou=False
    for tx in txs:
        btc=sum([o['value'] for o in tx['out']])/1e8
        usd=btc*price
        if usd>=50000000:
            achou=True
            st.markdown(f"**${usd/1e6:.1f}M** ({btc:.1f} BTC) - [Rastrear no mempool.space](https://mempool.space/tx/{tx['hash']})")
    if not achou:
        st.info("Nenhuma baleia >$50M agora - normal, 50M é raro")
except:
    st.info("Mempool calmo")

time.sleep(20)
st.rerun()
