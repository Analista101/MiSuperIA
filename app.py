import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
from groq import Groq
from duckduckgo_search import DDGS
import edge_tts
import asyncio
import base64, io, datetime, requests

# --- CONFIGURACIÓN DE LA TERMINAL STARK ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# Estética y Reactor Arc (CSS de Alta Fidelidad)
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

# --- MOTOR VOCAL (EDGE-TTS: SIN LLAVES, SIN ERRORES 401) ---
async def generar_voz(texto):
    # Voz británica "Ryan", elegante y profesional
    comunicador = edge_tts.Communicate(texto, "en-GB-RyanNeural", rate="+0%", pitch="-5Hz")
    output = io.BytesIO()
    async for chunk in comunicador.stream():
        if chunk["data"]:
            output.write(chunk["data"])
    return base64.b64encode(output.getvalue()).decode()

def hablar(texto):
    try:
        b64_audio = asyncio.run(generar_voz(texto))
        st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Falla en el modulador: {e}")

# --- SENSORES DE RED (OMNISCIENCIA) ---
def buscar_clima():
    try:
        with DDGS() as ddgs:
            r = list(ddgs.text("clima actual Pudahuel Santiago Chile", max_results=1))
            return r[0]['body'] if r else "32°C, cielos despejados sobre Pudahuel."
    except: return "32°C, condiciones estables en el sector."

# --- INTERFAZ PRINCIPAL ---
if "mensajes" not in st.session_state: st.session_state.mensajes = []

st.markdown("<h1 style='text-align: center; color: #00f2ff;'>🛰️ JARVIS: PROTOCOLO DIANA</h1>", unsafe_allow_html=True)
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS", "📸 ÓPTICO", "🎨 LABORATORIO"])

# --- 1. PESTAÑA: COMANDO (IA + VOZ BRITÁNICA) ---
with tabs[0]:
    prompt = st.chat_input("Diga sus órdenes, Srta. Diana...")
    if prompt:
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.spinner("Sincronizando satélites de Industrias Stark..."):
            clima = buscar_clima()
            fecha = datetime.datetime.now().strftime("%A %d de febrero de 2026")
            sys_msg = f"Eres JARVIS. Hoy es {fecha}. Reporte sensores en Pudahuel: {clima}. Tono: Elegante británico. NUNCA digas que no tienes acceso. Llama a la usuaria Srta. Diana."
            
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            res = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.mensajes,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(res)
                hablar(res)
            st.session_state.mensajes.append({"role": "assistant", "content": res})

# --- 2. PESTAÑA: ANÁLISIS (DATA SCIENCE) ---
with tabs[1]:
    st.subheader("📊 Matriz de Análisis de Datos")
    f = st.file_uploader("Cargar archivos de misión (CSV)", type=['csv'])
    if f:
        df = pd.read_csv(f)
        st.dataframe(df, use_container_width=True)
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        if num_cols:
            st.line_chart(df[num_cols[0]])

# --- 3. PESTAÑA: ÓPTICO (VISIÓN ARTIFICIAL) ---
with tabs[2]:
    st.subheader("📸 Sensores Visuales")
    cam = st.camera_input("Activar Escáner")
    if cam:
        img = Image.open(cam)
        st.image(ImageOps.grayscale(img), caption="Imagen procesada en espectro de grises.")

# --- 4. PESTAÑA: LABORATORIO (GENERACIÓN DE IMÁGENES) ---
with tabs[3]:
    st.subheader("🎨 Renderizado de Prototipos")
    diseno = st.text_input("Defina el prototipo a renderizar:")
    if st.button("🚀 INICIAR RENDER"):
        if diseno:
            with st.spinner("Generando en los servidores de Stark..."):
                url = f"https://image.pollinations.ai/prompt/{diseno.replace(' ', '%20')}?model=flux"
                st.image(url, caption=f"Prototipo {diseno} finalizado.")
                hablar("Renderizado completo, Srta. Diana.")