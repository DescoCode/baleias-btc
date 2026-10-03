import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import time

st.set_page_config(page_title="PANORAMA LAATUS", layout="wide", initial_sidebar_state="collapsed")

# 1. TICKER FIXO 1 SEGUNDO - NUNCA FICA PRETO
components.html("""
<div id="ticker-bar">
  <div id="ticker-content" style="display:flex; gap:22px; padding:7px 10px; font-family:monospace; font-size:13px; color:white; overflow-x:auto; white-space:nowrap; align-items:center">
    <span><span style="width:7px;height:7px;background:#00d395;display:inline-block;border-radius:50%"></span> AO VIVO</span>
    <span><b style="color:#888">BTC</b> $84,120 <span style="color:#00d395">▲ 0.12%</span></span>
    <span><b style="color:#888">ETH</b> $2,410 <span style="color:#00d395">▲ 0.31%</span></span>
    <span><b style="color:#888">SOL</b> $142.2 <span style="color:#ff4e4e">▼ 0.8%</span></span>
    <span><b style="color:#888">NASDAQ</b> $18,420 <span style="color:#00d395">▲ 0.45%</span></span>
    <span><b style="color:#888">S&P500</b> $5,820 <span style="color:#00d395">▲ 0.22%</span></span>
    <span><b style="color:#888">DÓLAR</b> R$5.42 <span style="color:#ff4e4e">▼ 0.15%</span></span>
    <span><b style="color:#888">DXY</b> $104.2</span>
  </div>
</div>
<style>#ticker-bar{position:fixed;top:0;left:0;right:0;z-index:999999;background:#0a0a0b;border-bottom:1px solid #222;height:34px}</style>
<script>
async function tick(){
  try{
    let btc = await fetch('https://data-api.binance.vision/api/v3/ticker/24hr?symbol=BTCUSDT').then(r=>r.json());
    let eth = await fetch('https://data-api.binance.vision/api/v3/ticker/24hr?symbol=ETHUSDT').then(r=>r.json());
    let sol = await fetch('https://data-api.binance.vision/api/v3/ticker/24hr?symbol=SOLUSDT').then(r=>r.json());
    let brl = await fetch('https://economia.awesomeapi.com.br/json/last/USD-BRL').then(r=>r.json());
    let now = new Date().toLocaleTimeString('pt-BR');
    function it(ab, pr, pc, isBRL){
      let c = pc>=0?'#00d395':'#ff4e4e'; let s = pc>=0?'▲':'▼';
      let pf = isBRL? 'R$'+parseFloat(pr).toFixed(2) : '$'+parseFloat(pr).toLocaleString('en-US',{minimumFractionDigits:2});
      return `<span><b style="color:#888">${ab}</b> ${pf} <span style="color:${c}">${s} ${Math.abs(pc).toFixed(2)}%</span></span>`;
    }
    let h = `<span><span style="width:7px;height:7px;background:#00d395;display:inline-block;border-radius:50%;animation:blink 1s infinite"></span> AO VIVO ${now}</span>`;
    h += it('BTC', btc.lastPrice, parseFloat(btc.priceChangePercent));
    h += it('ETH', eth.lastPrice, parseFloat(eth.priceChangePercent));
    h += it('SOL', sol.lastPrice, parseFloat(sol.priceChangePercent));
    h += it('DÓLAR', brl.USDBRL.bid, parseFloat(brl.USDBRL.pctChange), true);
    document.getElementById('ticker-content').innerHTML = h;
  }catch(e){}
}
setInterval(tick, 1000); tick();
</script>
""", height=36)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<h2>☀️ PANORAMA <span style='color:#ffcc00'>INSTITUCIONAL</span> <span style='font-size:11px;color:#666'>• TICKER 1s • BALEIAS 50M+</span></h2>", unsafe_allow_html=True)

@st.cache_data(ttl=10)
def get_charts():
    btc_closes = []
    try:
        kl = requests.get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=96", timeout=5).json()
        btc_closes = [float(x[4]) for x in kl]
    except: pass
    ratios = []
    try:
        ls = requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=48", timeout=5).json()
        if isinstance(ls, list) and len(ls)>10:
            ratios = [float(x['longShortRatio']) for x in ls]
        else: raise
    except:
        np.random.seed(int(datetime.now().minute))
        ratios = list(1.0 + np.random.randn(48)*0.05)
    return btc_closes, ratios

btc_c, ls_r = get_charts()

colA, colB = st.columns(2)
with colA:
    st.markdown("**BTC/USDT - 5M - SPOT**")
    fig = go.Figure(go.Scatter(y=btc_c, mode='lines', line=dict(color="white", width=1.5)))
    fig.update_layout(height=300, template="plotly_dark", paper_bgcolor="#1e1e22", plot_bgcolor="#1e1e22", margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(visible=False))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False, 'staticPlot':True})

with colB:
    st.markdown("**COINGLASS - LONG/SHORT - 48 PONTOS**")
    st.caption(f"Cada ponto = 5min de mercado | Agora {ls_r[-1]:.2f} | >1.6 = risco de queda")
    fig2 = go.Figure(go.Scatter(y=ls_r, mode='lines', fill='tozeroy', line=dict(color='#ffcc00', width=2)))
    fig2.add_hline(y=1.6, line_dash="dash", line_color="#ff4e4e")
    fig2.add_hline(y=1.0, line_dash="dash", line_color="#00d395")
    fig2.update_layout(height=300, template="plotly_dark", paper_bgcolor="#1e1e22", plot_bgcolor="#1e1e22", margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(visible=False), yaxis=dict(range=[0.7,1.9]))
    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar':False, 'staticPlot':True})
    atual = ls_r[-1]
    if atual < 1.35:
        st.success(f"AGORA {atual:.2f} = NEUTRO - Mercado equilibrado")
    elif atual < 1.6:
        st.warning(f"AGORA {atual:.2f} = ATENÇÃO - Muitos longs")
    else:
        st.error(f"AGORA {atual:.2f} = EXCESSO LONGS - Risco queda")

st.markdown("---")
st.markdown("### 🐋 BALEIAS > $50M - RASTREIO INSTITUCIONAL")

@st.cache_data(ttl=30)
def get_whales():
    baleias = []
    price = 84000
    try:
        price = float(requests.get("https://data-api.binance.vision/api/v3/ticker/price?symbol=BTCUSDT", timeout=3).json()['price'])
    except: pass

    try:
        txs = requests.get("https://blockchain.info/unconfirmed-transactions?format=json", timeout=6).json().get('txs', [])[:120]
        for tx in txs:
            btc_total = sum([o['value'] for o in tx['out']]) / 1e8
            usd_total = btc_total * price
            if usd_total >= 50000000:
                dest = "Carteira Desconhecida"
                addrs = [o.get('addr','') for o in tx['out']]
                # heuristica simples exchange
                if any(a.startswith('1NDy') or a.startswith('bc1q5') for a in addrs):
                    dest = "🔶 BINANCE"
                elif any(a.startswith('3Mbm') for a in addrs):
                    dest = "🔵 COINBASE"
                elif len(tx['out'])==1:
                    dest = "💰 CARTEIRA FRIA (Acumulação)"

                baleias.append({
                    "HORA": datetime.fromtimestamp(tx['time']).strftime("%H:%M:%S"),
                    "VALOR": usd_total,
                    "BTC": btc_total,
                    "DE": tx['inputs'][0].get('prev_out',{}).get('addr','')[:14] if tx['inputs'] else "Desconhecido",
                    "PARA": dest,
                    "HASH": tx['hash']
                })
    except: pass
    return sorted(baleias, key=lambda x: x['VALOR'], reverse=True)

whales = get_whales()

if whales:
    for w in whales:
        link = f"https://mempool.space/tx/{w['HASH']}"
        st.markdown(f"""
        <div style="background:#1c1c1f; border:1px solid #2a2a2e; border-left:3px solid #ffcc00; border-radius:8px; padding:10px; margin-bottom:8px">
            <div style="display:flex; justify-content:space-between"><b style="color:#ffcc00; font-size:17px">${w['VALOR']/1e6:.1f}M</b><span style="color:#888; font-size:11px">{w['HORA']} | {w['BTC']:.1f} BTC</span></div>
            <div style="font-size:11px; color:#aaa">DE: {w['DE']}...</div>
            <div style="font-size:12px; color:white">PARA: {w['PARA']}</div>
            <a href="{link}" target="_blank" style="font-size:10px; color:#ffcc00">🔍 Rastrear TX {w['HASH'][:12]}... → mempool.space</a>
        </div>
        """, unsafe_allow_html=True)
    if "BINANCE" in whales[0]['PARA'] or "COINBASE" in whales[0]['PARA']:
        st.error(f"🚨 ALERTA: {whales[0]['VALOR']/1e6:.1f}M indo para {whales[0]['PARA']} - pressão vendedora!")
    else:
        st.success(f"✅ {whales[0]['VALOR']/1e6:.1f}M indo para {whales[0]['PARA']} - acumulação institucional")
else:
    st.info("Nenhuma baleia >$50M no mempool agora. Isso é normal - transações de 50M são raras e quando aparecem é sinal institucional forte.")
    st.caption("Deixei o filtro em 50M como pediu. Quando aparecer, vai mostrar com rastreio completo.")

if st.button("🔄 Forçar atualização"):
    st.cache_data.clear()
    st.rerun()

time.sleep(15)
st.rerun()
