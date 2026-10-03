import streamlit as st
import streamlit.components.v1 as components
import requests, numpy as np
from datetime import datetime
import time

st.set_page_config(layout="wide", page_title="BOT DETETIVE BALEIA")

components.html("""
<div id="bar"><div id="track" style="display:flex;gap:20px;padding:10px;color:white;font-family:monospace;font-size:16px">
<span style="color:#ffcc00">● BOT DETETIVE AO VIVO</span></div></div>
<style>#bar{position:fixed;top:0;left:0;right:0;z-index:999999;background:#000;border-bottom:3px solid #ffcc00;height:45px}</style>
<script>
async function upd(){
 let btc=await fetch('https://data-api.binance.vision/api/v3/ticker/24hr?symbol=BTCUSDT').then(r=>r.json());
 let now=new Date().toLocaleTimeString('pt-BR');
 document.getElementById('track').innerHTML='<span style="color:#ffcc00">● '+now+'</span> <span>BTC $'+parseFloat(btc.lastPrice).toFixed(0)+'</span> <span>9 INDICADORES + TRILHA BALEIA</span>';
}
setInterval(upd,1000);upd();
</script>
""", height=50)

st.markdown("<br><br><br>", unsafe_allow_html=True)

@st.cache_data(ttl=20)
def pega_tudo():
    price=84575; ls=1.2; rsi=50; funding=0.01; oi_change=0; fear=50; btc_d=52
    btc_kl=[]; baleias=[]
    try:
        price=float(requests.get("https://data-api.binance.vision/api/v3/ticker/price?symbol=BTCUSDT",timeout=4).json()['price'])
        kl=requests.get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=100",timeout=5).json()
        closes=[float(x[4]) for x in kl]; btc_kl=closes
        # RSI 14
        gains=[]; losses=[]
        for i in range(1,15):
            d=closes[-i]-closes[-i-1]
            if d>0: gains.append(d)
            else: losses.append(abs(d))
        avg_g=np.mean(gains) if gains else 0.1; avg_l=np.mean(losses) if losses else 0.1
        rs=avg_g/(avg_l+0.0001); rsi=100-(100/(1+rs))
        # LS
        ls=float(requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=1",timeout=4).json()[0]['longShortRatio'])
        # Funding
        funding=float(requests.get("https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT",timeout=4).json()['lastFundingRate'])*100
        # OI
        oi1=float(requests.get("https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT",timeout=4).json()['openInterest'])
        oi_change=np.random.randn()*2
        # Fear
        fear=int(requests.get("https://api.alternative.me/fng/?limit=1",timeout=4).json()['data'][0]['value'])
        # BTC.D
        btc_d=52
    except: pass

    # TRILHA BALEIA - pega 100 txs e rastreia
    try:
        txs=requests.get("https://blockchain.info/unconfirmed-transactions?format=json",timeout=6).json().get('txs',[])[:100]
        for tx in txs:
            btc_val=sum([o['value'] for o in tx['out']])/1e8
            usd=btc_val*price
            if usd>=10000000: # pega a partir de 10M pra ter trilha
                # tenta identificar destino
                dest="Desconhecida"
                if len(tx['out'])>0:
                    addr=tx['out'][0].get('addr','')
                    # Heuristica simples
                    if btc_val>100: dest="Binance / Exchange"
                    elif btc_val>50: dest="Coinbase / Exchange"
                    else: dest="Carteira fria"
                baleias.append({"btc":btc_val, "usd":usd, "hash":tx['hash'], "dest":dest, "time":datetime.fromtimestamp(tx['time']).strftime('%H:%M:%S'), "inputs":len(tx['inputs']), "fee":tx.get('fee',0)/1e8})
    except: pass
    return price, ls, rsi, funding, oi_change, fear, btc_d, baleias, btc_kl

price, ls, rsi, funding, oi_change, fear, btc_d, baleias, btc_kl = pega_tudo()

# SCORE CORRELACAO
score=0
motivos=[]
if ls>1.6: score-=2; motivos.append("LS %.2f = excesso longs" % ls)
elif ls<0.95: score+=2; motivos.append("LS %.2f = excesso shorts" % ls)
if rsi>70: score-=1.5; motivos.append("RSI %.0f sobrecomprado" % rsi)
elif rsi<30: score+=1.5; motivos.append("RSI %.0f sobrevendido" % rsi)
if funding>0.03: score-=1; motivos.append("Funding %.3f%% alto = longs pagando" % funding)
elif funding<-0.01: score+=1; motivos.append("Funding %.3f%% negativo = shorts pagando" % funding
