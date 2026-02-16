import streamlit as st
import pandas as pd
from PIL import Image, ImageOps
import google.generativeai as genai
import edge_tts
import asyncio
import base64, io, datetime, requests
from streamlit_mic_recorder import mic_recorder

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# --- 2. ESTÉTICA STARK (RESTAURADA) ---
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

# --- 3. NÚCLEO GEMINI ---
model_chat = None
if "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Usamos flash-latest que es el más versátil
        model_chat = genai.GenerativeModel('gemini-1.5-flash-latest')
    except Exception as e:
        st.error(f"Falla en el Reactor Central: {e}")
else:
    st.warning("🛰️ Srta. Diana, la terminal requiere la GOOGLE_API_KEY en los Secrets.")

# --- 4. MOTOR VOCAL ---
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

# --- 5. INTERFAZ DE COMANDO ---
st.markdown("<h1 style='text-align: center; color: #00f2ff;'>🛰️ JARVIS: SISTEMA INTEGRADO DIANA</h1>", unsafe_allow_html=True)

if "mensajes" not in st.session_state: st.session_state.mensajes = []

tabs = st.tabs(["💬 COMANDO", "📊 ANÁLISIS UNIVERSAL", "📸 ÓPTICO", "🎨 LABORATORIO CREATIVO"])

# --- PESTAÑA 0: CHAT ---
with tabs[0]:
    col_mic, col_txt = st.columns([1, 5])
    with col_mic: 
        audio_stark = mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_final")
    with col_txt: 
        chat_input = st.chat_input("Diga sus órdenes, Srta. Diana...")

    if chat_input and model_chat:
        st.session_state.mensajes.append({"role": "user", "content": chat_input})
        with st.chat_message("user"): st.markdown(chat_input)
        
        response = model_chat.generate_content(f"Eres JARVIS, el asistente de Tony Stark. Elegante, británico. Llama Srta. Diana a la usuaria. Responde a: {chat_input}")
        res = response.text
        with st.chat_message("assistant"):
            st.markdown(res)
            hablar(res)
        st.session_state.mensajes.append({"role": "assistant", "content": res})

# --- PESTAÑA 1: ANÁLISIS UNIVERSAL ---
with tabs[1]:
    st.subheader("📊 Análisis de Inteligencia")
    archivo = st.file_uploader("Inyectar datos:", type=["png", "jpg", "jpeg", "docx"], key="up_final")
    if archivo and st.button("🔍 ESCANEAR"):
        if model_chat:
            with st.spinner("Procesando..."):
                img = Image.open(archivo) if not archivo.name.endswith('.docx') else archivo
                resp = model_chat.generate_content(["Actúa como JARVIS y analiza esto detalladamente.", img])
                st.info(resp.text)
                hablar("Análisis completado.")

# --- 2. CONFIGURACIÓN DEL NÚCLEO (CALIBRACIÓN FORZADA MARK 111) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Forzamos el nombre base que NO debería dar error 404
    try:
        model_chat = genai.GenerativeModel('gemini-1.5-flash')
    except:
        model_chat = genai.GenerativeModel('gemini-1.5-pro')
else:
    st.error("🚨 SRTA. DIANA: NO HAY LLAVE MAESTRA EN SECRETS.")

# --- PESTAÑA 2: ÓPTICO (RESTABLECIDO CON BYPASS DIRECTO) ---
with tabs[2]:
    st.subheader("📸 Sensores de Campo y Reconocimiento Táctico")
    
    # 1. Entrada de la cámara
    cam = st.camera_input("Activar Lente Óptico", key="cam_v112")
    
    if cam:
        # Previsualización Stark
        img_cam = Image.open(cam)
        st.image(img_cam, width=450, caption="Captura de los sensores frontales")
        
        # 2. El botón de análisis que usted solicitó
        if st.button("🔍 INICIAR ANÁLISIS TÁCTICO", key="btn_v112"):
            if "GOOGLE_API_KEY" in st.secrets:
                with st.spinner("JARVIS estableciendo conexión segura (Bypass Mode)..."):
                    try:
                        # --- MANIOBRA DE BYPASS (MÉTODO 3) ---
                        api_key = st.secrets["GOOGLE_API_KEY"]
                        # Forzamos la URL a la versión estable 'v1' para evitar el error 404 de la beta
                     # --- MANIOBRA DE EMERGENCIA: CAMBIO DE FRECUENCIA A MODELO LEGACY ---
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={api_key}"
                        
                        # Convertimos la imagen a bytes y luego a Base64
                        buf = io.BytesIO()
                        img_cam.save(buf, format="JPEG")
                        img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

                        # Construimos el paquete de datos manualmente
                        payload = {
                            "contents": [{
                                "parts": [
                                    {"text": "Actúa como JARVIS. Analiza esta imagen de forma técnica y elegante para la Srta. Diana."},
                                    {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
                                ]
                            }]
                        }
                        
                        # Enviamos la señal
                        response = requests.post(url, json=payload)
                        resultado = response.json()

                        # Extraemos la respuesta de la red
                        if 'candidates' in resultado:
                            texto_analisis = resultado['candidates'][0]['content']['parts'][0]['text']
                            st.success("✅ Diagnóstico Completado")
                            st.markdown(f"**JARVIS informa:** {texto_analisis}")
                            hablar(texto_analisis)
                        else:
                            st.error("🛰️ Error en la respuesta del satélite.")
                            st.json(resultado) # Para que veamos qué dice el servidor exactamente
                            
                    except Exception as e:
                        st.error(f"Falla crítica en el enlace manual: {e}")
            else:
                st.error("⚠️ No se detecta la llave de acceso en los sistemas.")

# --- PESTAÑA 3: LABORATORIO CREATIVO ---
with tabs[3]:
    st.subheader("🎨 Estación de Diseño Mark 61")
    diseno = st.text_input("Descripción del prototipo:")
    estilo = st.selectbox("Estilo:", ["Cinematic", "Cyberpunk", "Blueprint"])
    if st.button("🚀 SINTETIZAR"):
        if diseno:
            url = f"https://image.pollinations.ai/prompt/{diseno.replace(' ', '%20')}%20{estilo}?nologo=true"
            st.image(url, caption="Prototipo finalizado")
            hablar("Prototipo renderizado, Srta. Diana.")