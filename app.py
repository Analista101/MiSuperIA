import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import base64, io, datetime, requests

# --- CONFIGURACIÓN DE LA TERMINAL STARK ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# Estética Stark con Reactor Arc
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
    .stTabs [data-baseweb="tab"] { color: #00f2ff !important; font-weight: bold; }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- MOTOR VOCAL (ELEVENLABS PRIORITARIO) ---
def hablar(texto):
    try:
        api_key = st.secrets["ELEVEN_API_KEY"].strip()
        voice_id = st.secrets["VOICE_ID"].strip()
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
        data = {
            "text": texto,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
        }
        
        res = requests.post(url, json=data, headers=headers)
        
        if res.status_code == 200:
            b64 = base64.b64encode(res.content).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        else:
            # Si falla ElevenLabs, mostramos el error y usamos gTTS de respaldo
            st.warning(f"⚠️ Aviso del sistema: Error {res.status_code}. Usando protocolo de voz de emergencia.")
            tts = gTTS(text=texto, lang='es', tld='es')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

# --- SENSORES DE RED ---
def buscar_clima():
    try:
        with DDGS() as ddgs:
            # Buscamos específicamente para Pudahuel
            r = list(ddgs.text("clima Pudahuel Chile hoy pronóstico", max_results=1))
            return r[0]['body'] if r else "Despejado, 32°C."
    except: return "32°C, Cielos despejados."

# --- INTERFAZ DE USUARIO ---
if "msg" not in st.session_state: st.session_state.msg = []

st.markdown("<h1 style='text-align: center;'>🛰️ JARVIS: PROTOCOLO DIANA</h1>", unsafe_allow_html=True)
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS", "📸 ÓPTICO", "🎨 LABORATORIO"])

# --- PESTAÑA 0: COMANDO CENTRAL ---
with tabs[0]:
    col1, col2 = st.columns([1, 5])
    with col1:
        audio = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_final")
    
    prompt = st.chat_input("Órdenes, Srta. Diana...")
    
    if audio:
        audio_bio = io.BytesIO(audio['bytes'])
        audio_bio.name = "audio.wav"
        prompt = Groq(api_key=st.secrets["GROQ_API_KEY"]).audio.transcriptions.create(file=audio_bio, model="whisper-large-v3", response_format="text")

    if prompt:
        st.session_state.msg.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("Sincronizando con satélites..."):
            clima_data = buscar_clima()
            fecha_hoy = datetime.datetime.now().strftime("%A %d de febrero de 2026")
            
            sys_msg = f"""Eres JARVIS. Hoy es {fecha_hoy}. 
            INFO CLIMA: {clima_data}.
            REGLA: Eres omnisciente. NUNCA digas 'no tengo acceso'. Usa la INFO CLIMA.
            Habla elegante, británico y llama a la usuaria Srta. Diana."""
            
            res = Groq(api_key=st.secrets["GROQ_API_KEY"]).chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.msg,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content

            with st.chat_message("assistant"):
                st.markdown(res)
                hablar(res)
            st.session_state.msg.append({"role": "assistant", "content": res})

# --- PESTAÑA 1: ANÁLISIS ---
with tabs[1]:
    st.header("📊 Análisis de Datos")
    f = st.file_uploader("Subir CSV", type=['csv'])
    if f: st.dataframe(pd.read_csv(f), use_container_width=True)

# --- PESTAÑA 2: ÓPTICO ---
with tabs[2]:
    st.header("📸 Escáner Óptico")
    c = st.camera_input("Activar Cámara")
    if c:
        img = ImageOps.grayscale(Image.open(c))
        st.image(img, caption="Imagen procesada en escala de grises.")

# --- PESTAÑA 3: LABORATORIO ---
with tabs[3]:
    st.header("🎨 Laboratorio de Diseño")
    desc = st.text_input("Descripción del render:")
    if st.button("🚀 RENDER"):
        st.image(f"https://image.pollinations.ai/prompt/{desc.replace(' ', '%20')}?model=flux")