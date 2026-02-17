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
    f"Usa terminología de Stark Industries. Ubicación: Santiago, Chile. "
    f"Fecha: {fecha_actual} | Hora: {hora_actual}."
)

# --- INYECCIÓN HUD AVANZADO (MARK 190 - RÉPLICA EXACTA) ---
st.markdown("""
    <style>
    /* 1. Fondo con Mapa Global y Gradientes */
    .stApp {
        background: #010409 !important;
        background-image: 
            radial-gradient(circle at 50% 30%, rgba(0, 242, 255, 0.2) 0%, transparent 60%),
            url('https://wallpaperaccess.com/full/156094.jpg') !important; /* Mapa sutil de fondo */
        background-size: cover !important;
        background-blend-mode: overlay;
    }

    /* 2. El Reactor Arc con Anillos Holográficos */
    .reactor-container {
        position: relative;
        height: 250px;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: -30px;
    }

    .reactor-core {
        width: 80px;
        height: 80px;
        background: radial-gradient(circle, #fff 5%, #00f2ff 50%, transparent 80%);
        border-radius: 50%;
        box-shadow: 0 0 60px #00f2ff;
        z-index: 10;
    }

    .hologram-ring {
        position: absolute;
        border: 2px solid rgba(0, 242, 255, 0.4);
        border-radius: 50%;
        animation: rotate linear infinite;
    }

    .ring-outer { width: 220px; height: 220px; border-style: double; animation-duration: 20s; }
    .ring-middle { width: 180px; height: 180px; border-style: dashed; animation-duration: 15s; animation-direction: reverse; }
    .ring-inner { width: 140px; height: 140px; border-width: 1px; border-color: rgba(0, 242, 255, 0.6); animation-duration: 10s; }

    @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

    /* 3. Barra de Chat "Cyan Glow" */
    .stChatInputContainer {
        border: 2px solid #00f2ff !important;
        background: rgba(13, 27, 42, 0.8) !important;
        border-radius: 15px !important;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.4), inset 0 0 10px rgba(0, 242, 255, 0.2) !important;
        padding: 5px !important;
    }

    /* 4. Estilo de Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid rgba(0, 242, 255, 0.2);
    }

    .stTabs [data-baseweb="tab"] {
        color: #778da9 !important;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }

    .stTabs [aria-selected="true"] {
        color: #00f2ff !important;
        border-bottom: 2px solid #00f2ff !important;
    }

    /* 5. Iconos de estado */
    .status-text {
        color: #00f2ff;
        font-family: 'Courier New', monospace;
        letter-spacing: 3px;
        text-shadow: 0 0 5px #00f2ff;
        font-size: 0.8rem;
        margin-top: 10px;
    }
    </style>

    <div class="reactor-container">
        <div class="hologram-ring ring-outer"></div>
        <div class="hologram-ring ring-middle"></div>
        <div class="hologram-ring ring-inner"></div>
        <div class="reactor-core"></div>
    </div>
    <div style="text-align: center;">
        <p class="status-text">JARVIS V.2.0 | PROTOCOLO DIANA STARK</p>
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

# --- 5. PROTOCOLOS DE SOPORTE ---
def generar_pdf_reporte(titulo, contenido):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16); c.drawString(100, 750, "STARK INDUSTRIES - REPORTE DE INTELIGENCIA")
    c.line(100, 725, 500, 725)
    text_object = c.beginText(100, 700); text_object.setFont("Helvetica", 10)
    for line in contenido.split('\n'): text_object.textLine(line[:95])
    c.drawText(text_object); c.showPage(); c.save(); buffer.seek(0)
    return buffer

def enviar_correo_stark(dest, asunto, cuerpo):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587); server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        msg = MIMEMultipart(); msg['From'] = GMAIL_USER; msg['To'] = dest; msg['Subject'] = asunto
        msg.attach(MIMEText(cuerpo, 'plain'))
        server.send_message(msg); server.quit()
        return True
    except: return False

# --- 6. PESTAÑAS ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS", "✉️ COMUNICACIONES", "🎨 LABORATORIO"])

# --- TAB 0: COMANDO CENTRAL (MANOS LIBRES) ---
with tabs[0]:
    if "historial_chat" not in st.session_state: st.session_state.historial_chat = []
    if "modo_fluido" not in st.session_state: st.session_state.modo_fluido = False
    st.session_state.modo_fluido = st.toggle("🎙️ MODO MANOS LIBRES (SIRI STYLE)", value=st.session_state.modo_fluido)
    for m in st.session_state.historial_chat:
        with st.chat_message(m["role"], avatar="🚀" if m["role"] == "assistant" else "👤"): st.write(m["content"])
    col_mic, col_chat = st.columns([1, 12])
    with col_mic:
        audio_data = mic_recorder(start_prompt="🎙️" if not st.session_state.modo_fluido else "🟢", stop_prompt="🛑", key="mic_v189")
    with col_chat: prompt = st.chat_input("Escriba o hable, Srta. Diana...")
    texto_a_procesar = None
    if audio_data and 'bytes' in audio_data:
        audio_hash = hash(audio_data['bytes'])
        if "last_audio_hash" not in st.session_state or st.session_state.last_audio_hash != audio_hash:
            trans = client.audio.transcriptions.create(file=("voice.wav", audio_data['bytes']), model="whisper-large-v3", language="es")
            texto_a_procesar = trans.text
            st.session_state.last_audio_hash = audio_hash
    elif prompt: texto_a_procesar = prompt
    if texto_a_procesar:
        st.session_state.historial_chat.append({"role": "user", "content": texto_a_procesar})
        ctx = [{"role": "system", "content": PERSONALIDAD}] + st.session_state.historial_chat[-6:]
        res = client.chat.completions.create(model=modelo_texto, messages=ctx)
        ans = res.choices[0].message.content
        st.session_state.historial_chat.append({"role": "assistant", "content": ans})
        js_script = f"<script>var msg = new SpeechSynthesisUtterance({repr(ans)}); msg.lang='es-ES'; msg.onend=function(){{if({str(st.session_state.modo_fluido).lower()}){{setTimeout(function(){{const b=window.parent.document.querySelector('button[aria-label=\"🎙️\"]'); if(b)b.click();}},1000);}}}}; window.speechSynthesis.speak(msg);</script>"
        st.components.v1.html(js_script, height=0); st.rerun()

# --- TAB 1: ANÁLISIS (VISIÓN + DOCUMENTOS) ---
with tabs[1]:
    st.subheader("📊 Análisis de Inteligencia Multimodal")
    file = st.file_uploader("Cargar evidencia", type=['pdf','docx','xlsx','txt','png','jpg','jpeg'], key="scanner_v189")
    if file and st.button("🔍 INICIAR ANÁLISIS"):
        with st.spinner("JARVIS está analizando..."):
            try:
                if file.type in ["image/png", "image/jpeg", "image/jpg"]:
                    base64_image = base64.b64encode(file.read()).decode('utf-8')
                    response = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[{"role": "user", "content": [{"type": "text", "text": "Analiza esta imagen en ESPAÑOL."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
                    )
                else:
                    txt = ""
                    if file.type == "application/pdf":
                        reader = PyPDF2.PdfReader(file)
                        for page in reader.pages: txt += page.extract_text()
                    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        doc = docx.Document(file)
                        for p in doc.paragraphs: txt += p.text + "\n"
                    elif file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                        df = pd.read_excel(file); txt = df.to_string()
                    else: txt = file.read().decode()
                    prompt_an = f"Razonamiento y respuesta en ESPAÑOL: {txt[:8000]}"
                    response = client.chat.completions.create(model="qwen/qwen3-32b", messages=[{"role":"user","content":prompt_an}], reasoning_format="raw")
                
                full_res = response.choices[0].message.content
                if "<think>" in full_res:
                    parts = full_res.split("</think>")
                    with st.expander("🧠 RAZONAMIENTO"): st.info(parts[0].replace("<think>",""))
                    st.markdown(parts[1])
                    rep_content = parts[1]
                else: 
                    st.markdown(full_res)
                    rep_content = full_res
                
                pdf_file = generar_pdf_reporte("REPORTE STARK", rep_content)
                st.download_button("📥 DESCARGAR REPORTE PDF", pdf_file, "Reporte_Stark.pdf", "application/pdf")
            except Exception as e: st.error(f"Error: {e}")

# --- TAB 2: COMUNICACIONES ---
with tabs[2]:
    st.subheader("✉️ Centro de Despacho")
    c1, c2 = st.columns(2)
    dest = c1.text_input("Para:", value=GMAIL_USER)
    asun = c2.text_input("Asunto:", value="Reporte Stark")
    cuer = st.text_area("Mensaje:")
    if st.button("🚀 ENVIAR CORREO"):
        if enviar_correo_stark(dest, asun, cuer): st.success("Mensaje enviado con éxito.")
        else: st.error("Error en el envío.")

# --- TAB 3: LABORATORIO (MARK 85 - CON FILTROS) ---
with tabs[3]:
    st.subheader("🎨 Estación de Diseño Mark 85")
    col_p, col_f = st.columns([2, 1])
    with col_p: idea = st.text_input("Descripción del Prototipo:", key="lab_v189")
    with col_f: estilo = st.selectbox("Filtro de Renderizado:", ["Cinematic Marvel", "Technical Drawing", "Cyberpunk", "Industrial Stark", "Photorealistic"])
    
    if st.button("🚀 SINTETIZAR DISEÑO") and idea:
        with st.spinner("Sintetizando en la forja digital..."):
            url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            resp = requests.post(url, headers=headers, json={"inputs": f"{idea}, {estilo} style, high quality, 8k"})
            if resp.status_code == 200:
                st.image(Image.open(io.BytesIO(resp.content)), caption=f"Prototipo: {idea} | Estilo: {estilo}")
            else: st.error("El sintetizador está fuera de línea o el token es inválido.")