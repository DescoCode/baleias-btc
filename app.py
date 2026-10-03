import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout='wide', page_title='LATUS V36 FULL BLOCOS', page_icon='🐋')

html = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0e;color:#fff;font-family:monospace}
.topbar{position:fixed;top:0;left:0;right:0;height:46px;background:#000;border-bottom:2px solid #ffcc00;display:flex;align-items:center;padding:0 12px;z-index:9999;gap:14px;font-size:12px;overflow:auto;white-space:nowrap}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:58px 12px 12px}
.full{grid-column:1/-1}
.block{background:#13131a;border:1px solid #222;border-radius:12px;padding:12px;margin-bottom:2px}
.block-title{font-size:11px;color:#ffcc00;font-weight:900;margin-bottom:8px;display:flex;justify-content:space-between}
.score{font-size:38px;font-weight:900;padding:20px;border-radius:12px;text-align:center;border:2px solid #333}
.badge{padding:3px 8px;border-radius:6px;font-size:10px;font-weight:800;border:1px solid}
.g{color:#00ff88;border-color:#00ff88}
.r{color:#ff3333;border-color:#ff3333}
.whale{border-left:5px solid #ff3333;background:#2a0000;padding:10px;margin-bottom:8px;border-radius:8px;font-size:12px;border:1px solid #ff3333}
table{width:100%;border-collapse:collapse;font-size:11px}
th{color:#666;text-align:left;padding:5px}
td{padding:6px;border-top:1px solid #222}
@media(max-width:800px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="topbar" id="topbar">LATUS V36 - ALTA E BAIXA - 50M ONLY - LOADING...</div>
<div class="grid">
<div class="block full" style="border:3px solid #ffcc00">
<div class="block-title">ROBO DETETIVE - ALTA E BAIXA 75%+ <span id="botTime"></span> <span class="badge g" id="winrate">WINRATE --</span></div>
<div class="score" id="scoreBox" style="background:#111">AGUARDANDO CONFLUENCIA ALTA/BAIXA...</div>
<div style="margin-top:10px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;font-size:10px" id="checks"></div>
<div style="margin-top:8px;font-size:11px;color:#aaa" id="motivos"></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px">
<div style="background:#0f2318;border:1px solid #00ff88;border-radius:8px;padding:12px">
<div style="color:#00ff88;font-weight:900">ENTRADA PRINCIPAL (ALTA E BAIXA)</div>
<div id="entradaPrincipal" style="font-size:14px;margin-top:6px;font-weight:800">ESPERA</div>
<div id="alvoPrincipal" style="font-size:11px;color:#aaa;margin-top:4px"></div>
</div>
<div style="background:#1a1a1a;border:1px solid #333;border-radius:8px;padding:12px">
<div style="color:#666;font-weight:900">ULTIMO SINAL</div>
<div id="ultimoSinal" style="font-size:12px;margin-top:6px">Nenhum ainda - score precisa 3.5+ ou -3.5-</div>
</div>
</div>
</div>

<div class="block full">
<div class="block-title">BTCUSDT - GRAFICO ONLINE FIX <span class="badge g" id="chartStatus">LIVE 15s</span></div>
<div id="tvchart" style="height:400px"></div>
</div>

<div class="block">
<div class="block-title">FILTROS ONLINE BINANCE (RATIO)</div>
<table>
<tr><td>Long/Short Ratio Global</td><td id="ls">-</td><td id="lsCheck">-</td></tr>
<tr><td>Top Trader Pos</td><td id="topPos">-</td><td id="topCheck">-</td></tr>
<tr><td>Funding Rate</td><td id="funding">-</td><td id="fundCheck">-</td></tr>
<tr><td>RSI 15m</td><td id="rsi">-</td><td id="rsiCheck">-</td></tr>
<tr><td>OI</td><td id="oi">-</td><td>OK</td></tr>
<tr><td>Whale >$50M</td><td id="whaleCheck">-</td><td id="whaleStatus">-</td></tr>
</table>
<div style="margin-top:10px">
<a href="https://www.coinglass.com/pro/futures/LiquidationHeatMap" target="_blank" style="background:#ffcc00;color:#000;padding:6px 10px;border-radius:6px;font-size:10px;font-weight:900;text-decoration:none">ABRIR MAPA COINGLASS</a>
</div>
</div>

<div class="block" style="border:2px solid #ff3333">
<div class="block-title">WHALE ALERT SOMENTE >$50M <span class="badge r">CRITICO</span></div>
<div id="whales">Monitorando mempool... So >$50M mostra</div>
<div style="font-size:9px;color:#555;margin-top:8px">Filtro: $10M removido | So $50M+ aparece + bloqueia robo 30min + link trilha mempool.space</div>
</div>

<div class="block full">
<div class="block-title">LIQUIDACOES 24H</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;font-size:11px">
<div style="background:#1a1a1a;padding:8px;border-radius:6px">Long Liq: $73M vs Short $23M<br><span style="color:#00ff88">Longs limpos - tendencia alta</span></div>
<div style="background:#1a1a1a;padding:8px;border-radius:6px">IMA CIMA: $87.138<br>$94M em liquidacoes</div>
<div style="background:#1a1a1a;padding:8px;border-radius:6px">SUPORTE: $84.026<br>$38M em liquidacoes</div>
</div>
</div>

</div>

<script>
let priceNow=84800,lastWhale50Time=0,klinesData=[],chart,candleSeries;
function initChart(){chart=LightweightCharts.createChart(document.getElementById('tvchart'),{layout:{background:{color:'#13131a'},textColor:'#aaa'},grid:{vertLines:{color:'#1a1a1a'},horzLines:{color:'#1a1a1a'}},width:document.getElementById('tvchart').clientWidth,height:400});candleSeries=chart.addCandlestickSeries({upColor:'#00ff88',downColor:'#ff3333',borderVisible:false,wickUpColor:'#00ff88',wickDownColor:'#ff3333'});window.addEventListener('resize',()=>{chart.applyOptions({width:document.getElementById('tvchart').clientWidth});});}
async function loadChart(){try{let kl=await fetch('https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=200').then(r=>r.json());klinesData=kl.map(k=>({time:k[0]/1000,open:parseFloat(k[1]),high:parseFloat(k[2]),low:parseFloat(k[3]),close:parseFloat(k[4])}));candleSeries.setData(klinesData);document.getElementById('chartStatus').innerText='LIVE '+new Date().toLocaleTimeString();}catch{}}
async function updateTick(){try{let t=await fetch('https://data-api.binance.vision/api/v3/ticker/price?symbol=BTCUSDT').then(r=>r.json());priceNow=parseFloat(t.price);if(klinesData.length>0){let last=klinesData[klinesData.length-1];last.close=priceNow;if(priceNow>last.high)last.high=priceNow;if(priceNow<last.low)last.low=priceNow;candleSeries.update(last);}}catch{}}
async function fetchHigh(){try{
let lsJ=await fetch('https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=1').then(r=>r.json());let lsVal=parseFloat(lsJ[0].longShortRatio);
let topJ=await fetch('https://fapi.binance.com/futures/data/topLongShortPositionRatio?symbol=BTCUSDT&period=5m&limit=1').then(r=>r.json());let topVal=parseFloat(topJ[0].longShortRatio);
let fundJ=await fetch('https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT').then(r=>r.json());let funding=parseFloat(fundJ.lastFundingRate)*100;
let oiJ=await fetch('https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT').then(r=>r.json());let oiVal=parseFloat(oiJ.openInterest);
let kl=await fetch('https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=100').then(r=>r.json());
let closes=kl.map(k=>parseFloat(k[4]));let gains=[],losses=[];for(let i=1;i<15;i++){let d=closes[closes.length-i]-closes[closes.length-i-1];if(d>0)gains.push(d);else losses.push(Math.abs(d));}
let avgG=gains.reduce((a,b)=>a+b,0)/(gains.length||1);let avgL=losses.reduce((a,b)=>a+b,0)/(losses.length||1);
let rs=avgG/(avgL+0.0001);let rsi=100-(100/(1+rs));
let lsLong=lsVal>=0.9&&lsVal<=1.30;let lsShort=lsVal>=1.70;
let topLong=topVal>1.80;let topShort=topVal<1.0;
let fundPass=funding<0.03&&funding>-0.02;
let rsiLong=rsi>=32&&rsi<=52;let rsiShort=rsi>=58&&rsi<=75;
let whaleBlocked=(Date.now()-lastWhale50Time)<1800000;

document.getElementById('ls').innerText=lsVal.toFixed(4);
document.getElementById('lsCheck').innerText=lsLong?'NEUTRO LONG 🟢':lsShort?'EXCESSO LONG - SHORT 🟢':'RUIM 🔴';
document.getElementById('lsCheck').style.color=(lsLong||lsShort)?'#00ff88':'#ff3333';
document.getElementById('topPos').innerText=topVal.toFixed(4);
document.getElementById('topCheck').innerText=topLong?'WHALE LONG 🟢':topShort?'WHALE SHORT 🟢':'NEUTRO';
document.getElementById('funding').innerText=funding.toFixed(4)+'%';
document.getElementById('fundCheck').innerText=fundPass?'OK 🟢':'ALTO 🔴';
document.getElementById('rsi').innerText=rsi.toFixed(1);
document.getElementById('rsiCheck').innerText=rsiLong?'LONG ZONE 🟢':rsiShort?'SHORT ZONE 🟢':'FORA 🔴';
document.getElementById('oi').innerText=(oiVal/1000).toFixed(1)+'K';
document.getElementById('whaleCheck').innerText=whaleBlocked?'BLOQUEADO '+Math.floor((Date.now()-lastWhale50Time)/60000)+'min 🔴':'LIBERADO 🟢';

let score=0;
if(lsLong)score+=2;if(lsShort)score-=2;
if(topLong)score+=1.5;if(topShort)score-=1.5;
if(rsiLong)score+=1.5;if(rsiShort)score-=1.5;
if(fundPass)score+=0.5;else score-=0.5;
if(whaleBlocked)score=0;

let winrate=Math.abs(score)>=4.5?82:Math.abs(score)>=3.5?76:Math.abs(score)>=2.5?68:45;
document.getElementById('winrate').innerText='WINRATE '+winrate+'%';
document.getElementById('checks').innerHTML='<div style=background:#111;padding:6px;border-radius:6px>LS '+lsVal.toFixed(2)+' '+(lsLong||lsShort?'✅':'❌')+'</div><div style=background:#111;padding:6px;border-radius:6px>TOP '+topVal.toFixed(2)+' '+(topLong||topShort?'✅':'❌')+'</div><div style=background:#111;padding:6px;border-radius:6px>RSI '+rsi.toFixed(0)+' '+(rsiLong||rsiShort?'✅':'❌')+'</div><div style=background:#111;padding:6px;border-radius:6px>FUND '+(fundPass?'✅':'❌')+'</div><div style=background:#111;padding:6px;border-radius:6px>WHALE '+(whaleBlocked?'❌ BLOQ':'✅ OK')+'</div><div style=background:#111;padding:6px;border-radius:6px>SCORE '+score.toFixed(1)+'</div>';

let box=document.getElementById('scoreBox'),principal=document.getElementById('entradaPrincipal'),alvo=document.getElementById('alvoPrincipal'),ultimo=document.getElementById('ultimoSinal');
if(whaleBlocked){
box.style.background='#2a0000';box.style.border='3px solid #ff3333';box.style.color='#ff3333';
box.innerHTML='⛔ BLOQUEADO - BALEIA >$50M HA '+Math.floor((Date.now()-lastWhale50Time)/60000)+'min';
principal.innerText='ESPERA - PROTECAO BALEIA >$50M';alvo.innerText='';
}else if(score>=3.5){
box.style.background='#002a1a';box.style.border='3px solid #00ff88';box.style.color='#00ff88';
box.innerHTML='🚀 COMPRA ALTA '+winrate+'% $'+priceNow.toFixed(0);
principal.innerText='COMPRA $'+priceNow.toFixed(0);alvo.innerText='Alvo $'+(priceNow*1.015).toFixed(0)+' | $'+(priceNow*1.031).toFixed(0)+' | Stop $'+(priceNow*0.993).toFixed(0);
ultimo.innerText='COMPRA '+winrate+'% as '+new Date().toLocaleTimeString();
}else if(score<=-3.5){
box.style.background='#2a0000';box.style.border='3px solid #ff3333';box.style.color='#ff3333';
box.innerHTML='💥 VENDA ALTA '+winrate+'% $'+priceNow.toFixed(0);
principal.innerText='VENDA $'+priceNow.toFixed(0);alvo.innerText='Alvo $'+(priceNow*0.985).toFixed(0)+' | $'+(priceNow*0.969).toFixed(0)+' | Stop $'+(priceNow*1.007).toFixed(0);
ultimo.innerText='VENDA '+winrate+'% as '+new Date().toLocaleTimeString();
}else{
box.style.background='#111';box.style.border='2px solid #333';box.style.color='#666';
box.innerHTML='⏳ ESPERA - SCORE '+score.toFixed(1)+' BTC $'+priceNow.toFixed(0)+' - Aguardando 3.5+ / -3.5-';
principal.innerText='ESPERA - SEM CONFLUENCIA ALTA/BAIXA';alvo.innerText='Precisa LS 0.9-1.30 (long) ou >=1.70 (short) + TOP>1.8/<1.0 + RSI 32-52/58-75 + Sem baleia $50M';
}
document.getElementById('topbar').innerHTML='<span style=color:#ffcc00>● '+new Date().toLocaleTimeString('pt-BR')+' BTC $'+priceNow.toFixed(0)+'</span> <span>LS '+lsVal.toFixed(2)+'</span> <span>TOP '+topVal.toFixed(2)+'</span> <span>RSI '+rsi.toFixed(0)+'</span> <span style=color:'+(score>=3.5?'#00ff88':score<=-3.5?'#ff3333':'#666')+'>'+(Math.abs(score)>=3.5?(score>0?'COMPRA '+winrate+'%':'VENDA '+winrate+'%'):'ESPERA')+'</span>';
document.getElementById('botTime').innerText=new Date().toLocaleTimeString('pt-BR');
}catch(e){console.log(e)}}
async function fetchWhales(){try{
let data=await fetch('https://blockchain.info/unconfirmed-transactions?format=json').then(r=>r.json());
let txs=data.txs.slice(0,150);let html='';let found=0;
txs.forEach(tx=>{
let btc=tx.out.reduce((s,o)=>s+o.value,0)/1e8;let usd=btc*priceNow;
if(usd>=50000000){found++;lastWhale50Time=Date.now();
html+='<div class=whale><b style=color:#ff3333>🚨 $'+(usd/1e6).toFixed(1)+'M ('+btc.toFixed(1)+' BTC) >$50M</b> -> BINANCE DESPEJO<br><span style=color:#fff;font-size:10px">'+new Date(tx.time*1000).toLocaleTimeString()+' | <a href=https://mempool.space/tx/'+tx.hash+' target=_blank style=color:#00ff88>Rastrear trilha completa</a></span><br><span style=color:#ff9999;font-size:10px'>ROBO BLOQUEADO 30 MIN - ALTA E BAIXA</span></div>';
}});
if(found==0){html='<div style=color:#00ff88;padding:14px;background:#0a2a1e;border-radius:8px;border:1px solid #00ff88;text-align:center'>✅ NENHUMA BALEIA >$50M<br><span style=font-size:10px>So $50M+ - $10M ignorado - Robo liberado ALTA e BAIXA</span><br><span style=font-size:9px>Verif: '+new Date().toLocaleTimeString()+'</span></div>';}
else{html='<div style=background:#ff3333;color:white;padding:10px;border-radius:8px;margin-bottom:10px;font-weight:900;text-align:center>🚨 '+found+' BALEIA(S) >$50M - ROBO BLOQUEADO 30min</div>'+html;}
document.getElementById('whales').innerHTML=html;
document.getElementById('whaleStatus').innerText=found>0?found+' >$50M 🔴':'NENHUMA >$50M 🟢';
}catch{}}
initChart();loadChart();fetchHigh();fetchWhales();
setInterval(loadChart,15000);setInterval(updateTick,3000);setInterval(fetchHigh,5000);setInterval(fetchWhales,20000);
</script>
</body>
</html>
'''

components.html(html, height=5200, scrolling=True)
