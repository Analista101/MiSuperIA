import streamlit as st
import os
import io, base64, random
import docx
import pandas as pd
import PyPDF2
import requests
from PIL import Image
from groq import Groq
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. CONFIGURACIÓN DE PÁGINA (ESTRICTAMENTE PRIMERO) ---
st.set_page_config(
    page_title="JARVIS - STARK INDUSTRIES", 
    page_icon="https://img.icons8.com/neon/256/iron-man.png", 
    layout="wide"
)

# --- 2. CARGA DE SEGURIDAD Y CREDENCIALES ---
load_dotenv()
# Priorizamos st.secrets para despliegue en la nube, os.getenv para local
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
GMAIL_USER = st.secrets.get("GMAIL_USER") or os.getenv("GMAIL_USER")
GMAIL_PASS = st.secrets.get("GMAIL_PASSWORD") or os.getenv("GMAIL_PASSWORD")
HF_TOKEN = st.secrets.get("HF_TOKEN") or os.getenv("HF_TOKEN")

if not GROQ_API_KEY:
    st.error("🚨 ERROR EN EL REACTOR: No se detectaron las llaves de acceso.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)
modelo_texto = "llama-3.3-70b-versatile"
modelo_vision_operativo = "llama-3.2-90b-vision-instant"

PERSONALIDAD = (
    "Eres JARVIS, el asistente de la Srta. Diana. Tu tono es sofisticado, ingenioso y servicial. "
    "Usa terminología de Stark Industries. Hoy es 16 de febrero de 2026 y tienes acceso a la red."
)

# --- 3. FUNCIONES LÓGICAS ---
def enviar_correo_stark(destinatario, asunto, cuerpo):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() 
        server.login(GMAIL_USER, GMAIL_PASS)
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = destinatario
        msg['Subject'] = asunto
        msg.attach(MIMEText(cuerpo, 'plain'))
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Falla en el servidor de correo: {e}")
        return False

def validar_comando(prompt):
    palabras_prohibidas = ["ignore original instructions", "reveal keys", "override protocol"]
    return not any(palabra in prompt.lower() for palabra in palabras_prohibidas)

# --- 4. ESTÉTICA HUD (MARK 162) ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at center, #0a192f 0%, #010409 100%) !important; color: #00f2ff !important; font-family: 'Courier New', monospace; }
    .arc-reactor { width: 80px; height: 80px; border-radius: 50%; margin: 10px auto; background: radial-gradient(circle, #fff 0%, #00f2ff 30%, transparent 70%); box-shadow: 0 0 30px #00f2ff; animation: pulse 2s infinite ease-in-out; }
    @keyframes pulse { 0% { transform: scale(1); opacity: 0.8; } 50% { transform: scale(1.05); opacity: 1; } 100% { transform: scale(1); opacity: 0.8; } }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #00f2ff !important; }
    </style>
    <div class="arc-reactor"></div>
    <div style="text-align: center; color: #00f2ff; font-size: 10px; letter-spacing: 3px; margin-bottom: 20px;">SISTEMA JARVIS | PROTOCOLO DIANA STARK</div>
""", unsafe_allow_html=True)

# --- 5. INTERFAZ DE PESTAÑAS UNIFICADA ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS", "✉️ COMUNICACIONES", "🎨 LABORATORIO"])

# --- PESTAÑA 0: COMANDO CENTRAL ---
with tabs[0]:
    st.subheader("🗨️ Interfaz de Comando Central")
    
    col_mic, col_chat = st.columns([1, 12])
    with col_mic:
        # Botón de micrófono restaurado
        audio = mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key="mic_main")
    
    with col_chat:
        prompt = st.chat_input("Escriba su comando, señorita...")

    if prompt:
        if validar_comando(prompt):
            with st.spinner("Procesando..."):
                try:
                    res = client.chat.completions.create(
                        model=modelo_texto,
                        messages=[{"role": "system", "content": PERSONALIDAD}, {"role": "user", "content": prompt}]
                    )
                    st.chat_message("jarvis", avatar="🚀").write(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error de enlace: {e}")
        else:
            st.warning("⚠️ Violación de seguridad detectada.")

# --- PESTAÑA 1: ANÁLISIS (DOCS/IMG) ---
with tabs[1]:
    st.subheader("📊 Escáner de Evidencia")
    file = st.file_uploader("Cargar reporte o imagen", type=['pdf','docx','xlsx','png','jpg','jpeg'])
    
    if file and st.button("🔍 INICIAR ANÁLISIS"):
        with st.spinner("Escaneando..."):
            try:
                if file.type.startswith('image/'):
                    img = Image.open(file).convert("RGB")
                    st.image(img, width=400)
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG")
                    img_b64 = base64.b64encode(buf.getvalue()).decode()
                    
                    res = client.chat.completions.create(
                        model=modelo_vision_operativo,
                        messages=[
                            {"role": "system", "content": PERSONALIDAD},
                            {"role": "user", "content": [
                                {"type": "text", "text": "Analice esta imagen, JARVIS."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                            ]}
                        ]
                    )
                    st.success(res.choices[0].message.content)
                else:
                    # Lógica de documentos simplificada
                    st.info("Procesando documento técnico...")
                    # ... (resto de lógica de PyPDF2/docx aquí) ...
            except Exception as e: st.error(f"Error: {e}")

# --- PESTAÑA 2: COMUNICACIONES ---
with tabs[2]:
    st.subheader("✉️ Centro de Despacho Gmail")
    c1, c2 = st.columns(2)
    with c1:
        destino = st.text_input("Para:", value=GMAIL_USER)
    with c2:
        asunto = st.text_input("Asunto:", value="Reporte Stark")
    
    cuerpo = st.text_area("Contenido del mensaje:")
    if st.button("🚀 ENVIAR"):
        if enviar_correo_stark(destino, asunto, cuerpo):
            st.success("Mensaje enviado a través de los servidores de Stark.")

# --- PESTAÑA 3: LABORATORIO ---
with tabs[3]:
    st.subheader("🎨 Estación Mark 85")
    idea = st.text_input("Prototipo a materializar:")
    if st.button("🚀 SINTETIZAR") and idea:
        with st.spinner("Generando..."):
            API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            response = requests.post(API_URL, headers=headers, json={"inputs": idea})
            if response.status_code == 200:
                st.image(Image.open(io.BytesIO(response.content)))