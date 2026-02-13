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

# Estética y Reactor Arc
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
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- MOTOR VOCAL CORREGIDO (v40.0) ---
async def generar_voz(texto):
    # Voz británica elegante
    comunicador = edge_tts.Communicate(texto, "en-GB-RyanNeural", rate="+0%", pitch="-5Hz")
    output = io.BytesIO()
    # Corrección del error 'data': leemos directamente del stream
    async for chunk in comunicador.stream():
        if chunk["type"] == "audio":
            output.write(chunk["data"])
    return base64.b64encode(output.getvalue()).decode()

def hablar(texto):
    try:
        # Ejecutamos la corrutina de audio
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

# --- PESTAÑA 0: COMANDO ---
with tabs[0]:
    prompt = st.chat_input("Diga sus órdenes, Srta. Diana...")
    if prompt:
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.spinner("Sincronizando satélites..."):
            clima = buscar_clima()
            sys_msg = f"Eres JARVIS. Hoy es {datetime.datetime.now()}. Clima en Pudahuel: {clima}. Tono: Elegante británico. NUNCA digas que no tienes acceso. Llama a la usuaria Srta. Diana."
            
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            res = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.mensajes,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(res)
                hablar(res)
            st.session_state.mensajes.append({"role": "assistant", "content": res})

# --- PESTAÑA 1: ANÁLISIS ---
with tabs[1]:
    st.subheader("📊 Análisis de Datos")
    f = st.file_uploader("Subir CSV", type=['csv'])
    if f: st.dataframe(pd.read_csv(f), use_container_width=True)

# --- PESTAÑA 2: ÓPTICO ---
with tabs[2]:
    st.subheader("📸 Sensores Visuales")
    cam = st.camera_input("Activar Escáner")
    if cam:
        img = ImageOps.grayscale(Image.open(cam))
        st.image(img, caption="Imagen procesada.")

# --- PESTAÑA 3: LABORATORIO ---
with tabs[3]:
    st.subheader("🎨 Laboratorio de Diseño")
    diseno = st.text_input("Defina el prototipo:")
    if st.button("🚀 INICIAR RENDER"):
        if diseno:
            url = f"https://image.pollinations.ai/prompt/{diseno.replace(' ', '%20')}?model=flux"
            st.image(url, caption=f"Prototipo {diseno} finalizado.")
            hablar("Renderizado completo, Srta. Diana.")