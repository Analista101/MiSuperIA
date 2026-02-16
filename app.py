import streamlit as st  # <--- ESTO DEBE SER LA LÍNEA 1, SIN EXCEPCIÓN
import pandas as pd
from PIL import Image, ImageOps
import google.generativeai as genai
import edge_tts
import asyncio
import base64, io, datetime, requests
from streamlit_mic_recorder import mic_recorder

# --- 1. CONFIGURACIÓN DE PÁGINA (CHASIS) ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# --- 2. CONFIGURACIÓN DE SEGURIDAD (ESTRICTA) ---
# Verificamos si la llave existe para evitar el NameError
model_chat = None
if "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Usamos la ruta de modelo más compatible para evitar el error 'NotFound'
        model_chat = genai.GenerativeModel('models/gemini-1.5-flash')
    except Exception as e:
        st.error(f"Falla de inicialización: {e}")
else:
    st.warning("🛰️ Srta. Diana, falta la clave 'GOOGLE_API_KEY' en los Secrets de Streamlit.")

# --- 3. ESTÉTICA Y REACTORES ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #0a192f 0%, #020617 100%); color: #00f2ff; }
    .arc-reactor {
        width: 80px; height: 80px; border-radius: 50%; margin: 10px auto;
        background: radial-gradient(circle, #fff 0%, #00f2ff 40%, transparent 70%);
        box-shadow: 0 0 30px #00f2ff; border: 2px solid #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    .stTabs [data-baseweb="tab"] { color: #00f2ff !important; font-weight: bold; }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- 4. FUNCIONES DE APOYO ---
async def generar_voz(texto):
    try:
        comunicador = edge_tts.Communicate(texto, "en-GB-RyanNeural", rate="+0%", pitch="-5Hz")
        output = io.BytesIO()
        async for chunk in comunicador.stream():
            if chunk["type"] == "audio": output.write(chunk["data"])
        return base64.b64encode(output.getvalue()).decode()
    except: return None

def hablar(texto):
    b64 = asyncio.run(generar_voz(texto))
    if b64:
        st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)

# --- 5. INTERFAZ PRINCIPAL ---
st.markdown("<h1 style='text-align: center; color: #00f2ff;'>🛰️ JARVIS: SISTEMA INTEGRADO DIANA</h1>", unsafe_allow_html=True)

if "mensajes" not in st.session_state: st.session_state.mensajes = []

tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS UNIVERSAL", "📸 ÓPTICO", "🎨 LABORATORIO CREATIVO"])

# PESTAÑA 0: COMANDO
with tabs[0]:
    col_mic, col_txt = st.columns([1, 5])
    with col_mic: mic = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_v105")
    with col_txt: user_input = st.chat_input("Órdenes...")
    
    if user_input and model_chat:
        st.session_state.mensajes.append({"role": "user", "content": user_input})
        res = model_chat.generate_content(f"Eres JARVIS. Llama Srta. Diana a la usuaria. Responde corto: {user_input}").text
        st.chat_message("assistant").write(res)
        hablar(res)

# --- PROTOCOLO DE EMERGENCIA: SOLICITUD DIRECTA (BYPASS) ---
if st.button("🔍 ANÁLISIS TÁCTICO", key="btn_bypass"):
    if "GOOGLE_API_KEY" in st.secrets:
        with st.spinner("JARVIS forzando enlace satelital..."):
            try:
                # 1. Convertimos la imagen a Base64 para enviarla manualmente
                buffered = io.BytesIO()
                img_cam.save(buffered, format="JPEG")
                img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

                # 2. Construimos la petición manual (Sin usar la librería google-generativeai)
                api_key = st.secrets["GOOGLE_API_KEY"]
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": "Actúa como JARVIS. Describe esta imagen de forma elegante."},
                            {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
                        ]
                    }]
                }
                
                response = requests.post(url, json=payload)
                result = response.json()
                
                # 3. Extraemos la respuesta
                texto_res = result['candidates'][0]['content']['parts'][0]['text']
                st.success(texto_res)
                hablar("Enlace forzado con éxito. Análisis en pantalla.")
                
            except Exception as e:
                st.error("🛰️ Srta. Diana, incluso el bypass ha fallado.")
                st.write(f"Detalle técnico del servidor: {result if 'result' in locals() else e}")
    else:
        st.error("Falta llave de acceso.")

# PESTAÑA 2: ÓPTICO
with tabs[2]:
    cam = st.camera_input("Sensor Óptico", key="cam_v105")
    if cam and st.button("🔍 ANÁLISIS TÁCTICO"):
        if model_chat:
            with st.spinner("Procesando..."):
                img_cam = Image.open(cam)
                res = model_chat.generate_content(["Describe esta captura como JARVIS.", img_cam])
                st.success(res.text)
                hablar("Diagnóstico óptico listo.")

# PESTAÑA 3: LABORATORIO CREATIVO
with tabs[3]:
    prompt_img = st.text_input("Diseño de prototipo:")
    if st.button("🚀 SINTETIZAR"):
        url = f"https://image.pollinations.ai/prompt/{prompt_img.replace(' ', '%20')}?nologo=true"
        st.image(url)
        hablar("Imagen renderizada.")