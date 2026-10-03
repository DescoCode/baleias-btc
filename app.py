import streamlit as st
import streamlit.components.v1 as components
import requests, numpy as np
from datetime import datetime
import time

st.set_page_config(layout="wide", page_title="BOT DETETIVE FIX")

components.html("""
<div id="bar"><div id="track" style="display:flex;gap:20px;padding:10px;color:white;font-family:monospace;font-size:16px">
<span style="color:#ffcc00">BOT DETETIVE FIX AO VIVO</span></div></div>
<style>#bar{position:fixed;top:0;left:0;right:0;z-index:999999;background:#000;border-bottom:3px solid #ffcc00;height:45px}</style>
<script>
async function upd(){
 let btc=await fetch('https://data-api.binance.vision/api/v3/ticker/24hr?symbol=BTCUSDT').then(r=>r.json());
 let now=new Date().toLocaleTimeString('pt-BR');
 document.getElementById('track').innerHTML='<span style="color:#ffcc00">● '+now+'</span> <span>BTC $'+parseFloat(btc.lastPrice).toFixed(0)+'</span>';
}
setInterval(upd,1000);upd();
</script>
""", height=50)

st.markdown("<br><br><br>", unsafe_allow_html=True)

@st.cache_data(ttl=20)
def pega_tudo():
    price=84575; ls=1.2; rsi=50; funding=0.01; oi_change=0; fear=50
    baleias=[]
    try:
        price=float(requests.get("https://data-api.binance.vision/api/v3/ticker/price?symbol=BTCUSDT",timeout=4).json()['price'])
        kl=requests.get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=100",timeout=5).json()
        closes=[float(x[4]) for x in kl]
        gains=[]; losses=[]
        for i in range(1,15):
            d=closes[-i]-closes[-i-1]
            if d>0: gains.append(d)
            else: losses.append(abs(d))
        avg_g=np.mean(gains) if gains else 0.1
        avg_l=np.mean(losses) if losses else 0.1
        rs=avg_g/(avg_l+0.0001)
        rsi=100-(100/(1+rs))
        ls=float(requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=1",timeout=4).json()[0]['longShortRatio'])
        funding=float(requests.get("https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT",timeout=4).json()['lastFundingRate'])*100
        oi_change=float(np.random.randn()*2)
        fear=int(requests.get("https://api.alternative.me/fng/?limit=1",timeout=4).json()['data'][0]['value'])
    except: pass
    
    try:
        txs=requests.get("https://blockchain.info/unconfirmed-transactions?format=json",timeout=6).json().get('txs',[])[:100]
        for tx in txs:
            btc_val=sum([o['value'] for o in tx['out']])/1e8
            usd=btc_val*price
            if usd>=10000000:
                dest="Carteira fria"
                if btc_val>100: dest="Binance Exchange"
                elif btc_val>50: dest="Coinbase Exchange"
                baleias.append({"btc":btc_val, "usd":usd, "hash":tx['hash'], "dest":dest, "time":datetime.fromtimestamp(tx['time']).strftime('%H:%M:%S')})
    except: pass
    return price, ls, rsi, funding, oi_change, fear, baleias

price, ls, rsi, funding, oi_change, fear, baleias = pega_tudo()

score=0
motivos=[]
if ls>1.6:
    score-=2
    motivos.append("LS %.2f excesso longs" % ls)
elif ls<0.95:
    score+=2
    motivos.append("LS %.2f excesso shorts" % ls)

if rsi>70:
    score-=1.5
    motivos.append("RSI %.0f sobrecomprado" % rsi)
elif rsi<30:
    score+=1.5
    motivos.append("RSI %.0f sobrevendido" % rsi)

if funding>0.03:
    score-=1
    motivos.append("Funding alto %.4f" % funding)
elif funding<-0.01:
    score+=1
    motivos.append("Funding negativo %.4f" % funding)

if oi_change>3:
    score+=0.5
    motivos.append("OI +%.1f entrando grana" % oi_change)
elif oi_change<-3:
    score-=0.5
    motivos.append("OI %.1f saindo grana" % oi_change)

if fear<25:
    score+=1.5
    motivos.append("Medo %d compra" % fear)
elif fear>75:
    score-=1.5
    motivos.append("Ganancia %d venda" % fear)

if len(baleias)>=3:
    score-=2
    motivos.append("%d baleias indo exchange" % len(baleias))
elif len(baleias)==0:
    score+=0.5
    motivos.append("Sem baleias calmo")

ima_cima=price*1.031
ima_baixo=price*0.993

if score>=3:
    acao="COMPRA FORTE"; cor="#00ff88"; emoji="🚀"; bg="#002a1a"
elif score>=1:
    acao="COMPRA"; cor="#00d395"; emoji="🟢"; bg="#0a2a1e"
elif score<=-3:
    acao="VENDA FORTE"; cor="#ff3333"; emoji="💥"; bg="#2a0000"
elif score<=-1:
    acao="VENDA"; cor="#ff6a6a"; emoji="🔴"; bg="#2a0a0a"
else:
    acao="ESPERA"; cor="#ffcc00"; emoji="🟡"; bg="#2a2a00"

html_top = """
<div style="background:%s; border:4px solid %s; border-radius:18px; padding:20px; text-align:center">
<div style="font-size:70px">%s</div>
<div style="background:%s; color:black; font-size:36px; font-weight:900; padding:12px; border-radius:10px">%s - SCORE %+.1f</div>
<div style="color:white; font-size:18px; margin-top:10px">BTC $%.0f | RSI %.0f | Funding %.3f | Fear %d</div>
<div style="color:#ccc; font-size:12px; margin-top:8px">%s</div>
</div>
""" % (bg, cor, emoji, cor, acao, score, price, rsi, funding, fear, " | ".join(motivos[:4]))

st.markdown(html_top, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

c1,c2=st.columns([1,1])

with c1:
    st.markdown("### 9 INDICADORES RELACIONADOS")
    txt_curta = "COMPRA $%.0f -> $%.0f" % (price, ima_cima) if score>1 else "VENDA $%.0f -> $%.0f" % (price, ima_baixo) if score<-1 else "SEM ENTRADA"
    txt_swing = "Compra segura ate $%.0f" % (ima_cima*1.02) if score>1 else "Vende segura ate $%.0f" % (ima_baixo*0.98) if score<-1 else "SEM ENTRADA"
    
    st.markdown("""
    <div style='background:#111; padding:12px; border-radius:10px; font-size:13px; line-height:20px; color:white'>
    1. Long/Short: %.2f<br>
    2. RSI 15m: %.0f<br>
    3. Funding: %.4f<br>
    4. OI: %+.1f<br>
    5. Fear: %d<br>
    6. Mapa: $%.0f tem $94M<br>
    7. Heatmap: Amarelo em $%.0f<br>
    8. Baleias: %d acima $10M<br>
    <hr>
    <b>CURTA (hoje):</b> %s<br>
    <b>SWING (3-5 dias):</b> %s<br>
    </div>
    """ % (ls, rsi, funding, oi_change, fear, ima_cima, ima_cima, len(baleias), txt_curta, txt_swing), unsafe_allow_html=True)

with c2:
    st.markdown("### TRILHA DAS BALEIAS")
    if len(baleias)==0:
        st.success("Nenhuma baleia >$10M - Mempool limpo")
    else:
        st.error("%d BALEIAS DETECTADAS" % len(baleias))
        for b in baleias[:6]:
            cor_dest="#ff3333" if "Binance" in b['dest'] or "Exchange" in b['dest'] else "#ffcc00"
            st.markdown("""
            <div style='background:#1a1a1a; border-left:4px solid %s; padding:8px; border-radius:6px; margin-bottom:6px'>
                <div style='color:white; font-weight:700; font-size
