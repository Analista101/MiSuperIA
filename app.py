import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
import google.generativeai as genai
import edge_tts
import asyncio
import base64, io, datetime, requests
from streamlit_mic_recorder import mic_recorder

# --- 1. CONFIGURACIÓN INICIAL (CHASIS) ---
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

# --- 2. CONFIGURACIÓN DEL NÚCLEO (ENERGÍA) ---
model_chat = None
if "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model_chat = genai.GenerativeModel('gemini-1.5-flash-latest')
    except Exception as e:
        st.error(f"Falla en la inicialización del núcleo: {e}")
else:
    st.warning("🛰️ Srta. Diana, los sistemas están en modo offline. Falta la GOOGLE_API_KEY en Secrets.")

# --- 3. MOTOR VOCAL ---
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

# --- 4. INTERFAZ DE USUARIO (SISTEMAS ACTIVOS) ---
st.markdown("<h1 style='text-align: center; color: #00f2ff;'>🛰️ JARVIS: SISTEMA INTEGRADO DIANA</h1>", unsafe_allow_html=True)

if "mensajes" not in st.session_state: st.session_state.mensajes = []

# Pestañas principales
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS UNIVERSAL", "📸 ÓPTICO", "🎨 LABORATORIO CREATIVO"])

# --- PESTAÑA 0: COMANDO ---
with tabs[0]:
    col_mic, col_txt = st.columns([1, 5])
    input_usuario = None
    with col_mic:
        audio_stark = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_v103")
    with col_txt:
        chat_input = st.chat_input("Diga sus órdenes, Srta. Diana...")

    if chat_input: input_usuario = chat_input
    
    if input_usuario and model_chat:
        st.session_state.mensajes.append({"role": "user", "content": input_usuario})
        with st.chat_message("user"): st.markdown(input_usuario)
        
        response = model_chat.generate_content(f"Eres JARVIS. Llama a la usuaria Srta. Diana. Responde a: {input_usuario}")
        res = response.text
        with st.chat_message("assistant"):
            st.markdown(res)
            hablar(res)
        st.session_state.mensajes.append({"role": "assistant", "content": res})

# --- PESTAÑA 1: ANÁLISIS UNIVERSAL ---
with tabs[1]:
    st.subheader("📊 Análisis de Datos y Archivos")
    archivo = st.file_uploader("Inyectar Imagen o Docx:", type=["png", "jpg", "jpeg", "docx"], key="up103")
    if archivo and st.button("🔍 ANALIZAR ARCHIVO"):
        if model_chat:
            with st.spinner("Procesando..."):
                # Simplificación para asegurar que funcione
                img = Image.open(archivo) if not archivo.name.endswith('.docx') else archivo
                resp = model_chat.generate_content(["Analiza detalladamente como JARVIS.", img])
                st.info(resp.text)
                hablar("Análisis completado.")

# --- PESTAÑA 2: ÓPTICO ---
with tabs[2]:
    st.subheader("📸 Sensores Ópticos")
    cam = st.camera_input("Escáner Activo", key="cam_v103")
    if cam and st.button("🔍 ANÁLISIS TÁCTICO"):
        if model_chat:
            img_cam = Image.open(cam)
            res_c = model_chat.generate_content(["Describe esta imagen como JARVIS.", img_cam])
            st.success(res_c.text)
            hablar("Diagnóstico de cámara listo.")

# --- PESTAÑA 3: LABORATORIO CREATIVO ---
with tabs[3]:
    st.subheader("🎨 Estación de Diseño")
    diseno = st.text_input("Descripción del prototipo:")
    if st.button("🚀 SINTETIZAR"):
        url = f"https://image.pollinations.ai/prompt/{diseno.replace(' ', '%20')}?nologo=true"
        st.image(url)
        hablar("Imagen renderizada.")