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
from reportlab.lib.colors import HexColor

# --- 1. CONFIGURACIÓN HUD Y VARIABLES ---
load_dotenv()
st.set_page_config(
    page_title="JARVIS - STARK INDUSTRIES", 
    page_icon="https://img.icons8.com/neon/256/iron-man.png", 
    layout="wide"
)

# Seguridad Stark
ACCESS_PASSWORD = st.secrets.get("ACCESS_PASSWORD") or os.getenv("ACCESS_PASSWORD", "STARK_RECOVERY_2026")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
GMAIL_USER = st.secrets.get("GMAIL_USER") or os.getenv("GMAIL_USER")
GMAIL_PASS = st.secrets.get("GMAIL_PASSWORD") or os.getenv("GMAIL_PASSWORD")
HF_TOKEN = st.secrets.get("HF_TOKEN") or os.getenv("HF_TOKEN")

zona_horaria = pytz.timezone('America/Santiago')
ahora = datetime.datetime.now(zona_horaria)
fecha_actual = ahora.strftime("%d de febrero de 2026")
hora_actual = ahora.strftime("%H:%M")

PERSONALIDAD = f"Eres JARVIS, el asistente de la Srta. Diana. Tono sofisticado. Santiago, Chile. {fecha_actual}."

# Función PDF
def generar_pdf_stark(titulo, contenido):
    buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=letter)
    c.setStrokeColor(HexColor("#00f2ff")); c.rect(20, 20, 572, 752, stroke=1)
    c.setFont("Helvetica-Bold", 18); c.setFillColor(HexColor("#00f2ff"))
    c.drawString(50, 730, f"STARK INDUSTRIES - {titulo}")
    c.setFont("Helvetica", 10); c.setFillColor(HexColor("#555555"))
    c.drawString(50, 715, f"EMISIÓN: {fecha_actual} | {hora_actual}")
    y = 680; c.setFillColor(HexColor("#000000")); c.setFont("Helvetica", 11)
    for linea in contenido.split('\n'):
        if y < 50: c.showPage(); y = 750
        c.drawString(50, y, linea[:95]); y -= 15
    c.save(); buf.seek(0); return buf

# --- 2. ESTILOS VISUALES STARK V3 ---
st.markdown("""
    <style>
    .stApp { background-color: #010409 !important; }
    .reactor-container { height: 260px; display: flex; justify-content: center; align-items: center; margin-top: -30px; }
    .reactor-core { 
        width: 125px; height: 125px; 
        background: radial-gradient(circle, #fff 5%, #00f2ff 45%, transparent 85%); 
        border-radius: 50%; box-shadow: 0 0 110px #00f2ff, inset 0 0 35px #00f2ff; 
        animation: pulse 2.5s infinite alternate ease-in-out; border: 2px solid rgba(0, 242, 255, 0.4);
    }
    @keyframes pulse { from { transform: scale(1); } to { transform: scale(1.15); } }
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
        pass_in = st.text_input("", type="password", placeholder="Código de acceso...")
        if st.button("DESBLOQUEAR"):
            if pass_in == ACCESS_PASSWORD: st.session_state["autenticado"] = True; st.rerun()
    st.stop()

# --- 4. MODELOS ---
client = Groq(api_key=GROQ_API_KEY)
MODELO_CHAT = "llama-3.3-70b-versatile"
MODELO_VISION_SCOUT = "meta-llama/llama-4-scout-17b-16e-instruct"

# --- 5. SIDEBAR (SENSORES COMPLETOS) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2ff; text-align:center;'>🛡️ E.S.T.A.D.O.</h2>", unsafe_allow_html=True)
    st.info(f"📅 **FECHA**: {fecha_actual}\n⏰ **HORA**: {hora_actual}")
    st.divider()
    st.subheader("🌐 Escaneo Ambiental")
    st.write("🌦️ **Clima**: Santiago - 32°C")
    st.warning("⚠️ **SISMICIDAD**: Estable. Sin alertas en el perímetro.") 
    st.error("🔥 **INCENDIOS ACTIVOS:**\n1. V Región\n2. Melipilla\n3. Curacaví")
    if st.button("🔄 REINICIAR SISTEMAS"):
        st.session_state.historial_chat = []; st.rerun()

# --- 6. PESTAÑAS ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS PROFUNDO", "✉️ DESPACHO", "🎨 LABORATORIO"])

# TAB 0: COMANDO CENTRAL (CON MANOS LIBRES)
with tabs[0]:
    if "historial_chat" not in st.session_state: st.session_state.historial_chat = []
    if "modo_fluido" not in st.session_state: st.session_state.modo_fluido = False
    st.session_state.modo_fluido = st.toggle("🎙️ MODO MANOS LIBRES", value=st.session_state.modo_fluido)
    
    for m in st.session_state.historial_chat:
        with st.chat_message(m["role"], avatar="🚀" if m["role"] == "assistant" else "👤"):
            st.markdown(m["content"])
            if "youtube" in m["content"]: st.video(m["content"].split()[-1])

    col_mic, col_chat = st.columns([1, 10])
    with col_mic: audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key="jarvis_mic")
    with col_chat: prompt = st.chat_input("Órdenes, Srta. Diana...")

    final_text = None
    if audio_data and 'bytes' in audio_data:
        trans = client.audio.transcriptions.create(file=("v.wav", audio_data['bytes']), model="whisper-large-v3", language="es")
        final_text = trans.text
    elif prompt: final_text = prompt

    if final_text:
        st.session_state.historial_chat.append({"role": "user", "content": final_text})
        res = client.chat.completions.create(model=MODELO_CHAT, messages=[{"role": "system", "content": PERSONALIDAD}] + st.session_state.historial_chat[-5:])
        ans = res.choices[0].message.content
        st.session_state.historial_chat.append({"role": "assistant", "content": ans})
        
        js = f"""<script>
            var m = new SpeechSynthesisUtterance({repr(ans)}); m.lang='es-ES';
            m.onend = function() {{
                if ({str(st.session_state.modo_fluido).lower()}) {{
                    setTimeout(() => {{ window.parent.document.querySelector('button[aria-label="🎙️"]').click(); }}, 1000);
                }}
            }}; window.speechSynthesis.speak(m);
        </script>"""
        st.components.v1.html(js, height=0); st.rerun()

# TAB 1: ANÁLISIS PROFUNDO (SCOUT + PDF)
with tabs[1]:
    st.subheader("📊 Inteligencia Scout Exhaustiva")
    f = st.file_uploader("Cargar evidencia técnica", type=['pdf','png','jpg','xlsx'])
    if f and st.button("🔍 INICIAR ESCANEO"):
        with st.spinner("Analizando con protocolos Llama-4-Scout..."):
            try:
                if f.type in ["image/png", "image/jpeg"]:
                    img = Image.open(f).convert("RGB"); img.thumbnail((1024, 1024))
                    buf = io.BytesIO(); img.save(buf, format="JPEG"); b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                    res = client.chat.completions.create(model=MODELO_VISION_SCOUT, messages=[{"role": "user", "content": [{"type": "text", "text": "Análisis industrial exhaustivo."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}])
                    out = res.choices[0].message.content
                elif f.name.endswith('.pdf'):
                    reader = PyPDF2.PdfReader(f); out = "".join([p.extract_text() for p in reader.pages[:10]])
                    res = client.chat.completions.create(model=MODELO_CHAT, messages=[{"role": "user", "content": f"Analiza este documento:\n{out}"}])
                    out = res.choices[0].message.content
                else: out = "Formato procesado."
                st.markdown(f"### 📑 Resultado:\n{out}")
                st.download_button("📥 DESCARGAR REPORTE PDF", generar_pdf_stark("SCOUT REPORT", out), "Reporte.pdf")
            except Exception as e: st.error(f"Fallo en Scout: {e}")

# TAB 2: DESPACHO
with tabs[2]:
    st.subheader("✉️ Terminal de Comunicaciones")
    dest = st.text_input("Para:", value=GMAIL_USER)
    asunto = st.text_input("Asunto:", value="INFORME STARK")
    cuerpo = st.text_area("Mensaje")
    f_adj = st.file_uploader("📎 Adjunto", key="mail_adj")
    if st.button("🚀 TRANSMITIR"):
        st.success("Transmisión preparada.")

# TAB 3: LABORATORIO (GENERACIÓN + FILTROS)
with tabs[3]:
    st.subheader("🎨 Forja Mark 85")
    idea = st.text_input("Concepto Visual:")
    estilo = st.selectbox("Filtro Stark:", ["Cinematic Marvel", "Digital Blueprint", "Cyberpunk", "Photorealistic", "Blueprint Tech"])
    if st.button("🔥 GENERAR PROTOTIPO") and idea:
        with st.spinner("Sintetizando..."):
            try:
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                payload = {"inputs": f"stark industries tech, {idea}, {estilo}, highly detailed"}
                r = requests.post("https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0", headers=headers, json=payload)
                if r.status_code == 200: st.image(Image.open(io.BytesIO(r.content)))
                else: st.error(f"Error en la forja: {r.status_code}")
            except Exception as e: st.error(f"Fallo de conexión: {e}")