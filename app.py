import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
from groq import Groq
from duckduckgo_search import DDGS
import edge_tts
import asyncio
import base64, io, datetime, requests
from streamlit_mic_recorder import mic_recorder # <--- Sensor de audio recuperado

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
    .stTabs [data-baseweb="tab"] { color: #00f2ff !important; font-weight: bold; }
    .stChatMessage { background-color: rgba(26, 28, 35, 0.8); border: 1px solid #00f2ff; border-radius: 10px; }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- MOTOR VOCAL (CORRECCIÓN 'DATA') ---
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
    except Exception as e:
        st.error(f"Falla en el modulador: {e}")

# --- SENSORES DE RED ---
def buscar_clima():
    try:
        with DDGS() as ddgs:
            r = list(ddgs.text("clima actual Pudahuel Santiago Chile", max_results=1))
            return r[0]['body'] if r else "32°C, despejado."
    except: return "32°C, condiciones estables."

# --- INICIALIZACIÓN ---
if "mensajes" not in st.session_state: st.session_state.mensajes = []

st.markdown("<h1 style='text-align: center; color: #00f2ff;'>🛰️ JARVIS: PROTOCOLO DIANA</h1>", unsafe_allow_html=True)
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS", "📸 ÓPTICO", "🎨 LABORATORIO"])

# --- 1. PESTAÑA: COMANDO (MICRÓFONO REINTEGRADO) ---
with tabs[0]:
    col_mic, col_txt = st.columns([1, 4])
    prompt = None
    with col_mic:
        # El botón de dictado ha vuelto
        audio_stark = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_v41")
    
    chat_input = st.chat_input("Diga sus órdenes, Srta. Diana...")
    
    if audio_stark:
        audio_bio = io.BytesIO(audio_stark['bytes'])
        audio_bio.name = "audio.wav"
        client_whisper = Groq(api_key=st.secrets["GROQ_API_KEY"])
        prompt = client_whisper.audio.transcriptions.create(file=audio_bio, model="whisper-large-v3", response_format="text")
    elif chat_input:
        prompt = chat_input

    if prompt:
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.spinner("Sincronizando satélites..."):
            clima = buscar_clima()
            sys_msg = f"Eres JARVIS. Clima en Pudahuel: {clima}. Tono: Elegante británico. NUNCA digas que no tienes acceso. Llama a la usuaria Srta. Diana."
            res = Groq(api_key=st.secrets["GROQ_API_KEY"]).chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.mensajes,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(res)
                hablar(res)
            st.session_state.mensajes.append({"role": "assistant", "content": res})

# --- 2. PESTAÑA: ANÁLISIS (GRÁFICOS REINTEGRADOS) ---
with tabs[1]:
    st.subheader("📊 Análisis de Datos")
    f = st.file_uploader("Subir archivos CSV", type=['csv'])
    if f:
        df = pd.read_csv(f)
        st.dataframe(df, use_container_width=True)
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        if num_cols:
            st.area_chart(df[num_cols[0]]) # Gráfico recuperado

# --- 3. PESTAÑA: ÓPTICO (FILTROS REINTEGRADOS) ---
with tabs[2]:
    st.subheader("📸 Sensores Visuales")
    cam = st.camera_input("Activar Escáner")
    if cam:
        img = Image.open(cam)
        modo = st.radio("Filtro:", ["Normal", "Grises", "Térmico", "Nocturno"])
        if modo == "Grises": img = ImageOps.grayscale(img)
        elif modo == "Térmico": img = ImageOps.colorize(ImageOps.grayscale(img), "blue", "red")
        elif modo == "Nocturno": img = ImageOps.colorize(ImageOps.grayscale(img), "black", "green")
        st.image(img, use_container_width=True)

# --- 4. PESTAÑA: LABORATORIO ---
with tabs[3]:
    st.subheader("🎨 Renderizado")
    diseno = st.text_input("Defina el prototipo:")
    if st.button("🚀 RENDER"):
        url = f"https://image.pollinations.ai/prompt/{diseno.replace(' ', '%20')}?model=flux"
        st.image(url, caption="Prototipo finalizado.")
        hablar("Renderizado completo, Srta. Diana.")