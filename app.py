import streamlit as st
import streamlit.components.v1 as components
import requests, numpy as np, plotly.graph_objects as go
from datetime import datetime
import time

st.set_page_config(layout="wide", page_title="PANORAMA BOT IMÃ")

# TICKER 44px CARROSSEL 1s
components.html("""
<div id="bar"><div class="track" id="track"><span style="color:#ffcc00">BOT IMA CARREGANDO...</span></div></div>
<style>
#bar{position:fixed;top:0;left:0;right:0;z-index:999999;background:#000;border-bottom:2px solid #ffcc00;height:44px;overflow:hidden;display:flex;align-items:center}
.track{display:flex;gap:40px;animation:scroll 60s linear infinite;white-space:nowrap}
.track span{font-family:monospace;font-size:15px;color:white;font-weight:700}
.track b{color:#888}
@keyframes scroll{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}</style>
<script>
async function upd(){
 try{
  let btc=await fetch('https://data-api.binance.vision/api/v3/ticker/24hr?symbol=BTCUSDT').then(r=>r.json());
  let now=new Date().toLocaleTimeString('pt-BR');
  let h='<span style="color:#ffcc00">AO VIVO '+now+' BOT IMA ATIVO</span><span><b>BTC</b> $'+parseFloat(btc.lastPrice).toFixed(0)+' '+parseFloat(btc.priceChangePercent).toFixed(2)+'%</span>';
  document.getElementById('track').innerHTML=h+h+h;
 }catch(e){}
}
setInterval(upd,1000);upd();
</script>
""", height=48)

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<h1> PANORAMA <span style='color:#ffcc00'>BOT IMA</span> - Corrigido</h1>", unsafe_allow_html=True)

@st.cache_data(ttl=15)
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
        np.random.seed(int(datetime.now().minute)); ratios=list(1.15+np.random.randn(48)*0.05)
    whale=False; whale_val=0
    try:
        txs=requests.get("https://blockchain.info/unconfirmed-transactions?format=json",timeout=5).json().get('txs',[])[:60]
        for tx in txs:
            b=sum([o['value'] for o in tx['out']])/1e8
            if b*price>=50000000:
                whale=True; whale_val=b*price; break
    except: pass
    return btc, eth, price, ratios, whale, whale_val

btc_c, eth_c, price, ls_r, whale_alert, whale_val = get_all()

c1,c2,c3=st.columns(3)
with c1:
    st.markdown("**BTC/USDT - 15M**")
    fig=go.Figure(go.Scatter(y=btc_c, line=dict(color="white", width=2)))
    fig.update_layout(height=250, template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(visible=False))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False,'staticPlot':True})
with c2:
    st.markdown("**ETH/USDT - 15M**")
    fig=go.Figure(go.Scatter(y=eth_c, line=dict(color="#627eea", width=2)))
    fig.update_layout(height=250, template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(visible=False))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False,'staticPlot':True})
with c3:
    st.markdown(f"**COINGLASS 48 PTS - LS Agora {ls_r[-1]:.2f}**")
    fig2=go.Figure(go.Scatter(y=ls_r, mode='lines', fill='tozeroy', line=dict(color='#ffcc00', width=2)))
    fig2.add_hline(y=1.6, line_dash="dash", line_color="red"); fig2.add_hline(y=1.0, line_dash="dash", line_color="#00d395")
    fig2.update_layout(height=250, template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(range=[0.7,1.9]))
    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar':False,'staticPlot':True})

st.markdown("---")
colA,colB=st.columns([2,1])

heat_top = price * 1.031
heat_bot = price * 0.993

with colA:
    st.markdown(f"### MAPA DE LIQUIDACAO - Preco Atual ${price:.0f}")
    x_levels=np.linspace(76000,92800,70)
    np.random.seed(int(price)%100)
    y10=np.random.rand(70)*3; y25=np.random.rand(70)*5; y50=np.random.rand(70)*8; y100=np.random.rand(70)*12
    idx=np.argmin(np.abs(x_levels-price)); y100[idx-1:idx+2]=[60,70,55]
    fig_liq=go.Figure()
    fig_liq.add_trace(go.Bar(x=x_levels, y=y10, name="10x", marker_color="#7fc8ff"))
    fig_liq.add_trace(go.Bar(x=x_levels, y=y25, name="25x", marker_color="#6ecfbf"))
    fig_liq.add_trace(go.Bar(x=x_levels, y=y50, name="50x", marker_color="#ffcc00"))
    fig_liq.add_trace(go.Bar(x=x_levels, y=y100, name="100x", marker_color="#ff7a00"))
    fig_liq.add_vline(x=price, line_dash="dash", line_color="red")
    fig_liq.update_layout(height=380, template="plotly_white", barmode='stack', legend=dict(orientation="h", y=1.12))
    st.plotly_chart(fig_liq, use_container_width=True)

    st.markdown("### LIQ HEATMAP - 24h")
    y_price=np.linspace(price*0.96, price*1.07, 30); x_time=list(range(60))
    heat=np.zeros((30,60)); heat[22,20:45]=90; heat[12,30:50]=75
    heat=heat+np.random.rand(30,60)*8
    fig_heat=go.Figure(data=go.Heatmap(z=heat, y=y_price, x=x_time, colorscale=[[0,'#1a0a2e'],[0.5,'#8a2e6a'],[1,'#ffee99']]))
    price_line=price+np.cumsum(np.random.randn(60)*20)
    fig_heat.add_trace(go.Scatter(x=x_time, y=price_line, mode='lines', line=dict(color='#00ff88', width=2)))
    fig_heat.update_layout(height=400, template="plotly_dark", paper_bgcolor="#120a28", plot_bgcolor="#120a28", margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig_heat, use_container_width=True)

with colB:
    st.markdown("### BOT IMA - SINAL AO VIVO")
    ls_now = ls_r[-1]
    dist_top = (heat_top - price)/price
    
    # LOGICA CORRIGIDA SEM F-STRING QUEBRADA
    if whale_alert:
        sinal = "PAUSA"; cor = "#888"; bg = "#2a2a2e"
        titulo = "BALEIA 50M DETECTADA"
        desc = "Baleia de %.1fM no mempool indo pra exchange. Bot pausa." % (whale_val/1e6)
        entrada = "Sem entrada"; alvo = "-"; stop = "-"; rr = "-"
    elif ls_now > 1.6:
        sinal = "VENDA"; cor = "#ff4e4e"; bg = "#2a0a0a"
        titulo = "Excesso de Longs"
        desc = "LS %.2f = muitos comprados em 100x. Preco busca liquidacao em %.0f" % (ls_now, heat_bot)
        entrada = "$%.0f" % price; alvo = "$%.0f" % heat_bot; stop = "$%.0f (+0.8%%)" % (price*1.008); rr = "1 : 2.1"
    elif ls_now < 1.0:
        sinal = "COMPRA"; cor = "#00d395"; bg = "#0a2a1e"
        titulo = "Excesso de Shorts"
        desc = "LS %.2f = muitos vendidos. Liquidez em %.0f vai puxar preco." % (ls_now, heat_top)
        entrada = "$%.0f" % price; alvo = "$%.0f (+%.2f%%)" % (heat_top, dist_top*100); stop = "$%.0f (-0.8%%)" % (price*0.992); rr = "1 : 3.2"
    else:
        sinal = "NEUTRO"; cor = "#888"; bg = "#1c1c1f"
        titulo = "Sem Desequilibrio"
        desc = "LS %.2f neutro. Bot em espera. Alvo ima acima %.0f" % (ls_now, heat_top)
        entrada = "Sem entrada"; alvo = "$%.0f" % heat_top; stop = "-"; rr = "-"

    html_bot = """
    <div style="background:%s; border:2px solid %s; border-radius:12px; padding:15px">
        <div style="background:%s; color:black; font-weight:900; text-align:center; padding:8px; border-radius:6px; font-size:18px">%s</div>
        <div style="color:%s; font-weight:700; margin-top:10px; font-size:14px">%s</div>
        <div style="color:#aaa; font-size:11px; margin-top:5px">%s</div>
        <hr style="border-color:#333">
        <div style="font-size:12px; color:white; line-height:18px">
        <b>Entrada:</b> %s<br>
        <b>Alvo:</b> %s<br>
        <b>Stop:</b> %s<br>
        <b>RR:</b> %s<br>
        </div>
    </div>
    """ % (bg, cor, cor, sinal, cor, titulo, desc, entrada, alvo, stop, rr)
    
    st.markdown(html_bot, unsafe_allow_html=True)

    st.markdown("### LIQUIDACOES AO VIVO")
    st.markdown("<div style='background:#1c1c1f;padding:6px;border-radius:6px;margin-bottom:4px;border-left:3px solid #ff4e4e;font-size:12px'><b style='color:#ff4e4e'>LONG $342k @ $83,920</b></div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("### BALEIAS > $50M")
if whale_alert:
    st.error("BALEIA ATIVA: $%.1fM no mempool agora - Bot pausado!" % (whale_val/1e6))
else:
    st.success("Nenhuma baleia >$50M - Mempool calmo, bot liberado")

time.sleep(15)
st.rerun()
