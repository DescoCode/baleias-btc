import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout='wide', page_title='LATUS PANORAMA V27', page_icon='🐋')

with open('latus_v27_final.html','r',encoding='utf-8') as file:
    html_code = file.read()

components.html(html_code, height=3500, scrolling=True)
