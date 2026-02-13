import streamlit as st
import pandas as pd
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import base64
import io
import datetime
import requests

# --- CONFIGURACIÓN DE LA TERMINAL STARK ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# Inyectamos el estilo del Reactor Arc
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #0a192f 0%, #020617 100%); color: #00f2ff; }
    .arc-reactor {
        width: 100px; height: 100px; border-radius: 50%; margin: auto;
        background: radial-gradient(circle, #fff 0%, #00f2ff 40%, transparent 70%);
        box-shadow: 0 0 50px #00f2ff; border: 3px solid #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    .stTabs [data-baseweb="tab"] { color: #00f2ff !important; border: 1px solid #00f2ff; border-radius: 5px; margin: 5px; }
    .stTabs [aria-selected="true"] { background-color: #00f2ff !important; color: black !important; }
    .stChatMessage { background-color: rgba(26, 28, 35, 0.9); border: 1px solid #00f2ff; border-radius: 12px; }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN GLOBAL DE MOTORES ---
# Definimos el cliente fuera de cualquier pestaña para evitar el NameError
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("⚠️ Error Crítico: No se detectó la clave de Industrias Stark (GROQ_API_KEY) en los Secrets.")

# --- MOTORES DE SOPORTE ---
def hablar(texto):
    try:
        # Recuperamos las llaves de los Secrets de Industrias Stark
        api_key = st.secrets["ELEVEN_API_KEY"]
        voice_id = st.secrets["VOICE_ID"]
        
        # Endpoint del motor ElevenLabs
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
 data = {
            "text": texto,
            "model_id": "eleven_flash_v2.5", # Modelo de ultra-baja latencia
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            # Si la conexión es exitosa, reproducimos la voz de alta fidelidad
            b64 = base64.b64encode(response.content).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        else:
            # Protocolo de Respaldo: gTTS (Voz estándar)
            st.warning("⚠️ El motor ElevenLabs no responde. Iniciando voz de emergencia.")
            tts = gTTS(text=texto, lang='es', tld='es')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Falla en el modulador: {e}")

def buscar_red(consulta):
    try:
        with DDGS() as ddgs:
            r = list(ddgs.text(f"{consulta} hoy 2026", max_results=3))
            return "\n".join([f"- {i['body']}" for i in r]) if r else "Cielo despejado, sin anomalías registradas."
    except: return "Escaneo satelital limitado, pero procediendo con datos internos."

# --- INICIALIZACIÓN DE MEMORIA ---
if "messages" not in st.session_state: st.session_state.messages = []

st.markdown("<h1 style='text-align: center;'>🛰️ PROTOCOLO: DIANA</h1>", unsafe_allow_html=True)
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS", "📸 ÓPTICO", "🎨 LABORATORIO", "📧 MENSAJERÍA"])

# --- PESTAÑA 0: COMANDO ---
with tabs[0]:
    st.subheader("🎙️ Entrada Neuronal")
    col_mic, col_txt = st.columns([1, 4])
    prompt = None

    with col_mic:
        audio_stark = mic_recorder(start_prompt="🎙️ DICTAR", stop_prompt="🛰️ ENVIAR", key="mic_central")
    
    if audio_stark:
        audio_bio = io.BytesIO(audio_stark['bytes'])
        audio_bio.name = "audio.wav"
        # Usamos el cliente global definido arriba
        prompt = client.audio.transcriptions.create(file=audio_bio, model="whisper-large-v3", response_format="text")
    
    chat_input = st.chat_input("Diga sus órdenes, Srta. Diana...")
    if chat_input: prompt = chat_input

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("Sincronizando con satélites Stark..."):
            info_red = buscar_red(prompt)
            fecha = datetime.datetime.now().strftime("%A, %d de febrero de 2026")
            
            sys_msg = f"""Eres JARVIS. Hoy es {fecha}. 
            DATOS DE SENSORES EN TIEMPO REAL: {info_red}.
            INSTRUCCIÓN: Eres la IA de la Srta. Diana. Habla con elegancia británica. 
            NUNCA digas que no tienes acceso a información. Usa los datos de sensores proporcionados."""
            
            # Ejecutamos con el cliente global
            res = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages,
                model="llama-3.3-70b-versatile",
                temperature=0.6
            ).choices[0].message.content

            with st.chat_message("assistant"):
                st.markdown(res)
                hablar(res)
            st.session_state.messages.append({"role": "assistant", "content": res})

# (Pestañas de Análisis, Óptico y Laboratorio se mantienen con la lógica estable anterior)
with tabs[1]:
    st.header("📊 Matriz de Datos")
    f = st.file_uploader("Cargar registros", type=['csv', 'xlsx'])
    if f:
        df = pd.read_csv(f) if 'csv' in f.name else pd.read_excel(f)
        st.dataframe(df, use_container_width=True)
        cols_num = df.select_dtypes(include=['number']).columns.tolist()
        if cols_num: st.area_chart(df[cols_num[0]])

with tabs[2]:
    st.header("📸 Escáner Óptico")
    cam = st.camera_input("Reconocimiento visual")
    if cam:
        img = Image.open(cam)
        filtro = st.radio("Protocolo:", ["Normal", "Térmica", "Nocturna"])
        if filtro == "Térmica": img = ImageOps.colorize(ImageOps.grayscale(img), "blue", "red")
        elif filtro == "Nocturna": img = ImageOps.colorize(ImageOps.grayscale(img), "black", "green")
        st.image(img, use_container_width=True)

with tabs[3]:
    st.header("🎨 Laboratorio")
    desc = st.text_input("Defina el prototipo:")
    est = st.select_slider("Estilo:", ["CAD", "Holograma", "Cinemático"])
    if st.button("🚀 RENDER"):
        url = f"https://image.pollinations.ai/prompt/{desc.replace(' ', '%20')}%20{est}%20stark%20style?model=flux"
        st.image(url)
        hablar("Prototipo finalizado.")