import streamlit as st, requests, time
NTFY="bot-btc-13981878671"
def alerta(m): requests.post(f"https://ntfy.sh/{NTFY}", data=m.encode(), headers={"Title":"BALEIA $50M","Priority":"high"})
def get_price():
 try: return float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",timeout=5).json()['price'])
 except: return 85000
st.set_page_config(page_title="Radar Baleias")
st.title("🐋 RADAR > $50M")
price=get_price()
st.metric("BTC", f"${price:,.0f}")
try:
 txs=requests.get("https://mempool.space/api/mempool/recent",timeout=10).json()
 tops=[]
 for tx in txs:
  vout=sum(o['value'] for o in tx.get('vout',[]))/1e8
  if vout*price>=50000000: tops.append((vout,vout*price,tx['txid']))
 for btc,usd,txid in sorted(tops,key=lambda x:x[1],reverse=True)[:10]:
  st.error(f"{btc:.1f} BTC (${usd/1e6:.1f}M)")
  if f"a_{txid}" not in st.session_state:
   alerta(f"BALEIA {btc:.0f} BTC ${usd/1e6:.1f}M!")
   st.session_state[f"a_{txid}"]=True
 if not tops: st.success("Sem baleias > $50M agora")
except Exception as e: st.write(e)
if st.button("📲 TESTAR"): alerta("Teste OK!"); st.success("Olha o app ntfy.sh")
time.sleep(20); st.rerun()
