import streamlit as st
import pandas as pd
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import base64, io, datetime, requests

# --- CONFIGURACIÓN DE LA TERMINAL STARK ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# Estética Stark y Reactor Arc
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
    .stChatMessage { background-color: rgba(26, 28, 35, 0.8); border: 1px solid #00f2ff; border-radius: 10px; }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- MOTOR VOCAL ELEVENLABS ---
def hablar(texto):
    try:
        api_key = st.secrets["ELEVEN_API_KEY"]
        voice_id = st.secrets["VOICE_ID"]
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id.strip()}"
        headers = {"xi-api-key": api_key.strip(), "Content-Type": "application/json"}
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
            st.error(f"⚠️ Error {res.status_code}: Verifique el Voice ID en sus Secrets.")
            tts = gTTS(text=texto, lang='es', tld='es')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Falla en el modulador: {e}")

# --- MOTOR DE BÚSQUEDA ---
def buscar_red(q):
    try:
        with DDGS() as ddgs:
            r = list(ddgs.text(f"{q} Chile Pudahuel hoy", max_results=2))
            return "\n".join([i['body'] for i in r]) if r else "Cielo despejado, 32°C."
    except: return "Sensores indican clima estable, 32°C."

# --- INICIALIZACIÓN DE SESIÓN ---
if "messages" not in st.session_state: st.session_state.messages = []

st.markdown("<h1 style='text-align: center;'>🛰️ JARVIS: PROTOCOLO DIANA</h1>", unsafe_allow_html=True)

# --- DEFINICIÓN DE PESTAÑAS (TODAS ACTIVAS) ---
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS", "📸 ÓPTICO", "🎨 LABORATORIO"])

# 1. PESTAÑA: COMANDO (IA + VOZ + MIC)
with tabs[0]:
    col_mic, col_txt = st.columns([1, 4])
    prompt = None
    with col_mic:
        audio_stark = mic_recorder(start_prompt="🎙️ DICTAR", stop_prompt="🛰️ ENVIAR", key="mic_v33")
    
    chat_input = st.chat_input("Diga sus órdenes, Srta. Diana...")
    
    if audio_stark:
        audio_bio = io.BytesIO(audio_stark['bytes'])
        audio_bio.name = "audio.wav"
        client_whisper = Groq(api_key=st.secrets["GROQ_API_KEY"])
        prompt = client_whisper.audio.transcriptions.create(file=audio_bio, model="whisper-large-v3", response_format="text")
    elif chat_input:
        prompt = chat_input

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.spinner("Consultando satélites de Industrias Stark..."):
            info = buscar_red(prompt)
            fecha = datetime.datetime.now().strftime("%A %d de febrero de 2026")
            sys_msg = f"Eres JARVIS. Hoy es {fecha}. Reporte sensores: {info}. Tono: Elegante británico. NUNCA digas que no tienes acceso. Llama a la usuaria Srta. Diana."
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            res = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(res)
                hablar(res)
            st.session_state.messages.append({"role": "assistant", "content": res})

# 2. PESTAÑA: ANÁLISIS (DATOS)
with tabs[1]:
    st.header("📊 Matriz de Análisis de Datos")
    f = st.file_uploader("Cargar registros (CSV)", type=['csv'])
    if f:
        df = pd.read_csv(f)
        st.dataframe(df, use_container_width=True)
        cols = df.select_dtypes(include=['number']).columns.tolist()
        if cols:
            st.subheader("Visualización de Tendencias")
            st.area_chart(df[cols[0]])

# 3. PESTAÑA: ÓPTICO (CAMARA)
with tabs[2]:
    st.header("📸 Escáner Óptico de Reconocimiento")
    cam = st.camera_input("Activar Sensores Visuales")
    if cam:
        img = Image.open(cam)
        filtro = st.radio("Modo de Visión:", ["Normal", "Térmica", "Nocturna"])
        if filtro == "Térmica": img = ImageOps.colorize(ImageOps.grayscale(img), "blue", "red")
        elif filtro == "Nocturna": img = ImageOps.colorize(ImageOps.grayscale(img), "black", "green")
        st.image(img, use_container_width=True)

# 4. PESTAÑA: LABORATORIO (IMÁGENES)
with tabs[3]:
    st.header("🎨 Laboratorio de Prototipos Finales")
    desc = st.text_input("Defina el diseño del prototipo:")
    if st.button("🚀 INICIAR RENDERIZADO"):
        with st.spinner("Generando prototipo en la nube..."):
            url = f"https://image.pollinations.ai/prompt/{desc.replace(' ', '%20')}?model=flux"
            st.image(url, caption="Prototipo finalizado con éxito, Srta. Diana.")
            hablar("Renderizado de prototipo finalizado.")