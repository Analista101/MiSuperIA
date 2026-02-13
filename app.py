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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN DE LA TERMINAL STARK ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# Estética Stark e Inyección de CSS
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

# --- MOTORES DE SOPORTE ---
def hablar(texto):
    try:
        tts = gTTS(text=texto, lang='es', tld='es')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

def buscar_red(consulta):
    try:
        with DDGS() as ddgs:
            r = list(ddgs.text(f"{consulta} hoy 2026", max_results=3))
            return "\n".join([i['body'] for i in r]) if r else "SISTEMA_OFFLINE"
    except: return "SISTEMA_OFFLINE"

# --- INICIALIZACIÓN DE ESTADOS ---
if "messages" not in st.session_state: st.session_state.messages = []

# --- INTERFAZ DE NAVEGACIÓN ---
st.markdown("<h1 style='text-align: center;'>🛰️ PROTOCOLO: DIANA</h1>", unsafe_allow_html=True)
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS", "📸 ÓPTICO", "🎨 LABORATORIO", "📧 MENSAJERÍA"])

# --- PESTAÑA 0: COMANDO CENTRAL (VOZ Y TEXTO) ---
with tabs[0]:
    st.subheader("🎙️ Entrada Neuronal (Voz y Texto)")
    
    col_mic, col_txt = st.columns([1, 4])
    prompt = None

    with col_mic:
        audio_stark = mic_recorder(start_prompt="🎙️ DICTAR", stop_prompt="🛰️ ENVIAR", key="mic_central")
    
    if audio_stark:
        client_whisper = Groq(api_key=st.secrets["GROQ_API_KEY"])
        audio_bio = io.BytesIO(audio_stark['bytes'])
        audio_bio.name = "audio.wav"
        prompt = client_whisper.audio.transcriptions.create(file=audio_bio, model="whisper-large-v3", response_format="text")
    
    chat_input = st.chat_input("Diga sus órdenes, Srta. Diana...")
    if chat_input: prompt = chat_input

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("Procesando en servidores Stark..."):
            info = buscar_red(prompt)
            fecha = datetime.datetime.now().strftime("%A, %d de febrero de 2026")
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            sys_msg = f"Eres JARVIS. Hoy es {fecha}. Datos: {info}. Habla elegante y llama a la usuaria 'Srta. Diana'."
            
            res = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content

            with st.chat_message("assistant"):
                st.markdown(res)
                hablar(res)
            st.session_state.messages.append({"role": "assistant", "content": res})

# --- PESTAÑA 1: ANÁLISIS ---
with tabs[1]:
    st.header("📊 Matriz de Datos")
    f = st.file_uploader("Cargar registros", type=['csv', 'xlsx'])
    if f:
        df = pd.read_csv(f) if 'csv' in f.name else pd.read_excel(f)
        st.metric("Puntos de Datos", len(df))
        st.dataframe(df, use_container_width=True)
        cols_num = df.select_dtypes(include=['number']).columns.tolist()
        if cols_num:
            y = st.selectbox("Métrica a proyectar:", cols_num)
            st.area_chart(df[y])

# --- PESTAÑA 2: ÓPTICO ---
with tabs[2]:
    st.header("📸 Escáner Óptico")
    cam = st.camera_input("Iniciado reconocimiento facial...")
    if cam:
        img = Image.open(cam)
        filtro = st.radio("Protocolo visual:", ["Normal", "Térmica", "Nocturna", "Rayos X"])
        if filtro == "Térmica": img = ImageOps.colorize(ImageOps.grayscale(img), "blue", "red")
        elif filtro == "Nocturna": img = ImageOps.colorize(ImageOps.grayscale(img), "black", "green")
        elif filtro == "Rayos X": img = img.filter(ImageFilter.FIND_EDGES)
        st.image(img, use_container_width=True)

# --- PESTAÑA 3: LABORATORIO ---
with tabs[3]:
    st.header("🎨 Renderizado Mark II")
    desc = st.text_input("Defina el prototipo:")
    est = st.select_slider("Estilo:", ["Boceto", "CAD", "Holograma", "Realista", "Cinemático"])
    if st.button("🚀 INICIAR RENDER"):
        url = f"https://image.pollinations.ai/prompt/{desc.replace(' ', '%20')}%20{est}%20stark%20style?model=flux"
        st.image(url, caption="Prototipo finalizado")
        hablar("Renderizado listo.")

# --- PESTAÑA 4: MENSAJERÍA ---
with tabs[4]:
    st.header("📧 Transmisor")
    dest = st.text_input("Destinatario:", "sandoval0193@gmail.com")
    cuerpo = st.text_area("Contenido del mensaje:")
    if st.button("📤 TRANSMITIR"):
        st.success(f"Señal enviada a {dest}.")
        hablar("Mensaje enviado con éxito, Srta. Diana.")