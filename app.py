import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
from groq import Groq
from duckduckgo_search import DDGS
import edge_tts
import asyncio
import base64, io, datetime, requests
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURACIÓN DE LA TERMINAL ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# Estética Stark
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #0a192f 0%, #020617 100%); color: #00f2ff; }
    .arc-reactor {
        width: 80px; height: 80px; border-radius: 50%; margin: 20px auto;
        background: radial-gradient(circle, #fff 0%, #00f2ff 40%, transparent 70%);
        box-shadow: 0 0 30px #00f2ff; border: 2px solid #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    .stTabs [data-baseweb="tab"] { color: #00f2ff !important; font-weight: bold; font-size: 18px; }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- MOTOR VOCAL ---
async def generar_voz(texto):
    comunicador = edge_tts.Communicate(texto, "en-GB-RyanNeural", rate="+0%", pitch="-5Hz")
    output = io.BytesIO()
    async for chunk in comunicador.stream():
        if chunk["type"] == "audio":
            output.write(chunk["data"])
    return base64.b64encode(output.getvalue()).decode()

def hablar(texto):
    try:
        b64_audio = asyncio.run(generar_voz(texto))
        st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

# --- INTERFAZ PRINCIPAL ---
if "mensajes" not in st.session_state: st.session_state.mensajes = []

st.markdown("<h1 style='text-align: center; color: #00f2ff;'>🛰️ JARVIS: SISTEMA INTEGRADO DIANA</h1>", unsafe_allow_html=True)
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS UNIVERSAL", "📸 ÓPTICO", "🎨 LABORATORIO"])

# --- 1. PESTAÑA: COMANDO ---
with tabs[0]:
    col_mic, col_txt = st.columns([1, 4])
    prompt = None
    with col_mic:
        audio_stark = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_v43")
    chat_input = st.chat_input("Órdenes, Srta. Diana...")
    if audio_stark:
        audio_bio = io.BytesIO(audio_stark['bytes'])
        audio_bio.name = "audio.wav"
        prompt = Groq(api_key=st.secrets["GROQ_API_KEY"]).audio.transcriptions.create(file=audio_bio, model="whisper-large-v3", response_format="text")
    elif chat_input: prompt = chat_input

    if prompt:
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = client.chat.completions.create(
            messages=[{"role": "system", "content": "Eres JARVIS, elegante británico. Llama a la usuaria Srta. Diana."}] + st.session_state.mensajes,
            model="llama-3.3-70b-versatile"
        ).choices[0].message.content
        with st.chat_message("assistant"):
            st.markdown(res)
            hablar(res)
        st.session_state.mensajes.append({"role": "assistant", "content": res})

# --- 2. PESTAÑA: ANÁLISIS UNIVERSAL (LECTURA DE CUALQUIER FORMATO) ---
with tabs[1]:
    st.subheader("📊 Análisis de Datos Multi-Formato")
    # Cargador configurado para aceptar diversos formatos
    f = st.file_uploader("Cargar archivos (Excel, CSV, TXT)", type=['csv', 'xlsx', 'xls', 'txt'])
    
    if f:
        try:
            # Lógica para determinar el tipo de archivo y leerlo
            if f.name.endswith('.csv'):
                df = pd.read_csv(f)
            elif f.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(f)
            elif f.name.endswith('.txt'):
                df = pd.read_csv(f, sep=None, engine='python') # Intenta detectar el separador solo
            
            st.success(f"Protocolo de lectura completado: {f.name}")
            st.dataframe(df, use_container_width=True)
            
            if st.button("🧠 ANÁLISIS DE IA AVANZADO"):
                summary = df.head(10).to_string() # Enviamos una muestra para análisis
                res_ia = Groq(api_key=st.secrets["GROQ_API_KEY"]).chat.completions.create(
                    messages=[{"role": "user", "content": f"Analiza estos datos brevemente como JARVIS para la Srta. Diana: {summary}"}],
                    model="llama-3.3-70b-versatile"
                ).choices[0].message.content
                st.info(res_ia)
                hablar("Análisis de datos finalizado, Srta. Diana.")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

# (Mantenemos Pestaña ÓPTICO y LABORATORIO con las mejoras anteriores)
with tabs[2]:
    st.subheader("📸 Sensores Visuales")
    cam = st.camera_input("Activar Escáner")
    if cam:
        img = Image.open(cam)
        modo = st.select_slider("Filtro:", options=["Normal", "Grises", "Térmico", "Nocturno"])
        if modo == "Grises": img = ImageOps.grayscale(img)
        elif modo == "Térmico": img = ImageOps.colorize(ImageOps.grayscale(img), "blue", "red")
        elif modo == "Nocturno": img = ImageOps.colorize(ImageOps.grayscale(img), "black", "green")
        st.image(img, use_container_width=True)

with tabs[3]:
    st.subheader("🎨 Estación de Diseño")
    c1, c2 = st.columns([2, 1])
    with c2:
        estilo = st.selectbox("Estilo Visual:", ["Cinematic", "Blueprint", "Cyberpunk", "Hyper-Realistic"])
    with c1:
        diseno = st.text_area("Descripción del prototipo:")
        if st.button("🚀 RENDER"):
            url = f"https://image.pollinations.ai/prompt/{diseno.replace(' ', '%20')}%20{estilo}?model=flux"
            st.image(url, caption="Renderizado completo.")
            hablar("Prototipo finalizado, Srta. Diana.")