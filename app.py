import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
import google.generativeai as genai  # MIGRADO: Adios Groq
from duckduckgo_search import DDGS
import edge_tts
import asyncio
import base64, io, datetime, requests
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURACIÓN DE LA TERMINAL STARK ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# Estética Stark (Reactor Arc y Colores)
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

# --- CONFIGURACIÓN DE NÚCLEO GEMINI ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model_chat = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ CRÍTICO: Falta la GOOGLE_API_KEY en los secretos.")

# --- MOTOR VOCAL (BRITÁNICO) ---
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

# --- INICIALIZACIÓN ---
if "mensajes" not in st.session_state: st.session_state.mensajes = []

st.markdown("<h1 style='text-align: center; color: #00f2ff;'>🛰️ JARVIS: SISTEMA INTEGRADO DIANA</h1>", unsafe_allow_html=True)
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS UNIVERSAL", "📸 ÓPTICO", "🎨 LABORATORIO CREATIVO"])

# --- 1. PESTAÑA: COMANDO (MIGRADA A GEMINI) ---
with tabs[0]:
    chat_input = st.chat_input("Diga sus órdenes, Srta. Diana...")
    
    # Historial de Chat
    for msj in st.session_state.mensajes:
        with st.chat_message(msj["role"]): st.markdown(msj["content"])

    if chat_input:
        st.session_state.mensajes.append({"role": "user", "content": chat_input})
        with st.chat_message("user"): st.markdown(chat_input)
        
        try:
            # Contexto de JARVIS para Gemini
            contexto = "Eres JARVIS, el asistente de inteligencia artificial de Tony Stark. Eres elegante, británico, servicial y llamas a la usuaria 'Srta. Diana'."
            response = model_chat.generate_content(f"{contexto} \n Usuario: {chat_input}")
            res = response.text
            
            with st.chat_message("assistant"):
                st.markdown(res)
                hablar(res)
            st.session_state.mensajes.append({"role": "assistant", "content": res})
        except Exception as e:
            st.error(f"Falla en el enlace neural: {e}")

# --- 2. PESTAÑA: ANÁLISIS UNIVERSAL (MARK 98 - TOTAL GEMINI) ---
with tabs[1]:
    st.subheader("📊 Terminal de Inteligencia Mark 98")
    try:
        from docx import Document
    except: pass

    archivo = st.file_uploader("📁 Inyectar Imagen o Documento:", type=["png", "jpg", "jpeg", "docx"], key="up98")

    if archivo:
        if archivo.name.endswith('.docx'):
            doc = Document(archivo)
            content = "\n".join([p.text for p in doc.paragraphs])
            st.session_state.datos_stark = content
            st.session_state.tipo_stark = "TEXTO"
            st.success("✔️ Documento Word analizado.")
        else:
            img = Image.open(archivo)
            st.session_state.datos_stark = img
            st.session_state.tipo_stark = "IMAGEN"
            st.image(img, caption="Señal visual confirmada", width=350)

    st.write("---")
    if st.button("🔍 EJECUTAR ANÁLISIS DE JARVIS", type="primary", use_container_width=True):
        if 'datos_stark' in st.session_state:
            with st.spinner("JARVIS procesando datos..."):
                try:
                    prompt_analisis = "Actúa como JARVIS. Identifica esta imagen o analiza este texto. Si es una planta, di nombre común, científico y cuidados. Sé extenso y elegante."
                    # Gemini maneja ambos tipos de datos
                    response = model_chat.generate_content([prompt_analisis, st.session_state.datos_stark])
                    st.markdown("### 📝 Informe Stark")
                    st.info(response.text)
                    hablar("Análisis finalizado, Srta. Diana.")
                except Exception as e:
                    st.error(f"Falla en el escaneo: {e}")
        else:
            st.warning("⚠️ Sin datos en los sensores.")

# --- 3. PESTAÑA: ÓPTICO (FILTROS) ---
with tabs[2]:
    st.subheader("📸 Sensores Visuales")
    cam = st.camera_input("Activar Escáner")
    if cam:
        img_cam = Image.open(cam)
        f_modo = st.selectbox("Filtro de Espectro:", ["Normal", "Grises", "Térmico", "Nocturno"])
        if f_modo == "Grises": img_cam = ImageOps.grayscale(img_cam)
        elif f_modo == "Térmico": img_cam = ImageOps.colorize(ImageOps.grayscale(img_cam), "blue", "red")
        elif f_modo == "Nocturno": img_cam = ImageOps.colorize(ImageOps.grayscale(img_cam), "black", "green")
        st.image(img_cam, use_container_width=True)

# --- 4. PESTAÑA: LABORATORIO CREATIVO (MARK 61) ---
with tabs[3]:
    st.subheader("🎨 Estación de Diseño Mark 61")
    diseno = st.text_area("Descripción del prototipo:")
    if st.button("🚀 INICIAR SÍNTESIS"):
        if diseno:
            url_final = f"https://image.pollinations.ai/prompt/{diseno.replace(' ', '%20')}?width=1024&height=1024&nologo=true"
            st.image(url_final, caption="Sintetizando imagen...")
            hablar("Prototipo renderizado, Srta. Diana.")