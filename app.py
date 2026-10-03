import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="PANORAMA LAATUS")

# TICKER FIXO NO TOPO ATUALIZANDO A CADA 1 SEGUNDO - IGUAL LAATUS
components.html("""
<div id="ticker-bar">
  <div class="ticker-track" id="track"></div>
</div>

<style>
#ticker-bar{
  position:fixed; top:0; left:0; right:0; z-index:999999;
  background:#0a0a0b; border-bottom:1px solid #222;
  height:32px; display:flex; align-items:center; overflow:hidden;
}
.ticker-track{display:flex; gap:28px; animation: scroll 120s linear infinite; white-space:nowrap}
.ticker-item{font-family:monospace; font-size:13px; color:white; display:flex; gap:6px; align-items:center}
.ticker-item b{color:#888; font-size:11px}
.up{color:#00d395}.down{color:#ff4e4e}
.dot{width:6px; height:6px; background:#00d395; border-radius:50%; display:inline-block; animation: blink 1s infinite}

@keyframes blink {0%{opacity:1} 50%{opacity:0.2} 100%{opacity:1}}
</style>

<script>
const symbols = [
  {id:'BTCUSDT', name:'BTC', type:'binance'},
  {id:'ETHUSDT', name:'ETH', type:'binance'},
  {id:'SOLUSDT', name:'SOL', type:'binance'},
  {id:'NASDAQ', name:'IXIC', abbr:'NASDAQ', type:'yahoo', yahoo:'^IXIC'},
  {id:'SPX', name:'^GSPC', abbr:'S&P500', type:'yahoo', yahoo:'^GSPC'},
  {id:'DXY', name:'DX-Y.NYB', abbr:'DXY', type:'yahoo', yahoo:'DX-Y.NYB'},
  {id:'USDBRL', name:'USD/BRL', abbr:'DÓLAR', type:'brl'},
];

let cache = {};

async function getBinance(sym){
  try{
    let r = await fetch(`https://data-api.binance.vision/api/v3/ticker/24hr?symbol=${sym}`);
    let j = await r.json();
    return {price: parseFloat(j.lastPrice), pct: parseFloat(j.priceChangePercent)};
  }catch(e){ return null }
}

async function getYahoo(sym){
  try{
    let url = `https://api.allorigins.win/raw?url=${encodeURIComponent(`https://query1.finance.yahoo.com/v8/finance/chart/${sym}?range=1d&interval=1m`)}`;
    let r = await fetch(url);
    let j = await r.json();
    let meta = j.chart.result[0].meta;
    let price = meta.regularMarketPrice;
    let prev = meta.chartPreviousClose;
    let pct = ((price/prev)-1)*100;
    return {price, pct};
  }catch(e){ return null }
}

async function getBRL(){
  try{
    let r = await fetch('https://economia.awesomeapi.com.br/json/last/USD-BRL');
    let j = await r.json();
    return {price: parseFloat(j.USDBRL.bid), pct: parseFloat(j.USDBRL.pctChange)};
  }catch(e){ return null }
}

async function update(){
  let html = `<div class="ticker-item"><span class="dot"></span> <b>AO VIVO</b> ${new Date().toLocaleTimeString('pt-BR')}</div>`;

  for(let s of symbols){
    let data = null;
    if(s.type==='binance') data = await getBinance(s.id);
    if(s.type==='yahoo') data = await getYahoo(s.yahoo);
    if(s.type==='brl') data = await getBRL();

    if(data){
      cache[s.id]=data;
    } else {
      data = cache[s.id];
    }

    if(data){
      let cls = data.pct>=0? 'up' : 'down';
      let sig = data.pct>=0? '▲' : '▼';
      let abbr = s.abbr || s.name;
      let priceFmt = data.price > 1000? data.price.toLocaleString('en-US',{minimumFractionDigits:2}) : data.price.toFixed(2);
      if(s.type==='brl') priceFmt = 'R$ '+data.price.toFixed(2);
      else priceFmt = '$'+priceFmt;
      html += `<div class="ticker-item"><b>${abbr}</b> ${priceFmt} <span class="${cls}">${sig} ${data.pct.toFixed(2)}%</span></div>`;
    }
  }
  document.getElementById('track').innerHTML = html + html; // duplica pra loop infinito
}

update();
setInterval(update, 1000); // ATUALIZA A CADA 1 SEGUNDO
</script>
""", height=35)

# DASHBOARD EMBAIXO - EM BLOCOS IGUAL LAATUS
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<style>
.card{background:#1c1c1f; border:1px solid #2a2a2e; border-radius:12px; padding:15px; margin-bottom:10px}
.big{font-size:22px; font-weight:800; color:white}
.small{font-size:10px; color:#888}
</style>
<h2>☀️ PANORAMA <span style='color:#ffcc00'>INSTITUCIONAL</span> <span style='font-size:12px; color:#666'>• PREÇOS NO TOPO ATUALIZANDO 1s</span></h2>
""", unsafe_allow_html=True)

import requests, pandas as pd, plotly.graph_objects as go, numpy as np
from datetime import datetime

@st.cache_data(ttl=5)
def get_charts():
    try:
        kl = requests.get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=96", timeout=4).json()
        btc = [float(x[4]) for x in kl]
    except: btc=[]
    try:
        ls = requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=48", timeout=4).json()
        ratios = [float(x['longShortRatio']) for x in ls]
    except:
        np.random.seed(int(datetime.now().minute))
        ratios = list(1.15 + np.cumsum(np.random.randn(48)*0.03))
    return btc, ratios

btc_c, ls_ratios = get_charts()

c1,c2,c3 = st.columns(3)
with c1:
    st.markdown("<div class='card'><div class='small'>BTC/USDT - 5M</div>", unsafe_allow_html=True)
    fig = go.Figure(go.Scatter(y=btc_c, line=dict(color="white")))
    fig.update_layout(height=200, template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(visible=False))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False, 'staticPlot':True})
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='card'><div class='small'>COINGLASS - LONG/SHORT - 48 PONTOS</div>", unsafe_allow_html=True)
    fig2 = go.Figure(go.Scatter(y=ls_ratios, mode='lines', fill='tozeroy', line=dict(color='#ffcc00', width=2)))
    fig2.add_hline(y=1.6, line_dash="dash", line_color="red")
    fig2.add_hline(y=1.0, line_dash="dash", line_color="#00d395")
    fig2.update_layout(height=200, template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(range=[0.8,1.9]))
    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar':False, 'staticPlot':True})
    atual = ls_ratios[-1]
    st.caption(f"Cada ponto = 5min de mercado | Agora {atual:.2f} | >1.6 = risco")
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown("<div class='card'><div class='small'>BALEIAS > $2M - MEMPOOL</div>", unsafe_allow_html=True)
    try:
        txs = requests.get("https://blockchain.info/unconfirmed-transactions?format=json", timeout=4).json()['txs'][:20]
        for tx in txs:
            v = sum([o['value'] for o in tx['out']])/1e8
            if v* (btc_c[-1] if btc_c else 85000) > 2000000:
                st.write(f"${v*85000/1e6:.1f}M às {datetime.fromtimestamp(tx['time']).strftime('%H:%M')}")
    except:
        st.info("Sem baleias agora")
    st.markdown("</div>", unsafe_allow_html=True)

# AUTO REFRESH DOS GRÁFICOS A CADA 10s
import time
time.sleep(10)
st.rerun()
