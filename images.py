import requests
import streamlit as st
from streamlit_lottie import st_lottie
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


lottie_animation_1 = "https://lottie.host/24867631-b0e7-4393-bb3b-2b8f0179ff34/jC5Oi3G29n.json"
lottie_anime_json = load_lottie_url(lottie_animation_1)

st.title("WELCOME")

st_lottie(lottie_anime_json, key="Hello")

st.markdown('systuuum faar dengeee...')
