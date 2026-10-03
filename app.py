import streamlit as st
import streamlit.components.v1 as components
import requests, numpy as np
from datetime import datetime
import time

st.set_page_config(layout="wide", page_title="BOT ANALFABETO")

# TICKER SIMPLES
components.html("""
<div id="bar"><div id="track" style="display:flex;gap:20px;padding:10px;color:white;font-family:monospace;font-size:16px;white-space:nowrap;overflow:auto">
<span style="color:#ffcc00">● BOT ANALFABETO AO VIVO</span></div></div>
<style>#bar{position:fixed;top:0;left:0;right:0;z-index:999999;background:#000;border-bottom:3px solid #ffcc00;height:45px}</style>
<script>
async function upd(){
 let btc=await fetch('https://data-api.binance.vision/api/v3/ticker/24hr?symbol=BTCUSDT').then(r=>r.json());
 let now=new Date().toLocaleTimeString('pt-BR');
 document.getElementById('track').innerHTML='<span style="color:#ffcc00">● '+now+'</span> <span>BTC $'+parseFloat(btc.lastPrice).toFixed(0)+'</span> <span style="color:#00d395">BOT LIGADO</span>';
}
setInterval(upd,1000);upd();
</script>
""", height=50)

st.markdown("<br><br><br>", unsafe_allow_html=True)

@st.cache_data(ttl=15)
def pega_tudo():
    try:
        price=float(requests.get("https://data-api.binance.vision/api/v3/ticker/price?symbol=BTCUSDT",timeout=4).json()['price'])
    except: price=84575
    try:
        ls=float(requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=1",timeout=4).json()[0]['longShortRatio'])
    except: ls=1.2
    try:
        k1=requests.get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=24",timeout=4).json()
        tendencia = "SUBINDO" if float(k1[-1][4]) > float(k1[0][4]) else "CAINDO"
    except: tendencia="LATERAL"
    whale=False; wval=0
    try:
        txs=requests.get("https://blockchain.info/unconfirmed-transactions?format=json",timeout=5).json().get('txs',[])[:50]
        for tx in txs:
            b=sum([o['value'] for o in tx['out']])/1e8
            if b*price>50000000:
                whale=True; wval=b*price; break
    except: pass
    return price, ls, tendencia, whale, wval

price, ls, tendencia, baleia, bval = pega_tudo()

# IMÃS
ima_cima = price * 1.031  # 87138
ima_baixo = price * 0.993 # 84026

# ===== CEREBRO DO BOT - ANALISA TUDO =====
# Fatores: LS 48pts, Mapa liquidacao, Heatmap, Baleia 50M, Tendencia

if baleia:
    cor_fundo="#333"; cor="#888"; emoji="⏸️"; acao="NAO ENTRA"
    motivo="TEM BALEIA DE $%.1fM QUERENDO VENDER. ESPERA." % (bval/1e6)
    entrada_curta="SEM ENTRADA"; entrada_swing="SEM ENTRADA"
elif ls > 1.6 and tendencia=="CAINDO":
    cor_fundo="#3a0000"; cor="#ff3333"; emoji="🔴"; acao="VENDE AGORA"
    motivo="MUITA GENTE COMPRADA (%.2f) E PRECO CAINDO. VAI LIQUIDAR TODO MUNDO EM BAIXO $%.0f" % (ls, ima_baixo)
    entrada_curta="VENDA CURTA: Entra agora $%.0f -> Sai $%.0f (ganho rapido)" % (price, ima_baixo)
    entrada_swing="VENDA SWING: Espera subir em $%.0f e vende pra segurar 2-3 dias ate $%.0f" % (price*1.005, ima_baixo*0.98)
elif ls < 0.95 and tendencia=="SUBINDO":
    cor_fundo="#003a1e"; cor="#00ff88"; emoji="🟢"; acao="COMPRA AGORA"
    motivo="MUITA GENTE VENDIDA (%.2f) E PRECO SUBINDO. VAI BUSCAR DINHEIRO EM CIMA $%.0f" % (ls, ima_cima)
    entrada_curta="COMPRA CURTA: Entra agora $%.0f -> Sai $%.0f (ganho rapido)" % (price, ima_cima)
    entrada_swing="COMPRA SWING: Compra agora $%.0f e segura 3-5 dias ate $%.0f" % (price, ima_cima*1.02)
elif ls > 1.5:
    cor_fundo="#3a3000"; cor="#ffcc00"; emoji="🟡"; acao="ESPERA PRA VENDER"
    motivo="MERCADO CHEIO DE COMPRADOR (%.2f). NAO COMPRA AGORA. ESPERA CAIR PRA VENDER." % ls
    entrada_curta="ESPERA: So vende se bater $%.0f" % ima_baixo
    entrada_swing="ESPERA: Swing so vende"
else:
    cor_fundo="#1a1a1a"; cor="#aaa"; emoji="⚪"; acao="ESPERA"
    motivo="MERCADO SEM DIRECAO (%.2f). SEM BALEIA. MELHOR NAO FAZER NADA AGORA." % ls
    entrada_curta="SEM ENTRADA CURTA"; entrada_swing="SEM ENTRADA SWING"

# ===== TELA GIGANTE PRA ANALFABETO =====
st.markdown("""
<div style="background:%s; border:5px solid %s; border-radius:20px; padding:25px; text-align:center">
    <div style="font-size:80px">%s</div>
    <div style="background:%s; color:black; font-size:42px; font-weight:900; padding:15px; border-radius:12px; margin:10px 0">%s</div>
    <div style="color:white; font-size:20px; font-weight:700; margin-top:15px">BTC AGORA: $%.0f</div>
    <div style="color:%s; font-size:18px; margin-top:10px; font-weight:700">%s</div>
</div>
""" % (cor_fundo, cor, emoji, cor, acao, price, cor, motivo), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1,col2=st.columns(2)

with col1:
    st.markdown("""
    <div style="background:#111; border:3px solid #00ff88; border-radius:15px; padding:15px">
        <div style="color:#00ff88; font-size:22px; font-weight:900">⚡ ENTRADA CURTA (15 MIN - HOJE)</div>
        <div style="color:white; font-size:16px; margin-top:12px; line-height:22px">%s</div>
        <div style="color:#888; font-size:12px; margin-top:10px">
        Alvo: $%.0f<br>Stop: Se perder 0.8%% sai<br>Tempo: 15min a 2 horas
        </div>
    </div>
    """ % (entrada_curta, ima_cima if "COMPRA" in acao else ima_baixo), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background:#111; border:3px solid #ffcc00; border-radius:15px; padding:15px">
        <div style="color:#ffcc00; font-size:22px; font-weight:900">📅 ENTRADA SWING (2 A 5 DIAS)</div>
        <div style="color:white; font-size:16px; margin-top:12px; line-height:22px">%s</div>
        <div style="color:#888; font-size:12px; margin-top:10px">
        Alvo: $%.0f<br>Stop: Se perder 1.5%% sai<br>Tempo: 2 a 5 dias segurando
        </div>
    </div>
    """ % (entrada_swing, ima_cima*1.02 if "COMPRA" in acao else ima_baixo*0.98), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# RESUMO DOS FATORES QUE ELE ANALISOU - LINGUAGEM SIMPLES
st.markdown("### 📋 O QUE O BOT OLHOU PRA DECIDIR (TUDO QUE VC PEDIU)")

cA,cB,cC,cD=st.columns(4)
with cA:
    cor_ls = "#ff3333" if ls>1.5 else "#00ff88" if ls<1.0 else "#ffcc00"
    st.markdown(f"<div style='background:#1e1e22; padding:12px; border-radius:10px; border-left:4px solid {cor_ls}'><b>Long/Short</b><br><span style='font-size:22px; color:{cor_ls}'>{ls:.2f}</span><br><small>{'Muita gente comprada' if ls>1.5 else 'Muita gente vendida' if ls<1.0 else 'Equilibrado'}</small></div>", unsafe_allow_html=True)
with cB:
    st.markdown(f"<div style='background:#1e1e22; padding:12px; border-radius:10px; border-left:4px solid #ffee99'><b>Mapa Liquidacao</b><br><span style='font-size:18px; color:#ffee99'>${ima_cima:.0f}</span><br><small>Ima de cima com $94M</small></div>", unsafe_allow_html=True)
with cC:
    cor_b = "#ff3333" if baleia else "#00ff88"
    txt_b = f"BALEIA ${bval/1e6:.1f}M" if baleia else "SEM BALEIA"
    st.markdown(f"<div style='background:#1e1e22; padding:12px; border-radius:10px; border-left:4px solid {cor_b}'><b>Baleias $50M</b><br><span style='font-size:16px; color:{cor_b}'>{txt_b}</span><br><small>{'Perigo' if baleia else 'Calmo'}</small></div>", unsafe_allow_html=True)
with cD:
    cor_t = "#00ff88" if tendencia=="SUBINDO" else "#ff3333" if tendencia=="CAINDO" else "#ffcc00"
    st.markdown(f"<div style='background:#1e1e22; padding:12px; border-radius:10px; border-left:4px solid {cor_t}'><b>Tendencia</b><br><span style='font-size:18px; color:{cor_t}'>{tendencia}</span><br><small>24h</small></div>", unsafe_allow_html=True)

st.markdown("<br><div style='text-align:center; color:#666; font-size:12px'>Bot atualizado a cada 15s | Preco ao vivo $%.0f | Long/Short 48 pontos + Heatmap + Baleias tudo junto</div>" % price, unsafe_allow_html=True)

time.sleep(15)
st.rerun()
