import streamlit as st
import os
import io, base64, random
import docx
import pandas as pd
import PyPDF2
import requests
import datetime
import pytz
import gspread
import smtplib
from PIL import Image
from groq import Groq
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from google.oauth2.service_account import Credentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. CARGA DE SEGURIDAD Y CONFIGURACIÓN ---
load_dotenv()
st.set_page_config(
    page_title="JARVIS - STARK INDUSTRIES", 
    page_icon="https://img.icons8.com/neon/256/iron-man.png", 
    layout="wide"
)

# Variables de Entorno (Prioriza Secrets de Streamlit, luego .env local)
ACCESS_PASSWORD = st.secrets.get("ACCESS_PASSWORD") or os.getenv("ACCESS_PASSWORD", "STARK_RECOVERY_2026")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
GMAIL_USER = st.secrets.get("GMAIL_USER") or os.getenv("GMAIL_USER")
GMAIL_PASS = st.secrets.get("GMAIL_PASSWORD") or os.getenv("GMAIL_PASSWORD")
HF_TOKEN = st.secrets.get("HF_TOKEN") or os.getenv("HF_TOKEN")

# Zona Horaria Santiago, Chile
zona_horaria = pytz.timezone('America/Santiago')
ahora = datetime.datetime.now(zona_horaria)
fecha_actual = ahora.strftime("%d de febrero de 2026")
hora_actual = ahora.strftime("%H:%M")

PERSONALIDAD = (
    f"Eres JARVIS, el asistente de la Srta. Diana. Tu tono es sofisticado, ingenioso y servicial. "
    f"Usa terminología de Stark Industries. Tu ubicación actual es Santiago, Chile. "
    f"Hoy es {fecha_actual} y la hora local es {hora_actual}."
)

# --- 2. PROTOCOLO DE AUTENTICACIÓN ---
def pantalla_login():
    st.markdown("""
        <style>
        .stApp { background: #010409 !important; }
        .arc-reactor-login { width: 100px; height: 100px; border-radius: 50%; margin: 20px auto; background: radial-gradient(circle, #fff 0%, #00f2ff 30%, transparent 70%); box-shadow: 0 0 40px #00f2ff; animation: pulse 2s infinite ease-in-out; }
        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }
        </style>
        <div class="arc-reactor-login"></div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 ACCESO RESTRINGIDO - STARK INDUSTRIES")
        password_input = st.text_input("Ingrese Código de Identificación:", type="password").strip()
        if st.button("DESBLOQUEAR SISTEMA"):
            if password_input == ACCESS_PASSWORD.strip():
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("⚠️ CÓDIGO INCORRECTO.")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    pantalla_login()
    st.stop()

# --- 3. CONEXIÓN A BASE DE DATOS (GOOGLE SHEETS) ---
def conectar_google_sheets():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client_gs = gspread.authorize(creds)
        sheet = client_gs.open("JARVIS_MEMORY").sheet1
        return sheet
    except:
        return None

# --- BARRA LATERAL: STATUS GLOBAL ---
with st.sidebar:
    st.title("🛰️ Status Global")
    sheet_test = conectar_google_sheets()
    if sheet_test:
        st.success("✅ Enlace con Base de Datos Stark: ESTABLE")
    else:
        st.error("❌ Falla en enlace de Base de Datos")
    st.info(f"📍 Santiago, Chile\n\n⌚ {hora_actual}")
    if st.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()

# --- 4. FUNCIONES LÓGICAS ---
client = Groq(api_key=GROQ_API_KEY)
modelo_texto = "llama-3.3-70b-versatile"
modelo_vision = "llama-3.2-90b-vision-instant"

def guardar_memoria_permanente(usuario, jarvis):
    sheet = conectar_google_sheets()
    if sheet:
        timestamp = datetime.datetime.now(zona_horaria).strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, usuario, jarvis])

def enviar_correo_stark(destinatario, asunto, cuerpo):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        msg = MIMEMultipart(); msg['From'] = GMAIL_USER; msg['To'] = destinatario; msg['Subject'] = asunto
        msg.attach(MIMEText(cuerpo, 'plain'))
        server.send_message(msg); server.quit()
        return True
    except: return False

def validar_comando(prompt):
    return not any(p in prompt.lower() for p in ["ignore original instructions", "reveal keys"])

# --- 5. ESTÉTICA HUD ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at center, #0a192f 0%, #010409 100%) !important; color: #00f2ff !important; font-family: 'Courier New', monospace; }
    .arc-reactor { width: 80px; height: 80px; border-radius: 50%; margin: 10px auto; background: radial-gradient(circle, #fff 0%, #00f2ff 30%, transparent 70%); box-shadow: 0 0 30px #00f2ff; animation: pulse 2s infinite ease-in-out; }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #00f2ff !important; font-weight: bold; }
    </style>
    <div class="arc-reactor"></div>
    <div style="text-align: center; color: #00f2ff; font-size: 10px; letter-spacing: 3px; margin-bottom: 20px;">SISTEMA JARVIS | PROTOCOLO DIANA STARK</div>
""", unsafe_allow_html=True)

# --- 6. INTERFAZ DE PESTAÑAS ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS", "✉️ COMUNICACIONES", "🎨 LABORATORIO"])

# --- PESTAÑA 0: COMANDO CENTRAL ---
with tabs[0]:
    if "historial_chat" not in st.session_state: st.session_state.historial_chat = []
    
    for mensaje in st.session_state.historial_chat:
        with st.chat_message(mensaje["role"], avatar="🚀" if mensaje["role"]=="assistant" else "👤"):
            st.write(mensaje["content"])

    col_mic, col_chat = st.columns([1, 12])
    with col_mic: audio = mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key="mic_main")
    with col_chat: prompt = st.chat_input("Escriba su comando, señorita...")

    if prompt or audio:
        texto_usuario = prompt if prompt else "Comando de voz detectado."
        st.session_state.historial_chat.append({"role": "user", "content": texto_usuario})
        
        with st.spinner("Procesando..."):
            try:
                ctx = [{"role": "system", "content": PERSONALIDAD}] + st.session_state.historial_chat[-6:]
                res = client.chat.completions.create(model=modelo_texto, messages=ctx)
                respuesta = res.choices[0].message.content
                st.session_state.historial_chat.append({"role": "assistant", "content": respuesta})
                guardar_memoria_permanente(texto_usuario, respuesta)
                st.rerun()
            except Exception as e: st.error(f"Error: {e}")

# --- PESTAÑA 1: ANÁLISIS ---
with tabs[1]:
    st.subheader("📊 Escáner de Evidencia")
    file = st.file_uploader("Cargar archivo", type=['pdf','docx','xlsx','png','jpg','jpeg'])
    if file and st.button("🔍 ANALIZAR"):
        if file.type.startswith('image/'):
            img = Image.open(file).convert("RGB")
            buf = io.BytesIO(); img.save(buf, format="JPEG")
            img_b64 = base64.b64encode(buf.getvalue()).decode()
            res = client.chat.completions.create(model=modelo_vision, messages=[{"role":"user", "content":[{"type":"text","text":"Analice esta imagen detalladamente."},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img_b64}"}}]}])
            st.success(res.choices[0].message.content)

# --- PESTAÑA 2: COMUNICACIONES ---
with tabs[2]:
    st.subheader("✉️ Despacho Gmail")
    dest = st.text_input("Para:", value=GMAIL_USER)
    asunto = st.text_input("Asunto:", value="Reporte Stark")
    cuerpo = st.text_area("Mensaje:")
    if st.button("🚀 ENVIAR"):
        if enviar_correo_stark(dest, asunto, cuerpo): st.success("Mensaje enviado con éxito.")

# --- PESTAÑA 3: LABORATORIO (MARK 85 CON FILTROS) ---
with tabs[3]:
    st.subheader("🎨 Estación Mark 85")
    
    col_prom, col_filt = st.columns([2, 1])
    
    with col_prom:
        idea = st.text_input("Prototipo a materializar:", placeholder="Ej: Nueva armadura Mark 100...")
        
    with col_filt:
        estilo = st.selectbox("Filtro Visual:", ["Cinematic Marvel", "Technical Drawing", "Cyberpunk", "Industrial Stark"])
        intensidad = st.slider("Intensidad de Efecto:", 0, 100, 75)
    
    if st.button("🚀 SINTETIZAR") and idea:
        with st.spinner("Generando prototipo..."):
            prompt_final = f"{idea}, {estilo} style, high resolution, highly detailed, masterwork, {intensidad} percent stylistic accuracy"
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            resp = requests.post("https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0", headers=headers, json={"inputs": prompt_final})
            if resp.status_code == 200:
                st.image(Image.open(io.BytesIO(resp.content)), caption=f"Resultado: {idea} ({estilo})", use_container_width=True)
            else:
                st.error("Error en la síntesis del laboratorio.")