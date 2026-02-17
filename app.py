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

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
load_dotenv()
st.set_page_config(
    page_title="JARVIS - STARK INDUSTRIES", 
    page_icon="https://img.icons8.com/neon/256/iron-man.png", 
    layout="wide"
)

# Variables de Entorno (Secrets o .env)
ACCESS_PASSWORD = st.secrets.get("ACCESS_PASSWORD") or os.getenv("ACCESS_PASSWORD", "STARK_RECOVERY_2026")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
GMAIL_USER = st.secrets.get("GMAIL_USER") or os.getenv("GMAIL_USER")
GMAIL_PASS = st.secrets.get("GMAIL_PASSWORD") or os.getenv("GMAIL_PASSWORD")
HF_TOKEN = st.secrets.get("HF_TOKEN") or os.getenv("HF_TOKEN")

# Zona Horaria y Personalidad
zona_horaria = pytz.timezone('America/Santiago')
ahora = datetime.datetime.now(zona_horaria)
fecha_actual = ahora.strftime("%d de febrero de 2026")
hora_actual = ahora.strftime("%H:%M")

PERSONALIDAD = (
    f"Eres JARVIS, el asistente de la Srta. Diana. Tu tono es sofisticado e ingenioso. "
    f"Usa terminología de Stark Industries. Ubicación: Santiago, Chile. "
    f"Fecha: {fecha_actual} | Hora: {hora_actual}."
)

# --- 2. PROTOCOLO DE AUTENTICACIÓN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

def pantalla_login():
    st.markdown('<div class="arc-reactor"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 ACCESO RESTRINGIDO")
        password_input = st.text_input("Código de Identificación:", type="password").strip()
        if st.button("DESBLOQUEAR"):
            if password_input == ACCESS_PASSWORD.strip():
                st.session_state["autenticado"] = True
                st.rerun()
            else: st.error("⚠️ CÓDIGO INCORRECTO.")

if not st.session_state["autenticado"]:
    pantalla_login()
    st.stop()

# --- 3. CONEXIÓN A BASE DE DATOS ---
def conectar_google_sheets():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds).open("JARVIS_MEMORY").sheet1
    except: return None

def guardar_memoria_permanente(usuario, jarvis):
    sheet = conectar_google_sheets()
    if sheet:
        sheet.append_row([datetime.datetime.now(zona_horaria).strftime("%Y-%m-%d %H:%M:%S"), usuario, jarvis])

# --- 4. CONFIGURACIÓN IA Y CORREO ---
client = Groq(api_key=GROQ_API_KEY)
modelo_texto = "llama-3.3-70b-versatile"
modelo_vision = "llama-3.2-90b-vision-instant"

def enviar_correo_stark(dest, asunto, cuerpo):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls(); server.login(GMAIL_USER, GMAIL_PASS)
        msg = MIMEMultipart(); msg['From'] = GMAIL_USER; msg['To'] = dest; msg['Subject'] = asunto
        msg.attach(MIMEText(cuerpo, 'plain'))
        server.send_message(msg); server.quit()
        return True
    except: return False

# --- 5. ESTÉTICA HUD ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at center, #0a192f 0%, #010409 100%) !important; color: #00f2ff !important; font-family: 'Courier New', monospace; }
    .arc-reactor { width: 80px; height: 80px; border-radius: 50%; margin: 10px auto; background: radial-gradient(circle, #fff 0%, #00f2ff 30%, transparent 70%); box-shadow: 0 0 30px #00f2ff; animation: pulse 2s infinite ease-in-out; }
    @keyframes pulse { 0% { transform: scale(1); opacity: 0.8; } 50% { transform: scale(1.05); opacity: 1; } 100% { transform: scale(1); opacity: 0.8; } }
    </style>
    <div class="arc-reactor"></div>
    <div style="text-align: center; color: #00f2ff; font-size: 10px; letter-spacing: 3px; margin-bottom: 20px;">SISTEMA JARVIS | PROTOCOLO DIANA STARK</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🛰️ Status Global")
    if conectar_google_sheets(): st.success("✅ Memoria: ESTABLE")
    else: st.error("❌ Memoria: OFFLINE")
    st.info(f"⌚ {hora_actual} Santiago")

# --- 6. PESTAÑAS ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS", "✉️ COMUNICACIONES", "🎨 LABORATORIO"])

# --- TAB 0: CHAT ---
with tabs[0]:
    if "historial_chat" not in st.session_state: st.session_state.historial_chat = []
    for m in st.session_state.historial_chat:
        with st.chat_message(m["role"], avatar="🚀" if m["role"]=="assistant" else "👤"): st.write(m["content"])

    col_mic, col_chat = st.columns([1, 12])
    with col_mic: audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key="mic_main")
    with col_chat: prompt = st.chat_input("Escriba su comando...")

    texto_final = None
    if audio_data and 'bytes' in audio_data:
        try:
            trans = client.audio.transcriptions.create(file=("a.wav", audio_data['bytes']), model="whisper-large-v3", language="es")
            texto_final = trans.text
        except: st.error("Error de audio.")
    elif prompt: texto_final = prompt

    if texto_final:
        st.session_state.historial_chat.append({"role": "user", "content": texto_final})
        with st.spinner("Procesando..."):
            ctx = [{"role": "system", "content": PERSONALIDAD}] + st.session_state.historial_chat[-6:]
            res = client.chat.get_completions(modelo_texto, ctx) if hasattr(client.chat, 'get_completions') else client.chat.completions.create(model=modelo_texto, messages=ctx)
            ans = res.choices[0].message.content
            st.session_state.historial_chat.append({"role": "assistant", "content": ans})
            guardar_memoria_permanente(texto_final, ans)
            st.rerun()

# --- TAB 1: ANÁLISIS (REPARADO PARA IMÁGENES) ---
with tabs[1]:
    st.subheader("📊 Escáner de Evidencia")
    file = st.file_uploader("Cargar archivo", type=['pdf','docx','png','jpg','jpeg'])
    if file and st.button("🔍 ANALIZAR"):
        with st.spinner("Analizando..."):
            try:
                if file.type.startswith('image/'):
                    img = Image.open(file).convert("RGB")
                    st.image(img, width=400)
                    buf = io.BytesIO(); img.save(buf, format="JPEG"); b64 = base64.b64encode(buf.getvalue()).decode()
                    res = client.chat.completions.create(model=modelo_vision, messages=[{"role":"user", "content":[{"type":"text","text":"Analiza esta imagen."},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}])
                    st.write(res.choices[0].message.content)
                elif file.type == "application/pdf":
                    pdf = PyPDF2.PdfReader(file); text = "".join([p.extract_text() for p in pdf.pages])
                    res = client.chat.completions.create(model=modelo_texto, messages=[{"role":"user", "content":f"Analiza: {text[:4000]}"}])
                    st.write(res.choices[0].message.content)
            except Exception as e: st.error(f"Falla: {e}")

# --- TAB 2: COMUNICACIONES (RESTAURADA) ---
with tabs[2]:
    st.subheader("✉️ Centro de Despacho Gmail")
    c1, c2 = st.columns(2)
    with c1: dest = st.text_input("Para:", value=GMAIL_USER)
    with c2: asun = st.text_input("Asunto:", value="Reporte Stark")
    cuer = st.text_area("Mensaje:")
    if st.button("🚀 ENVIAR CORREO"):
        if enviar_correo_stark(dest, asun, cuer): st.success("Mensaje enviado.")
        else: st.error("Falla en el servidor de correo.")

# --- TAB 3: LABORATORIO ---
with tabs[3]:
    st.subheader("🎨 Estación Mark 85")
    col_p, col_f = st.columns([2, 1])
    with col_p: idea = st.text_input("Prototipo:", key="lab_idea_m169")
    with col_f: 
        estilo = st.selectbox("Filtro:", ["Cinematic Marvel", "Technical Drawing", "Cyberpunk", "Industrial Stark"])
        intens = st.slider("Intensidad:", 0, 100, 75)
    if st.button("🚀 SINTETIZAR") and idea:
        with st.spinner("Sintetizando..."):
            url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
            resp = requests.post(url, headers={"Authorization": f"Bearer {HF_TOKEN}"}, json={"inputs": f"{idea}, {estilo} style"})
            if resp.status_code == 200: st.image(Image.open(io.BytesIO(resp.content)))
            else: st.error("Error en sintetizador.")