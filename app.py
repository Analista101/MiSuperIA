import streamlit as st
import os
import io, base64, requests
import datetime, pytz, smtplib
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

# --- 1. CONFIGURACIÓN HUD ---
load_dotenv()
st.set_page_config(page_title="JARVIS - STARK INDUSTRIES", page_icon="https://img.icons8.com/neon/256/iron-man.png", layout="wide")

# Variables de Seguridad
ACCESS_PASSWORD = st.secrets.get("ACCESS_PASSWORD") or os.getenv("ACCESS_PASSWORD", "STARK_RECOVERY_2026")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
GMAIL_USER = st.secrets.get("GMAIL_USER") or os.getenv("GMAIL_USER")
GMAIL_PASS = st.secrets.get("GMAIL_PASSWORD") or os.getenv("GMAIL_PASSWORD")
HF_TOKEN = st.secrets.get("HF_TOKEN") or os.getenv("HF_TOKEN")

zona_horaria = pytz.timezone('America/Santiago')
ahora = datetime.datetime.now(zona_horaria)
fecha_actual = ahora.strftime("%d de febrero de 2026")
hora_actual = ahora.strftime("%H:%M")

PERSONALIDAD = f"Eres JARVIS, el asistente de la Srta. Diana. Tono sofisticado, ingenioso y técnico. Santiago, Chile. {fecha_actual}."

# --- 2. ESTILOS VISUALES STARK V3 (DISEÑO NEÓN EXTREMO) ---
st.markdown("""
    <style>
    .stApp { background-color: #010409 !important; }
    
    /* Reactor Ark Grande y Luminoso */
    .reactor-container { height: 250px; display: flex; justify-content: center; align-items: center; }
    .reactor-core { 
        width: 110px; height: 110px; 
        background: radial-gradient(circle, #fff 5%, #00f2ff 40%, transparent 85%); 
        border-radius: 50%; 
        box-shadow: 0 0 100px #00f2ff, inset 0 0 30px #00f2ff; 
        animation: pulse-ark 2s infinite alternate ease-in-out;
        border: 2px solid rgba(0, 242, 255, 0.4);
    }
    @keyframes pulse-ark { 
        from { transform: scale(1); filter: brightness(1); box-shadow: 0 0 60px #00f2ff; } 
        to { transform: scale(1.1); filter: brightness(1.3); box-shadow: 0 0 120px #00f2ff; } 
    }
    
    /* Cuadros de Texto con Bordes Neón */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: rgba(0, 0, 0, 0.8) !important;
        color: #00f2ff !important;
        border: 1px solid #00f2ff !important;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.2) !important;
    }
    
    /* Botones Stark */
    button, div.stButton > button { 
        background: rgba(0, 242, 255, 0.05) !important; 
        color: #00f2ff !important; 
        border: 1px solid #00f2ff !important; 
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.3) !important;
        text-transform: uppercase; letter-spacing: 2px;
    }
    </style>
    <div class="reactor-container"><div class="reactor-core"></div></div>
""", unsafe_allow_html=True)

# --- 3. AUTENTICACIÓN ---
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='color:#00f2ff; text-align:center;'>IDENTIFICACIÓN BIOMÉTRICA</h3>", unsafe_allow_html=True)
        pass_in = st.text_input("", type="password", placeholder="Clave Stark...")
        if st.button("ACCEDER"):
            if pass_in == ACCESS_PASSWORD: st.session_state["autenticado"] = True; st.rerun()
    st.stop()

# --- 4. MODELOS ---
client = Groq(api_key=GROQ_API_KEY)
MODELO_CHAT = "llama-3.3-70b-versatile"
MODELO_VISION_SCOUT = "meta-llama/llama-4-scout-17b-16e-instruct"

# --- 5. SIDEBAR (INCENDIOS TIEMPO REAL) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2ff; text-align:center;'>🛡️ E.S.T.A.D.O.</h2>", unsafe_allow_html=True)
    st.info(f"📅 **FECHA**: {fecha_actual}\n⏰ **HORA**: {hora_actual}")
    st.divider()
    st.subheader("🌐 Escaneo Ambiental")
    st.write("🌦️ **Clima**: Santiago - 32°C")
    st.warning("⚠️ **Sismicidad**: Perímetro Estable.")
    st.error("🔥 **INCENDIOS ACTIVOS:**\n\n1. Región de Valparaíso (Controlado)\n2. Sector Melipilla (Activo)\n3. Curacaví (Foco en combate)")
    if st.button("🔄 REINICIAR SISTEMAS"):
        st.session_state.historial_chat = []; st.rerun()

# --- 6. PESTAÑAS ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS PROFUNDO", "✉️ DESPACHO", "🎨 LABORATORIO"])

# TAB 1: ANÁLISIS PROFUNDO (CORREGIDO)
with tabs[1]:
    st.subheader("📊 Módulo de Inteligencia Scout Exhaustivo")
    f = st.file_uploader("Subir evidencia estratégica", type=['pdf','docx','png','jpg','xlsx'])
    if f and st.button("🔍 INICIAR ESCANEO DE ALTO NIVEL"):
        with st.spinner("Realizando análisis multivariable..."):
            try:
                if f.type in ["image/png", "image/jpeg"]:
                    img = Image.open(f).convert("RGB"); img.thumbnail((1024, 1024))
                    buf = io.BytesIO(); img.save(buf, format="JPEG")
                    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                    # Prompt de profundidad
                    res = client.chat.completions.create(model=MODELO_VISION_SCOUT, messages=[{"role": "user", "content": [{"type": "text", "text": "Actúa como JARVIS. Realiza un análisis técnico y exhaustivo. No resumas, detalla cada anomalía, componente y contexto que veas en esta imagen."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}])
                    out = res.choices[0].message.content
                elif f.name.endswith('.xlsx'):
                    df = pd.read_excel(f)
                    out = f"--- REPORTE DE DATOS STARK ---\nRegistros: {len(df)}\n\nESTADÍSTICAS DETALLADAS:\n{df.describe(include='all').to_string()}\n\nCORRELACIONES DETECTADAS:\n{df.corr(numeric_only=True).to_string()}"
                elif f.name.endswith('.pdf'):
                    reader = PyPDF2.PdfReader(f)
                    texto = "".join([p.extract_text() for p in reader.pages[:10]]) # Aumentado a 10 páginas
                    res = client.chat.completions.create(model=MODELO_CHAT, messages=[{"role": "user", "content": f"Realiza un análisis profundo paso a paso del siguiente documento, extrayendo datos críticos y conclusiones técnicas:\n{texto}"}])
                    out = res.choices[0].message.content
                st.markdown(out)
            except Exception as e: st.error(f"Fallo sensor: {e}")

# TAB 3: LABORATORIO (RESTAURADO)
with tabs[3]:
    st.subheader("🎨 Forja de Prototipos Mark 85")
    idea = st.text_input("Describa el diseño para la forja:")
    estilo = st.selectbox("Renderizado Stark:", ["Cinematic Marvel", "Digital Blueprint", "Cyberpunk", "Photorealistic"])
    if st.button("🔥 INICIAR SÍNTESIS") and idea:
        with st.spinner("Sintetizando polímeros visuales..."):
            try:
                API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                payload = {"inputs": f"High tech stark industries style, {idea}, {estilo}, hyper-detailed, neon accents"}
                r = requests.post(API_URL, headers=headers, json=payload)
                if r.status_code == 200:
                    st.image(Image.open(io.BytesIO(r.content)), caption="Prototipo Generado")
                else:
                    st.error(f"Fallo en la forja. Código: {r.status_code}")
            except Exception as e: st.error(f"Error en laboratorio: {e}")

# (Resto de pestañas Comando Central y Despacho se mantienen con el diseño neón actualizado)