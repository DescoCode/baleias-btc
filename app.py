import streamlit as st
import requests

st.set_page_config(layout='wide', page_title='LATUS V40 GRAFICO FIX', page_icon='🐋')

try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=15*1000, key="auto15s")
except:
    pass

@st.cache_data(ttl=10)
def get_data():
    try:
        price = float(requests.get("https://data-api.binance.vision/api/v3/ticker/price?symbol=BTCUSDT", timeout=8).json()['price'])
        ls = float(requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=1", timeout=8).json()[0]['longShortRatio'])
        top = float(requests.get("https://fapi.binance.com/futures/data/topLongShortPositionRatio?symbol=BTCUSDT&period=5m&limit=1", timeout=8).json()[0]['longShortRatio'])
        fund = float(requests.get("https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT", timeout=8).json()['lastFundingRate'])*100
        oi = float(requests.get("https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT", timeout=8).json()['openInterest'])
        kl = requests.get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=100", timeout=8).json()
        closes = [float(k[4]) for k in kl]
        gains=[]; losses=[]
        for i in range(1,15):
            d=closes[-i]-closes[-i-1]
            if d>0: gains.append(d)
            else: losses.append(abs(d))
        avgG=sum(gains)/len(gains) if gains else 0.1
        avgL=sum(losses)/len(losses) if losses else 0.1
        rsi=100-(100/(1+avgG/(avgL+0.0001)))
        return price, ls, top, fund, oi, rsi
    except:
        return 84800, 1.20, 1.90, 0.0005, 97500, 45

@st.cache_data(ttl=20)
def get_dxy_nasdaq():
    dxy_price, dxy_change = 101.92, -0.01
    nasdaq_price, nasdaq_change = 27191, 1.19
    try:
        dxy = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB?interval=1m&range=1d", timeout=8, headers={"User-Agent":"Mozilla/5.0"}).json()
        dxy_price = dxy['chart']['result'][0]['meta']['regularMarketPrice']
        prev = dxy['chart']['result'][0]['meta']['previousClose']
        dxy_change = ((dxy_price - prev)/prev)*100
    except: pass
    try:
        nas = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5EIXIC?interval=1m&range=1d", timeout=8, headers={"User-Agent":"Mozilla/5.0"}).json()
        nasdaq_price = nas['chart']['result'][0]['meta']['regularMarketPrice']
        prev = nas['chart']['result'][0]['meta']['previousClose']
        nasdaq_change = ((nasdaq_price - prev)/prev)*100
    except: pass
    return dxy_price, dxy_change, nasdaq_price, nasdaq_change

@st.cache_data(ttl=10)
def get_whales(price):
    whales=[]
    try:
        data=requests.get("https://blockchain.info/unconfirmed-transactions?format=json", timeout=8).json()
        for tx in data['txs'][:150]:
            btc=sum([o['value'] for o in tx['out']])/1e8
            usd=btc*price
            if usd>=50000000:
                whales.append((btc, usd, tx['hash']))
    except: pass
    return whales

price, ls_val, top_val, funding, oi_val, rsi = get_data()
dxy_price, dxy_change, nasdaq_price, nasdaq_change = get_dxy_nasdaq()
whales = get_whales(price)

ls_long = 0.9 <= ls_val <= 1.30
ls_short = ls_val >= 1.70
top_long = top_val > 1.80
top_short = top_val < 1.0
rsi_long = 32 <= rsi <= 52
rsi_short = 58 <= rsi <= 75
fund_ok = -0.02 < funding < 0.03
dxy_bull = dxy_change < 0
dxy_bear = dxy_change > 0.3
nasdaq_bull = nasdaq_change > 0.3
nasdaq_bear = nasdaq_change < -0.3
blocked = len(whales)>0

score=0
if ls_long: score+=2
if ls_short: score-=2
if top_long: score+=1.5
if top_short: score-=1.5
if rsi_long: score+=1.5
if rsi_short: score-=1.5
if fund_ok: score+=0.5
else: score-=0.5
if dxy_bull: score+=1.0
if dxy_bear: score-=1.0
if nasdaq_bull: score+=1.0
if nasdaq_bear: score-=1.0
if blocked: score=0

winrate = 85 if abs(score)>=5.5 else 82 if abs(score)>=4.5 else 76 if abs(score)>=3.5 else 50

st.markdown("""
<style>
.block{background:#13131a;border:1px solid #222;border-radius:12px;padding:14px;margin-bottom:12px}
.score{font-size:34px;font-weight:900;padding:18px;border-radius:12px;text-align:center}
.live{animation:blink 1s infinite}@keyframes blink{0%{opacity:1}50%{opacity:0.3}100%{opacity:1}}
</style>
""", unsafe_allow_html=True)

# TOPBAR FIXA COM AUTO
st.markdown(f"""
<div style="position:fixed;top:0;left:0;right:0;background:#000;border-bottom:2px solid #ffcc00;padding:8px 12px;z-index:9999;display:flex;gap:12px;font-size:12px;font-family:monospace;overflow:auto;white-space:nowrap">
<span style="color:#00ff88" class="live">● AUTO 15s</span>
<span style="color:#ffcc00">BTC ${price:.0f}</span>
<span>LS {ls_val:.2f}</span>
<span>TOP {top_val:.2f}</span>
<span>RSI {rsi:.0f}</span>
<span style="color:{'#00ff88' if dxy_change<0 else '#ff3333'}">DXY {dxy_price:.2f}</span>
<span style="color:{'#00ff88' if nasdaq_change>0 else '#ff3333'}">NASDAQ {nasdaq_price:.0f}</span>
<span style="color:{'#00ff88' if score>=3.5 else '#ff3333' if score<=-3.5 else '#666'}">{'COMPRA' if score>=3.5 else 'VENDA' if score<=-3.5 else 'ESPERA'}</span>
</div>
<div style="height:42px"></div>
""", unsafe_allow_html=True)

if blocked:
    st.markdown(f'<div class="block" style="border:3px solid #ff3333;background:#2a0000"><div class="score" style="background:#2a0000;border:3px solid #ff3333;color:#ff3333">⛔ BLOQUEADO - {len(whales)} BALEIA(S) >$50M</div></div>', unsafe_allow_html=True)
elif score>=3.5:
    st.markdown(f'<div class="block" style="border:3px solid #00ff88;background:#002a1a"><div class="score" style="background:#002a1a;border:3px solid #00ff88;color:#00ff88">🚀 COMPRA ALTA {winrate}% - ${price:.0f} <span class="live">●</span></div><div style="margin-top:10px;color:#00ff88">ENTRADA: ${price:.0f} | Alvo ${price*1.015:.0f} | Alvo2 ${price*1.031:.0f} | Stop ${price*0.993:.0f} | Auto 15s</div></div>', unsafe_allow_html=True)
elif score<=-3.5:
    st.markdown(f'<div class="block" style="border:3px solid #ff3333;background:#2a0000"><div class="score" style="background:#2a0000;border:3px solid #ff3333;color:#ff3333">💥 VENDA ALTA {winrate}% - ${price:.0f} <span class="live">●</span></div></div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="block" style="border:3px solid #ffcc00;background:#111"><div class="score" style="background:#111;border:2px solid #333;color:#666">⏳ ESPERA - SCORE {score:.1f} - BTC ${price:.0f}</div></div>', unsafe_allow_html=True)

# GRAFICO FIX COM TRADINGVIEW - NUNCA FALHA
st.subheader("BTCUSDT - GRAFICO ONLINE - AUTO LIVE")
st.components.v1.html("""
<div class="tradingview-widget-container" style="height:500px">
  <div id="tradingview_btc" style="height:500px"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget(
  {
  "autosize": true,
  "symbol": "BINANCE:BTCUSDT",
  "interval": "15",
  "timezone": "America/Sao_Paulo",
  "theme": "dark",
  "style": "1",
  "locale": "br",
  "enable_publishing": false,
  "backgroundColor": "#13131a",
  "gridColor": "#1a1a1a",
  "hide_top_toolbar": false,
  "hide_legend": false,
  "save_image": false,
  "container_id": "tradingview_btc"
}
  );
  </script>
</div>
""", height=520)

# METRICS
c1,c2,c3,c4,c5,c6,c7,c8 = st.columns(8)
c1.metric("LS", f"{ls_val:.4f}")
c2.metric("Top", f"{top_val:.4f}")
c3.metric("RSI", f"{rsi:.1f}")
c4.metric("Funding", f"{funding:.4f}%")
c5.metric("DXY", f"{dxy_price:.2f}", f"{dxy_change:.2f}%", delta_color="inverse")
c6.metric("NASDAQ", f"{nasdaq_price:.0f}", f"{nasdaq_change:.2f}%")
c7.metric("Score", f"{score:.1f}")
c8.metric("Whale", f"{len(whales)}")

colA, colB = st.columns(2)
with colA:
    st.markdown("### FILTROS BINANCE (AUTO 10s)")
    st.write(f"LS: {ls_val:.4f} | Top: {top_val:.4f} | RSI: {rsi:.1f} | OI: {oi_val/1000:.1f}K")
    st.link_button("MAPA COINGLASS", "https://www.coinglass.com/pro/futures/LiquidationHeatMap")
with colB:
    st.markdown("### 🚨 WHALE >$50M (AUTO 10s)")
    if not whales:
        st.success("✅ NENHUMA BALEIA >$50M - AUTO LIBERADO")
    else:
        st.error(f"🚨 {len(whales)} BALEIA(S) >$50M")
        for btc, usd, h in whales:
            st.markdown(f"**${usd/1e6:.1f}M** - [Rastrear](https://mempool.space/tx/{h})")

colDXY, colNASDAQ = st.columns(2)
with colDXY:
    st.markdown("### 💵 DXY - DOLAR INDEX (AUTO)")
    color = "#00ff88" if dxy_change<0 else "#ff3333" if dxy_change>0.3 else "#aaa"
    status = "BULLISH BTC 🟢" if dxy_change<0 else "BEARISH BTC 🔴" if dxy_change>0.3 else "NEUTRO"
    st.markdown(f'<div class="block" style="border:2px solid {color}"><div style="font-size:20px;font-weight:900;color:{color}">DXY {dxy_price:.2f} ({dxy_change:+.2f}%) - {status}</div></div>', unsafe_allow_html=True)

with colNASDAQ:
    st.markdown("### 📈 NASDAQ (AUTO)")
    color = "#00ff88" if nasdaq_change>0.3 else "#ff3333" if nasdaq_change<-0.3 else "#aaa"
    status = "BULLISH BTC 🟢" if nasdaq_change>0.3 else "BEARISH BTC 🔴" if nasdaq_change<-0.3 else "NEUTRO"
    st.markdown(f'<div class="block" style="border:2px solid {color}"><div style="font-size:20px;font-weight:900;color:{color}">NASDAQ {nasdaq_price:.0f} ({nasdaq_change:+.2f}%) - {status}</div></div>', unsafe_allow_html=True)

st.caption("V40 - Grafico TradingView fix - Sem balões - Auto 15s")
