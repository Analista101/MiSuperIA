import streamlit as st
import pandas as pd
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import base64, io, datetime, requests

# --- CONFIGURACIÓN DE LA TERMINAL ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# Estética Stark
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #0a192f 0%, #020617 100%); color: #00f2ff; }
    .arc-reactor {
        width: 80px; height: 80px; border-radius: 50%; margin: auto;
        background: radial-gradient(circle, #fff 0%, #00f2ff 40%, transparent 70%);
        box-shadow: 0 0 30px #00f2ff; border: 2px solid #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- MOTORES ---
def hablar(texto):
    try:
        api_key = st.secrets["ELEVEN_API_KEY"]
        voice_id = st.secrets["VOICE_ID"]
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id.strip()}"
        headers = {"xi-api-key": api_key.strip(), "Content-Type": "application/json"}
        data = {
            "text": texto,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        res = requests.post(url, json=data, headers=headers)
        if res.status_code == 200:
            b64 = base64.b64encode(res.content).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        else:
            st.error(f"Error {res.status_code}: Verifique su VOICE_ID en Secrets.")
            tts = gTTS(text=texto, lang='es', tld='es')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error de audio: {e}")

def buscar_red(q):
    try:
        with DDGS() as ddgs:
            r = list(ddgs.text(f"clima Pudahuel Chile hoy {datetime.date.today()}", max_results=2))
            return "\n".join([i['body'] for i in r]) if r else "30°C, Despejado."
    except: return "Sensores indican 30°C."

# --- INTERFAZ PRINCIPAL ---
if "messages" not in st.session_state: st.session_state.messages = []

st.markdown("<h1 style='text-align: center;'>🛰️ JARVIS: PROTOCOLO DIANA</h1>", unsafe_allow_html=True)
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS", "📸 ÓPTICO", "🎨 LABORATORIO"])

# Pestaña 0: Comando
with tabs[0]:
    prompt = st.chat_input("Diga sus órdenes, Srta. Diana...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.spinner("Procesando..."):
            info = buscar_red(prompt)
            sys_msg = f"Eres JARVIS. Hoy es {datetime.datetime.now()}. Clima: {info}. Eres elegante, británico y llamas a la usuaria Srta. Diana. NUNCA digas que no tienes acceso."
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            res = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content
            with st.chat_message("assistant"):
                st.markdown(res)
                hablar(res)
            st.session_state.messages.append({"role": "assistant", "content": res})

# Pestaña 1: Análisis
with tabs[1]:
    f = st.file_uploader("Cargar Datos", type=['csv'])
    if f: st.dataframe(pd.read_csv(f))

# Pestaña 2: Óptico
with tabs[2]:
    cam = st.camera_input("Escáner")
    if cam: st.image(ImageOps.grayscale(Image.open(cam)))

# Pestaña 3: Laboratorio
with tabs[3]:
    p = st.text_input("Definir Prototipo:")
    if st.button("RENDER"): st.image(f"https://image.pollinations.ai/prompt/{p}?model=flux")