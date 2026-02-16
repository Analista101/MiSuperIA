import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
import google.generativeai as genai
import edge_tts
import asyncio
import base64, io, datetime, requests
from streamlit_mic_recorder import mic_recorder

# --- 1. CONFIGURACIÓN ESTRUCTURAL ---
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
    .stChatMessage { background-color: rgba(26, 28, 35, 0.8); border: 1px solid #00f2ff; border-radius: 10px; }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- 2. NÚCLEO GEMINI Y VOCAL ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model_chat = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ Error Crítico: Falta la GOOGLE_API_KEY en los secretos.")

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

# --- 3. INICIALIZACIÓN DE INTERFAZ ---
if "mensajes" not in st.session_state: st.session_state.mensajes = []

st.markdown("<h1 style='text-align: center; color: #00f2ff;'>🛰️ JARVIS: SISTEMA INTEGRADO DIANA</h1>", unsafe_allow_html=True)

# DEFINICIÓN CRÍTICA DE PESTAÑAS (Esto evita el NameError)
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS UNIVERSAL", "📸 ÓPTICO", "🎨 LABORATORIO CREATIVO"])

# --- PESTAÑA 0: COMANDO ---
with tabs[0]:
    col_mic, col_txt = st.columns([1, 5])
    input_usuario = None
    with col_mic:
        audio_stark = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_v101")
    with col_txt:
        chat_input = st.chat_input("Diga sus órdenes, Srta. Diana...")

    if audio_stark:
        input_usuario = "Orden recibida por voz (Procesando...)"
    elif chat_input:
        input_usuario = chat_input

    if input_usuario:
        st.session_state.mensajes.append({"role": "user", "content": input_usuario})
        with st.chat_message("user"): st.markdown(input_usuario)
        
        contexto = "Eres JARVIS, el asistente de Tony Stark. Elegante, británico y llamas a la usuaria 'Srta. Diana'."
        response = model_chat.generate_content(f"{contexto} \n Usuario: {input_usuario}")
        res = response.text
        
        with st.chat_message("assistant"):
            st.markdown(res)
            hablar(res)
        st.session_state.mensajes.append({"role": "assistant", "content": res})

# --- PESTAÑA 1: ANÁLISIS UNIVERSAL ---
with tabs[1]:
    st.subheader("📊 Terminal de Inteligencia Mark 101")
    archivo = st.file_uploader("📁 Inyectar Archivo:", type=["png", "jpg", "jpeg", "docx"], key="up101")
    if archivo:
        if not archivo.name.endswith('.docx'):
            img_ana = Image.open(archivo)
            st.image(img_ana, width=350)
            st.session_state.temp_data = img_ana
        else:
            try:
                from docx import Document
                doc = Document(archivo)
                st.session_state.temp_data = "\n".join([p.text for p in doc.paragraphs])
            except: st.error("Librería docx no instalada.")

    if st.button("🔍 INICIAR ESCANEO", key="btn_ana"):
        if 'temp_data' in st.session_state:
            with st.spinner("Analizando..."):
                resp = model_chat.generate_content(["Actúa como JARVIS. Analiza esto detalladamente.", st.session_state.temp_data])
                st.info(resp.text)
                hablar("Escaneo finalizado.")

# --- PESTAÑA 2: ÓPTICO (RESTORED) ---
with tabs[2]:
    st.subheader("📸 Sensores Visuales")
    cam = st.camera_input("Activar Escáner", key="cam_v101")
    if cam:
        img_cam = Image.open(cam)
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            f_modo = st.selectbox("Cambiar Espectro:", ["Normal", "Grises", "Térmico", "Nocturno"], key="opt_filter")
            img_proc = img_cam.copy()
            if f_modo == "Grises": img_proc = ImageOps.grayscale(img_proc)
            elif f_modo == "Térmico": img_proc = ImageOps.colorize(ImageOps.grayscale(img_proc), "blue", "red")
            elif f_modo == "Nocturno": img_proc = ImageOps.colorize(ImageOps.grayscale(img_proc), "black", "green")
            st.image(img_proc, use_container_width=True)
        with col_v2:
            if st.button("🔍 ANÁLISIS TÁCTICO", key="btn_cam"):
                with st.spinner("Procesando imagen..."):
                    res_c = model_chat.generate_content(["Analiza esta captura de cámara como JARVIS.", img_cam])
                    st.success("Diagnóstico completado:")
                    st.write(res_c.text)
                    hablar("Diagnóstico de cámara completado.")

# --- PESTAÑA 3: LABORATORIO CREATIVO ---
with tabs[3]:
    st.subheader("🎨 Estación de Diseño Mark 61")
    estilo = st.selectbox("Estilo Visual:", ["Cinematic", "Cyberpunk", "Blueprint", "Anime", "Realistic"], key="style_v101")
    diseno = st.text_area("Descripción del prototipo:", key="text_v101")
    if st.button("🚀 INICIAR SÍNTESIS", key="btn_draw"):
        if diseno:
            url = f"https://image.pollinations.ai/prompt/{diseno.replace(' ', '%20')}%20{estilo}?nologo=true"
            st.image(url, caption="Prototipo sintetizado")
            hablar("Prototipo listo, Srta. Diana.")