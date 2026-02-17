import streamlit as st
import os, io, base64, requests, datetime, pytz, smtplib
import pandas as pd
import PyPDF2
from PIL import Image
from groq import Groq
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

# --- 1. CONFIGURACIÓN HUD ---
load_dotenv()
st.set_page_config(page_title="JARVIS - STARK INDUSTRIES", page_icon="https://img.icons8.com/neon/256/iron-man.png", layout="wide")

# Credenciales
ACCESS_PASSWORD = st.secrets.get("ACCESS_PASSWORD") or os.getenv("ACCESS_PASSWORD", "STARK_RECOVERY_2026")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
GMAIL_USER = st.secrets.get("GMAIL_USER") or os.getenv("GMAIL_USER")
GMAIL_PASS = st.secrets.get("GMAIL_PASSWORD") or os.getenv("GMAIL_PASSWORD")
HF_TOKEN = st.secrets.get("HF_TOKEN") or os.getenv("HF_TOKEN")

zona_horaria = pytz.timezone('America/Santiago')
ahora = datetime.datetime.now(zona_horaria)
fecha_actual = ahora.strftime("%d de febrero de 2026")
hora_actual = ahora.strftime("%H:%M")

PERSONALIDAD = f"Eres JARVIS, el asistente de la Srta. Diana. Responde SIEMPRE EN ESPAÑOL. Tono sofisticado y técnico. Santiago, Chile. {fecha_actual}."

# --- 2. ESTILOS VISUALES STARK (REACTOR GRANDE Y NEÓN) ---
st.markdown("""
    <style>
    .stApp { background-color: #010409 !important; }
    .reactor-container { height: 260px; display: flex; justify-content: center; align-items: center; margin-top: -30px; }
    .reactor-core { 
        width: 130px; height: 130px; 
        background: radial-gradient(circle, #fff 5%, #00f2ff 45%, transparent 85%); 
        border-radius: 50%; box-shadow: 0 0 120px #00f2ff, inset 0 0 40px #00f2ff; 
        animation: pulse 2.5s infinite alternate ease-in-out; border: 2px solid rgba(0, 242, 255, 0.4);
    }
    @keyframes pulse { from { transform: scale(1); } to { transform: scale(1.1); } }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stChatInputContainer {
        background-color: rgba(0, 0, 0, 0.9) !important; color: #00f2ff !important;
        border: 1px solid #00f2ff !important; box-shadow: 0 0 15px rgba(0, 242, 255, 0.2) !important;
    }
    button, div.stButton > button, div.stDownloadButton > button { 
        background: rgba(0, 242, 255, 0.05) !important; color: #00f2ff !important; 
        border: 1px solid #00f2ff !important; text-transform: uppercase; letter-spacing: 2px;
    }
    </style>
    <div class="reactor-container"><div class="reactor-core"></div></div>
""", unsafe_allow_html=True)

# --- 3. AUTENTICACIÓN ---
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='color:#00f2ff; text-align:center;'>🔐 IDENTIFICACIÓN STARK</h3>", unsafe_allow_html=True)
        pass_in = st.text_input("", type="password", placeholder="Clave de acceso...")
        if st.button("DESBLOQUEAR"):
            if pass_in == ACCESS_PASSWORD: st.session_state["autenticado"] = True; st.rerun()
    st.stop()

# --- 4. MODELOS ---
client = Groq(api_key=GROQ_API_KEY)
MODELO_CHAT = "llama-3.3-70b-versatile"
MODELO_VISION_SCOUT = "meta-llama/llama-4-scout-17b-16e-instruct"

# --- 5. SIDEBAR (HUD) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2ff; text-align:center;'>🛡️ E.S.T.A.D.O.</h2>", unsafe_allow_html=True)
    st.info(f"📅 **FECHA**: {fecha_actual}\n⏰ **HORA**: {hora_actual}")
    st.divider()
    st.subheader("🌐 Escaneo Ambiental")
    st.write("🌦️ **Clima**: Santiago - 32°C")
    st.warning("⚠️ **SISMICIDAD**: Estable. Perímetro bajo vigilancia.")
    st.error("🔥 **INCENDIOS ACTIVOS:**\n1. V Región\n2. Melipilla\n3. Curacaví")
    if st.button("🔄 REINICIAR SISTEMAS"): st.session_state.historial_chat = []; st.rerun()

# --- 6. PESTAÑAS ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS PROFUNDO", "✉️ DESPACHO", "🎨 LABORATORIO"])

# TAB 0: COMANDO CENTRAL (MANOS LIBRES)
with tabs[0]:
    if "historial_chat" not in st.session_state: st.session_state.historial_chat = []
    st.session_state.modo_fluido = st.toggle("🎙️ MODO MANOS LIBRES", value=st.session_state.get('modo_fluido', False))
    
    for m in st.session_state.historial_chat:
        with st.chat_message(m["role"], avatar="🚀" if m["role"] == "assistant" else "👤"):
            st.markdown(m["content"])
            if "youtube" in m["content"]: st.video(m["content"].split()[-1])

    col_mic, col_chat = st.columns([1, 10])
    with col_mic: audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key="jarvis_mic")
    with col_chat: prompt = st.chat_input("Órdenes...")

    text_in = None
    if audio_data and 'bytes' in audio_data:
        text_in = client.audio.transcriptions.create(file=("v.wav", audio_data['bytes']), model="whisper-large-v3").text
    elif prompt: text_in = prompt

    if text_in:
        st.session_state.historial_chat.append({"role": "user", "content": text_in})
        res = client.chat.completions.create(model=MODELO_CHAT, messages=[{"role": "system", "content": PERSONALIDAD}] + st.session_state.historial_chat[-5:])
        ans = res.choices[0].message.content
        st.session_state.historial_chat.append({"role": "assistant", "content": ans})
        st.rerun()

# TAB 1: ANÁLISIS PROFUNDO (SCOUT + PDF EXHAUSTIVO)
with tabs[1]:
    st.subheader("📊 Módulo Scout - Análisis Exhaustivo")
    f = st.file_uploader("Evidencia técnica", type=['pdf','png','jpg','xlsx'])
    if f and st.button("🔍 INICIAR ESCANEO"):
        with st.spinner("Analizando detalladamente..."):
            try:
                if f.type in ["image/png", "image/jpeg"]:
                    img = Image.open(f).convert("RGB"); buf = io.BytesIO(); img.save(buf, format="JPEG")
                    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                    # Prompt forzado para profundidad y español
                    res = client.chat.completions.create(model=MODELO_VISION_SCOUT, messages=[{"role": "user", "content": [{"type": "text", "text": "Responde en ESPAÑOL. Realiza un análisis técnico, exhaustivo y profundo. Detalla cada objeto, texto y anomalía detectada."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}])
                    out = res.choices[0].message.content
                elif f.name.endswith('.pdf'):
                    reader = PyPDF2.PdfReader(f); texto = "".join([p.extract_text() for p in reader.pages[:10]])
                    res = client.chat.completions.create(model=MODELO_CHAT, messages=[{"role": "user", "content": f"Analiza este documento profundamente y en ESPAÑOL:\n{texto}"}])
                    out = res.choices[0].message.content
                else: out = "Análisis completado."
                
                st.markdown(out)
                
                # Función PDF integrada
                buf_pdf = io.BytesIO(); c = canvas.Canvas(buf_pdf, pagesize=letter)
                c.drawString(100, 750, f"REPORTE SCOUT - {fecha_actual}"); c.save(); buf_pdf.seek(0)
                st.download_button("📥 DESCARGAR REPORTE", buf_pdf, "Reporte_Stark.pdf")
            except Exception as e: st.error(f"Error en Scout: {e}")

# TAB 3: LABORATORIO (FLUX.1 RESTAURADO - FIX 410)
with tabs[3]:
    st.subheader("🎨 Forja Mark 85")
    idea = st.text_input("Concepto Visual:")
    estilo = st.selectbox("Filtro Stark:", ["Cinematic Marvel", "Digital Blueprint", "Cyberpunk", "Photorealistic", "Blueprint Tech"])
    if st.button("🔥 GENERAR PROTOTIPO") and idea:
        with st.spinner("Sintetizando..."):
            try:
                # Cambio a modelo FLUX para evitar el error 410
                API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                payload = {"inputs": f"Stark Industries tech, {idea}, {estilo}, neon blue, hyper-detailed"}
                r = requests.post(API_URL, headers=headers, json=payload)
                if r.status_code == 200:
                    st.image(Image.open(io.BytesIO(r.content)))
                else:
                    st.error(f"Error en la forja: {r.status_code}. Reintente en un momento.")
            except Exception as e: st.error(f"Fallo de conexión: {e}")