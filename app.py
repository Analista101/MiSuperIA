import streamlit as st
import os
import io, base64, random
import docx
import pandas as pd
import PyPDF2
import requests
import datetime
import pytz
import smtplib
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

# --- 1. CONFIGURACIÓN DE SEGURIDAD Y HUD ---
load_dotenv()
st.set_page_config(
    page_title="JARVIS - STARK INDUSTRIES", 
    page_icon="https://img.icons8.com/neon/256/iron-man.png", 
    layout="wide"
)

# Variables de Entorno
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
    f"Usa terminología de Stark Industries. Responde siempre en ESPAÑOL. "
    f"Ubicación: Santiago, Chile. Fecha: {fecha_actual} | Hora: {hora_actual}."
)

# --- 2. ESTILOS HUD (BOTONES NEÓN + REACTOR QUE RESPIRA) ---
st.markdown("""
    <style>
    .stApp {
        background: #010409 !important;
        background-image: 
            radial-gradient(circle at 50% 30%, rgba(0, 242, 255, 0.15) 0% , transparent 60%),
            url('https://wallpaperaccess.com/full/156094.jpg') !important;
        background-size: cover !important;
        background-blend-mode: overlay;
    }

    button, div.stButton > button, div.stDownloadButton > button {
        background: rgba(0, 242, 255, 0.05) !important;
        color: #00f2ff !important;
        border: 1px solid #00f2ff !important;
        border-radius: 5px !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 8px rgba(0, 242, 255, 0.3) !important;
        width: 100%;
    }

    button:hover {
        background: rgba(0, 242, 255, 0.2) !important;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.6) !important;
        color: #ffffff !important;
        border-color: #ffffff !important;
    }

    button[aria-label="🎙️"], button[aria-label="🟢"], button[aria-label="🛑"] {
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        border: 2px solid #00f2ff !important;
    }

    .stChatInputContainer {
        border: 2px solid #00f2ff !important;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.4) !important;
        background: rgba(0, 0, 0, 0.8) !important;
    }

    .reactor-container { position: relative; height: 250px; display: flex; justify-content: center; align-items: center; margin-top: -30px; }
    .reactor-core { 
        width: 80px; height: 80px; background: radial-gradient(circle, #fff 5%, #00f2ff 50%, transparent 80%); 
        border-radius: 50%; box-shadow: 0 0 60px #00f2ff; z-index: 10; 
        animation: pulse-breathe 2.5s infinite alternate ease-in-out; 
    }
    .hologram-ring { position: absolute; border: 2px solid rgba(0, 242, 255, 0.4); border-radius: 50%; animation: rotate linear infinite; }
    .ring-outer { width: 220px; height: 220px; border-style: double; animation-duration: 20s; }
    .ring-inner { width: 140px; height: 140px; border-width: 1px; animation-duration: 10s; }
    
    @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    @keyframes pulse-breathe {
        0% { transform: scale(1); box-shadow: 0 0 40px rgba(0, 242, 255, 0.6); }
        100% { transform: scale(1.05); box-shadow: 0 0 80px rgba(0, 242, 255, 1); }
    }
    </style>
    <div class="reactor-container">
        <div class="hologram-ring ring-outer"></div>
        <div class="hologram-ring ring-inner"></div>
        <div class="reactor-core"></div>
    </div>
""", unsafe_allow_html=True)

# --- 3. AUTENTICACIÓN ---
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 ACCESO RESTRINGIDO")
        pass_in = st.text_input("Código de Identificación:", type="password")
        if st.button("DESBLOQUEAR"):
            if pass_in == ACCESS_PASSWORD:
                st.session_state["autenticado"] = True
                st.rerun()
    st.stop()

# --- 4. CONEXIONES IA ---
client = Groq(api_key=GROQ_API_KEY)
modelo_texto = "llama-3.3-70b-versatile"
modelo_vision = "llama-3.2-11b-vision-preview"

# --- 5. FUNCIONES DE SOPORTE ---
def generar_pdf_reporte(titulo, contenido):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16); c.drawString(100, 750, f"STARK INDUSTRIES - {titulo}")
    text_object = c.beginText(100, 700); text_object.setFont("Helvetica", 10)
    for line in contenido.split('\n'): text_object.textLine(line[:95])
    c.drawText(text_object); c.showPage(); c.save(); buffer.seek(0)
    return buffer

# --- 6. MÓDULO DE ALERTAS (SIDEBAR) ---
with st.sidebar:
    st.markdown("""<div style='text-align: center; padding: 10px; border: 1px solid #00f2ff; border-radius: 10px; background: rgba(0, 242, 255, 0.05);'>
        <h3 style='color: #00f2ff; font-family: "Courier New";'>🛡️ ESTADO DE ALERTA</h3></div>""", unsafe_allow_html=True)
    st.info("🌦️ **CLIMA**: Despejado (32°C). Sin lluvias en Pudahuel.")
    st.warning("🌋 **SISMICIDAD**: Actividad media-alta detectada.")
    st.error("🔥 **INCENDIOS**: Pudahuel: Fuego controlado.")
    st.markdown("---")

# --- 7. PESTAÑAS ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS", "✉️ COMUNICACIONES", "🎨 LABORATORIO"])

# --- TAB 0: COMANDO CENTRAL ---
with tabs[0]:
    if "historial_chat" not in st.session_state: st.session_state.historial_chat = []
    if "modo_fluido" not in st.session_state: st.session_state.modo_fluido = False
    st.session_state.modo_fluido = st.toggle("🎙️ MODO MANOS LIBRES", value=st.session_state.modo_fluido)
    for m in st.session_state.historial_chat:
        with st.chat_message(m["role"], avatar="🚀" if m["role"] == "assistant" else "👤"): st.write(m["content"])
    
    col_mic, col_chat = st.columns([1, 12])
    with col_mic: audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key="mic_v1")
    with col_chat: prompt = st.chat_input("Escriba o hable, Srta. Diana...")

    texto_a_procesar = None
    if audio_data and 'bytes' in audio_data:
        trans = client.audio.transcriptions.create(file=("v.wav", audio_data['bytes']), model="whisper-large-v3", language="es")
        texto_a_procesar = trans.text
    elif prompt: texto_a_procesar = prompt

    if texto_a_procesar:
        st.session_state.historial_chat.append({"role": "user", "content": texto_a_procesar})
        ctx = [{"role": "system", "content": PERSONALIDAD}] + st.session_state.historial_chat[-6:]
        res = client.chat.completions.create(model=modelo_texto, messages=ctx)
        ans = res.choices[0].message.content
        st.session_state.historial_chat.append({"role": "assistant", "content": ans})
        
        js_script = f"<script>var msg = new SpeechSynthesisUtterance({repr(ans)}); msg.lang='es-ES'; msg.onend = function() {{ if({str(st.session_state.modo_fluido).lower()}) {{ setTimeout(function() {{ const b = window.parent.document.querySelector('button[aria-label=\"🎙️\"]'); if(b) b.click(); }}, 1000); }} }}; window.speechSynthesis.speak(msg);</script>"
        st.components.v1.html(js_script, height=0); st.rerun()

# --- TAB 1: ANÁLISIS (REPARADO: VISIÓN Y DOCUMENTOS) ---
with tabs[1]:
    st.subheader("📊 Análisis de Inteligencia Profundo")
    file = st.file_uploader("Evidencia técnica", type=['pdf','docx','xlsx','txt','png','jpg','jpeg'], key="an_file")
    if file and st.button("🔍 ANALIZAR"):
        with st.spinner("Procesando análisis exhaustivo..."):
            try:
                # CASO 1: IMÁGENES (REPARADO)
                if file.type in ["image/png", "image/jpeg"]:
                    # Redimensionar para evitar BadRequestError por tamaño
                    img = Image.open(file).convert("RGB")
                    img.thumbnail((800, 800))
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG")
                    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                    
                    resp = client.chat.completions.create(
                        model=modelo_vision, 
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Actúa como el sistema de visión JARVIS. Analiza esta imagen en ESPAÑOL con máximo detalle técnico e identifica anomalías."}, 
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                        ]}]
                    )
                    ans_an = resp.choices[0].message.content

                # CASO 2: DOCUMENTOS (AÑADIDO ANÁLISIS REAL)
                else:
                    texto_extraido = ""
                    if file.name.endswith('.pdf'):
                        reader = PyPDF2.PdfReader(file)
                        texto_extraido = "\n".join([page.extract_text() for page in reader.pages[:5]]) # Analiza primeras 5 páginas
                    elif file.name.endswith('.docx'):
                        doc = docx.Document(file)
                        texto_extraido = "\n".join([para.text for para in doc.paragraphs])
                    elif file.name.endswith('.xlsx'):
                        df = pd.read_excel(file)
                        texto_extraido = df.head(20).to_string() # Analiza cabecera de datos
                    else:
                        texto_extraido = file.read().decode('utf-8')

                    # Enviar texto extraído a la IA para análisis real
                    resp = client.chat.completions.create(
                        model=modelo_texto,
                        messages=[
                            {"role": "system", "content": "Eres el módulo de análisis de datos de JARVIS. Analiza el siguiente contenido técnico en ESPAÑOL y genera un reporte."},
                            {"role": "user", "content": f"Contenido del archivo {file.name}:\n\n{texto_extraido}"}
                        ]
                    )
                    ans_an = resp.choices[0].message.content

                st.markdown(ans_an)
                st.download_button("📥 REPORTE PDF", generar_pdf_reporte("REPORTE SCOUT", ans_an), "Reporte_Stark.pdf")
            
            except Exception as e:
                st.error(f"Fallo en los sensores de análisis: {str(e)}")

# --- TAB 2: COMUNICACIONES ---
with tabs[2]:
    st.subheader("✉️ Despacho Stark")
    c1, c2 = st.columns(2)
    dest = c1.text_input("Para:", value=GMAIL_USER)
    asun = c2.text_input("Asunto:", value="Confidencial")
    cuer = st.text_area("Mensaje:")
    adj = st.file_uploader("📎 Adjunto:", key="mail_adj")
    if st.button("🚀 ENVIAR"):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587); server.starttls(); server.login(GMAIL_USER, GMAIL_PASS)
            msg = MIMEMultipart(); msg['From'] = GMAIL_USER; msg['To'] = dest; msg['Subject'] = asun
            msg.attach(MIMEText(cuer, 'plain'))
            if adj:
                part = MIMEBase('application', 'octet-stream'); part.set_payload(adj.read()); encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={adj.name}'); msg.attach(part)
            server.send_message(msg); server.quit(); st.success("Enviado.")
        except Exception as e: st.error(f"Error: {e}")

# --- TAB 3: LABORATORIO (FIX ERROR 410) ---
with tabs[3]:
    st.subheader("🎨 Prototipado Mark 85")
    idea = st.text_input("Concepto:")
    estilo = st.selectbox("Filtro:", ["Cinematic Marvel", "Technical Drawing", "Cyberpunk", "Blueprint Tech"])
    if st.button("🚀 SINTETIZAR") and idea:
        with st.spinner("Sintetizando polímeros visuales..."):
            url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            payload = {"inputs": f"Stark Industries tech, {idea}, {estilo} style, highly detailed"}
            resp = requests.post(url, headers=headers, json=payload)
            if resp.status_code == 200: st.image(Image.open(io.BytesIO(resp.content)))
            else: st.error(f"Fallo en la forja: {resp.status_code}. Reintente en unos segundos.")