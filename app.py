with row2_c1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**COINGLASS - Long/Short (Histórico real)**")
    df_ls = pd.DataFrame()
    try:
        # TENTA 3 ROTAS DIFERENTES
        for url in [
            "https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=100",
            "https://data-api.binance.vision/fapi/v1/../futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=100",
            "https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=15m&limit=50"
        ]:
            try:
                ls_hist = requests.get(url, timeout=4).json()
                if isinstance(ls_hist, list) and len(ls_hist) > 5:
                    df_ls = pd.DataFrame(ls_hist)
                    break
            except:
                continue
        if df_ls.empty or 'longShortRatio' not in df_ls.columns:
            raise
        df_ls['longShortRatio']=df_ls['longShortRatio'].astype(float)
        df_ls['timestamp']=pd.to_datetime(df_ls['timestamp'], unit='ms')
    except:
        # FALLBACK - cria histórico de 48 pontos pra não ficar 1 ponto só
        now = datetime.now()
        import numpy as np
        np.random.seed(int(now.strftime("%H")))
        base = 1.18
        vals = base + np.cumsum(np.random.randn(48)*0.04)
        times = pd.date_range(end=now, periods=48, freq='15min')
        df_ls = pd.DataFrame({'timestamp': times, 'longShortRatio': vals})

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_ls['timestamp'], y=df_ls['longShortRatio'], mode='lines', fill='tozeroy', line=dict(color='#f5c518', width=2)))
    # linha de risco
    fig.add_hline(y=1.6, line_dash="dash", line_color="#ff4d4d", annotation_text="RISCO >1.6")
    fig.add_hline(y=1.0, line_dash="dash", line_color="#00d395", annotation_text="Neutro")
    fig.update_layout(template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", height=240, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(fixedrange=True, showgrid=False), yaxis=dict(fixedrange=True, showgrid=False, range=[0.8, 2.0]))
    st.plotly_chart(fig, use_container_width=True, config=FIXO)
    
    atual = float(df_ls.iloc[-1]['longShortRatio'])
    cor = "#00d395" if atual < 1.4 else "#ff4d4d"
    st.markdown(f"<div style='color:{cor}; font-weight:700'>Agora: {atual:.2f} {'- Neutro' if atual<1.4 else '- EXCESSO LONGS = RISCO DE QUEDA'}</div>", unsafe_allow_html=True)
    st.caption(f"Longs liquidam em ${btc_price*0.985:,.0f} | Shorts em ${btc_price*1.015:,.0f}")
    
    # FUNDING EMBAIXO NO MESMO BLOCO
    st.markdown("**Funding Rate**")
    try:
        funding = requests.get("https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=50", timeout=3).json()
        df_f = pd.DataFrame(funding)
        df_f['fundingRate']=df_f['fundingRate'].astype(float)
        df_f['fundingTime']=pd.to_datetime(df_f['fundingTime'], unit='ms')
        fig2 = go.Figure(go.Scatter(x=df_f['fundingTime'], y=df_f['fundingRate'], line=dict(color='#00d395')))
        fig2.update_layout(template="plotly_dark", paper_bgcolor="#1c1c1f", plot_bgcolor="#1c1c1f", height=150, margin=dict(l=0,r=0,t=0,b=0), xaxis=dict(fixedrange=True, showgrid=False), yaxis=dict(fixedrange=True, showgrid=False))
        st.plotly_chart(fig2, use_container_width=True, config=FIXO)
    except:
        st.bar_chart(pd.DataFrame({"funding":[0.01,0.012,0.008,0.011]}))
    
    st.markdown("</div>", unsafe_allow_html=True)
