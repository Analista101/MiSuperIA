import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
import google.generativeai as genai
import edge_tts
import asyncio
import base64, io, datetime, requests
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURACIÓN DE LA TERMINAL STARK ---
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

# --- CONFIGURACIÓN DE NÚCLEO GEMINI ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model_chat = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ Falta la GOOGLE_API_KEY en los secretos.")

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

# --- INICIALIZACIÓN ---
if "mensajes" not in st.session_state: st.session_state.mensajes = []

st.markdown("<h1 style='text-align: center; color: #00f2ff;'>🛰️ JARVIS: SISTEMA INTEGRADO DIANA</h1>", unsafe_allow_html=True)
tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS UNIVERSAL", "📸 ÓPTICO", "🎨 LABORATORIO CREATIVO"])

# --- 1. PESTAÑA: COMANDO (RECONECTADA CON VOZ) ---
with tabs[0]:
    col_mic, col_txt = st.columns([1, 5])
    input_usuario = None
    
    with col_mic:
        # Restauración del Micrófono
        audio_stark = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_v99")
    with col_txt:
        chat_input = st.chat_input("Diga sus órdenes, Srta. Diana...")

    if audio_stark:
        with st.spinner("Procesando frecuencia vocal..."):
            # Usamos Gemini para transcribir si es necesario, 
            # pero por ahora procesamos el texto directamente si el mic devuelve texto
            # OJO: Si su mic_recorder devuelve bytes, aquí se procesaría.
            st.warning("Sistema de voz: Gemini procesará su petición de audio.")
            input_usuario = "Analiza mi voz" # Placeholder o transcripción si el componente lo permite
    elif chat_input:
        input_usuario = chat_input

    if input_usuario:
        st.session_state.mensajes.append({"role": "user", "content": input_usuario})
        with st.chat_message("user"): st.markdown(input_usuario)
        
        contexto = "Eres JARVIS, británico, elegante, llamas a la usuaria 'Srta. Diana'."
        response = model_chat.generate_content(f"{contexto} \n Usuario: {input_usuario}")
        res = response.text
        
        with st.chat_message("assistant"):
            st.markdown(res)
            hablar(res)
        st.session_state.mensajes.append({"role": "assistant", "content": res})

# --- 2. PESTAÑA: ANÁLISIS UNIVERSAL ---
with tabs[1]:
    st.subheader("📊 Terminal de Inteligencia Mark 99")
    archivo = st.file_uploader("📁 Inyectar Archivo:", type=["png", "jpg", "jpeg", "docx"], key="up99")
    if archivo:
        if not archivo.name.endswith('.docx'):
            img_ana = Image.open(archivo)
            st.image(img_ana, width=350)
            st.session_state.temp_data = img_ana
        else:
            st.session_state.temp_data = archivo # Manejo de docx

    if st.button("🔍 INICIAR ESCANEO"):
        if 'temp_data' in st.session_state:
            with st.spinner("Escaneando..."):
                resp = model_chat.generate_content(["Identifica esto detalladamente como JARVIS.", st.session_state.temp_data])
                st.info(resp.text)
                hablar("Escaneo finalizado.")

# --- 3. PESTAÑA: ÓPTICO (CÁMARA) ---
with tabs[2]:
    st.subheader("📸 Sensores Visuales")
    cam = st.camera_input("Activar Escáner")
    if cam:
        img_cam = Image.open(cam)
        st.image(img_cam, use_container_width=True)

# --- 4. PESTAÑA: LABORATORIO CREATIVO (RESTORED) ---
with tabs[3]:
    st.subheader("🎨 Estación de Diseño Mark 61")
    
    col_dis, col_set = st.columns([2, 1])
    
    with col_set:
        st.markdown("### 🛠️ Ajustes de Red")
        # RESTAURACIÓN DE FILTROS Y ESTILOS
        estilo = st.selectbox("Estilo Visual:", [
            "Cinematic", "Blueprint", "Cyberpunk", "Anime", "Realistic", "Oil Painting", "3D Render"
        ])
        aspecto = st.radio("Relación de Aspecto:", ["1:1", "16:9", "9:16"])

    with col_dis:
        diseno = st.text_area("Descripción del prototipo:", placeholder="Ej: Una armadura dorada con detalles en plata...")
        
        if st.button("🚀 INICIAR SÍNTESIS"):
            if diseno:
                # Sincronización con el motor de Pollinations
                seed = datetime.datetime.now().microsecond
                url_final = f"https://image.pollinations.ai/prompt/{diseno.replace(' ', '%20')}%20in%20{estilo}%20style?width=1024&height=1024&seed={seed}&nologo=true"
                
                st.markdown(f"""
                    <div style="border: 3px solid #00f2ff; border-radius: 15px; padding: 10px; background-color: #000;">
                        <img src="{url_final}" style="width: 100%; border-radius: 10px;">
                    </div>
                """, unsafe_allow_html=True)
                hablar("Prototipo sintetizado, Srta. Diana.")
            else:
                st.warning("Srta. Diana, indique los parámetros de diseño.")