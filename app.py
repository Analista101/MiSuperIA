import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import base64, io, datetime, requests

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="JARVIS", layout="wide", page_icon="🛰️")

# Estética Stark
st.markdown("<style>.stApp { background: #020617; color: #00f2ff; }</style>", unsafe_allow_html=True)

# --- MOTORES ---
def hablar(texto):
    try:
        # Intentar ElevenLabs con el modelo más compatible
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{st.secrets['VOICE_ID']}"
        headers = {"xi-api-key": st.secrets["ELEVEN_API_KEY"], "Content-Type": "application/json"}
        data = {"text": texto, "model_id": "eleven_multilingual_v1", "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
        
        res = requests.post(url, json=data, headers=headers)
        if res.status_code == 200:
            b64 = base64.b64encode(res.content).decode()
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        else:
            # Respaldo gTTS
            tts = gTTS(text=texto, lang='es', tld='es')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

def buscar_red(q):
    try:
        with DDGS() as ddgs:
            r = list(ddgs.text(f"{q} Chile hoy", max_results=2))
            return "\n".join([i['body'] for i in r])
    except: return "Sin datos"

# --- INTERFAZ ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
if "msg" not in st.session_state: st.session_state.msg = []

st.title("🛰️ JARVIS: PROTOCOLO DIANA")
prompt = st.chat_input("Órdenes, Srta. Diana...")

# Soporte de voz
audio = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic")
if audio:
    audio_bio = io.BytesIO(audio['bytes'])
    audio_bio.name = "audio.wav"
    prompt = client.audio.transcriptions.create(file=audio_bio, model="whisper-large-v3", response_format="text")

if prompt:
    st.session_state.msg.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.spinner("Accediendo a satélites..."):
        info = buscar_red(prompt)
        sys_msg = f"""Eres JARVIS. Hoy es {datetime.datetime.now()}. 
        INFO REAL: {info}. 
        REGLA DE ORO: NO digas que eres una IA o que no tienes acceso. 
        Usa la INFO REAL para responder. Si te preguntan el clima en Pudahuel, lee la INFO REAL y dalo.
        Habla como Paul Bettany (JARVIS), elegante y proactivo. Llama a la usuaria Srta. Diana."""
        
        full_res = client.chat.completions.create(
            messages=[{"role": "system", "content": sys_msg}] + st.session_state.msg,
            model="llama-3.3-70b-versatile"
        ).choices[0].message.content

        with st.chat_message("assistant"):
            st.markdown(full_res)
            hablar(full_res)
        st.session_state.msg.append({"role": "assistant", "content": full_res})