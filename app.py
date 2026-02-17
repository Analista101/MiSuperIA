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
import numpy as np
import cv2
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

# Variables de Entorno (Recuperación de Secrets o Local)
ACCESS_PASSWORD = st.secrets.get("ACCESS_PASSWORD") or os.getenv("ACCESS_PASSWORD", "STARK_RECOVERY_2026")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
GMAIL_USER = st.secrets.get("GMAIL_USER") or os.getenv("GMAIL_USER")
GMAIL_PASS = st.secrets.get("GMAIL_PASSWORD") or os.getenv("GMAIL_PASSWORD")
HF_TOKEN = st.secrets.get("HF_TOKEN") or os.getenv("HF_TOKEN")

# Zona Horaria y Personalidad JARVIS
zona_horaria = pytz.timezone('America/Santiago')
ahora = datetime.datetime.now(zona_horaria)
fecha_actual = ahora.strftime("%d de febrero de 2026")
hora_actual = ahora.strftime("%H:%M")

PERSONALIDAD = (
    f"Eres JARVIS, el asistente de la Srta. Diana. Tu tono es sofisticado, ingenioso y servicial. "
    f"Usa terminología de Stark Industries. Ubicación: Santiago, Chile. "
    f"Fecha: {fecha_actual} | Hora: {hora_actual}."
)

# --- 2. ESTILOS HUD (BOTONES NEÓN + REACTOR ARK) ---
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

    /* Botones Neón Stark */
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

    /* Estilo para Micrófono HUD */
    button[aria-label="🎙️"], button[aria-label="🟢"], button[aria-label="🛑"] {
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        border: 2px solid #00f2ff !important;
    }

    .stChatInputContainer {
        border: 2px solid #00f2ff !important;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.4) !important;
        background: rgba(0, 0, 0, 0.8) !important;
    }

    /* Animación Reactor Ark */
    .reactor-container { position: relative; height: 200px; display: flex; justify-content: center; align-items: center; margin-top: 10px; }
    .reactor-core { 
        width: 70px; height: 70px; background: radial-gradient(circle, #fff 5%, #00f2ff 50%, transparent 80%); 
        border-radius: 50%; box-shadow: 0 0 50px #00f2ff; z-index: 10; 
        animation: pulse-breathe 2.5s infinite alternate ease-in-out; 
    }
    .hologram-ring { position: absolute; border: 2px solid rgba(0, 242, 255, 0.4); border-radius: 50%; animation: rotate linear infinite; }
    .ring-outer { width: 180px; height: 180px; border-style: double; animation-duration: 20s; }
    .ring-inner { width: 120px; height: 120px; border-width: 1px; animation-duration: 10s; }
    
    @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    @keyframes pulse-breathe {
        0% { transform: scale(1); opacity: 0.7; }
        100% { transform: scale(1.1); opacity: 1; }
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
        st.markdown("<h2 style='color:#00f2ff; text-align:center;'>🔐 ACCESO RESTRINGIDO</h2>", unsafe_allow_html=True)
        pass_in = st.text_input("Ingrese Código de Identificación Stark:", type="password")
        if st.button("DESBLOQUEAR SISTEMA"):
            if pass_in == ACCESS_PASSWORD:
                st.session_state["autenticado"] = True
                st.success("Acceso concedido. Bienvenido, Srta. Diana.")
                st.rerun()
            else:
                st.error("Código incorrecto. Intento registrado.")
    st.stop()

# --- 4. INICIALIZACIÓN IA ---
client = Groq(api_key=GROQ_API_KEY)
modelo_texto = "llama-3.3-70b-versatile"

# --- 5. FUNCIONES CORE ---
def generar_pdf_reporte(titulo, contenido):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, f"STARK INDUSTRIES - {titulo}")
    text_object = c.beginText(100, 700)
    text_object.setFont("Helvetica", 10)
    for line in contenido.split('\n'):
        text_object.textLine(line[:95])
    c.drawText(text_object)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# --- 6. BARRA LATERAL (ESTADO PERIMETRAL) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2ff; text-align:center;'>🛡️ E.S.T.A.D.O.</h2>", unsafe_allow_html=True)
    st.info(f"📅 **FECHA**: {fecha_actual}")
    st.info(f"⏰ **HORA**: {hora_actual}")
    st.divider()
    st.subheader("🌐 Escaneo Ambiental")
    st.write("🌦️ **Clima**: Pudahuel - Despejado (32°C)")
    st.warning("⚠️ **Sismicidad**: Actividad detectada en sector costero.")
    st.error("🔥 **Incendios**: Alerta roja en zonas forestales.")
    if st.button("🔄 REINICIAR SISTEMAS"):
        st.session_state.historial_chat = []
        st.rerun()

# --- 7. COMANDO CENTRAL (TABS) ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS", "✉️ DESPACHO", "🎨 LABORATORIO"])

# --- TAB 0: COMANDO CENTRAL ---
with tabs[0]:
    if "historial_chat" not in st.session_state: st.session_state.historial_chat = []
    if "modo_fluido" not in st.session_state: st.session_state.modo_fluido = False
    
    st.session_state.modo_fluido = st.toggle("🎙️ MODO MANOS LIBRES (JARVIS AUTO-ESCUCHA)", value=st.session_state.modo_fluido)
    
    # Contenedor de Chat
    for m in st.session_state.historial_chat:
        with st.chat_message(m["role"], avatar="🚀" if m["role"] == "assistant" else "👤"):
            st.markdown(m["content"])
    
    # Input de Voz y Texto
    col_mic, col_chat = st.columns([1, 10])
    with col_mic:
        audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key="jarvis_mic")
    with col_chat:
        prompt = st.chat_input("Órdenes, Srta. Diana...")

    texto_final = None
    if audio_data and 'bytes' in audio_data:
        with st.spinner("Decodificando audio..."):
            trans = client.audio.transcriptions.create(file=("v.wav", audio_data['bytes']), model="whisper-large-v3", language="es")
            texto_final = trans.text
    elif prompt:
        texto_final = prompt

    if texto_final:
        st.session_state.historial_chat.append({"role": "user", "content": texto_final})
        with st.chat_message("user", avatar="👤"): st.write(texto_final)
        
        with st.chat_message("assistant", avatar="🚀"):
            with st.spinner("Consultando base de datos Stark..."):
                ctx = [{"role": "system", "content": PERSONALIDAD}] + st.session_state.historial_chat[-6:]
                res = client.chat.completions.create(model=modelo_texto, messages=ctx)
                ans = res.choices[0].message.content
                st.markdown(ans)
                st.session_state.historial_chat.append({"role": "assistant", "content": ans})
        
        # Respuesta por Voz y Auto-Escucha (Corrección de llaves para f-string)
        js_speech = f"""
            <script>
            var msg = new SpeechSynthesisUtterance({repr(ans)});
            msg.lang = 'es-ES';
            msg.rate = 1.0;
            msg.onend = function() {{
                if ({str(st.session_state.modo_fluido).lower()}) {{
                    setTimeout(function() {{
                        const micBtn = window.parent.document.querySelector('button[aria-label="🎙️"]');
                        if (micBtn) micBtn.click();
                    }}, 1000);
                }}
            }};
            window.speechSynthesis.speak(msg);
            </script>
        """
        st.components.v1.html(js_speech, height=0)
        st.rerun()

# --- TAB 1: ANÁLISIS DE EVIDENCIA ---
with tabs[1]:
    st.subheader("📊 Módulo de Análisis de Inteligencia")
    archivo = st.file_uploader("Cargar evidencia (PDF, Imagen, CSV)", type=['pdf','docx','png','jpg','xlsx'])
    
    if archivo:
        if st.button("🔍 INICIAR ESCANEO"):
            with st.spinner("Analizando componentes..."):
                if archivo.type in ["image/png", "image/jpeg"]:
                    b64_img = base64.b64encode(archivo.read()).decode('utf-8')
                    resp = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Describe y analiza esta imagen técnicamente en español."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                        ]}]
                    )
                    analisis = resp.choices[0].message.content
                else:
                    analisis = "Documento procesado. Datos estructurados listos para reporte PDF."
                
                st.markdown(f"### 📋 Resultado del Análisis:\n{analisis}")
                st.download_button("📥 DESCARGAR REPORTE STARK", generar_pdf_reporte("ANÁLISIS TÉCNICO", analisis), "Reporte_Stark.pdf")

# --- TAB 2: COMUNICACIONES (EMAIL) ---
with tabs[2]:
    st.subheader("✉️ Terminal de Comunicaciones Encriptadas")
    c1, c2 = st.columns(2)
    with c1: destinatario = st.text_input("Para:", value="diana@stark.com")
    with c2: asunto = st.text_input("Asunto:", value="INFORME DE SITUACIÓN")
    cuerpo = st.text_area("Mensaje de voz a texto o manual:", height=150)
    adjunto_mail = st.file_uploader("Adjuntar archivo técnico", key="mail_file")
    
    if st.button("🚀 TRANSMITIR MENSAJE"):
        try:
            with st.spinner("Enviando vía satélite Stark..."):
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(GMAIL_USER, GMAIL_PASS)
                
                msg = MIMEMultipart()
                msg['From'], msg['To'], msg['Subject'] = GMAIL_USER, destinatario, asunto
                msg.attach(MIMEText(cuerpo, 'plain'))
                
                if adjunto_mail:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(adjunto_mail.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={adjunto_mail.name}')
                    msg.attach(part)
                
                server.send_message(msg)
                server.quit()
                st.success("Mensaje transmitido con éxito.")
        except Exception as e:
            st.error(f"Error en la transmisión: {e}")

# --- TAB 3: LABORATORIO (GENERACIÓN DE IMÁGENES) ---
with tabs[3]:
    st.subheader("🎨 Forja de Prototipos Mark 85")
    idea = st.text_input("Defina el concepto visual:")
    estilo_ia = st.selectbox("Filtro de Renderizado:", ["Cinematic Marvel", "Digital Blueprint", "Cyberpunk Santiago", "Photorealistic"])
    
    if st.button("🔥 SINTETIZAR IMAGEN") and idea:
        with st.spinner("Operando Stable Diffusion XL..."):
            API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            payload = {"inputs": f"{idea}, {estilo_ia} style, ultra high definition, stark industries technology"}
            
            response = requests.post(API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                st.image(Image.open(io.BytesIO(response.content)), caption="Prototipo Generado por JARVIS")
            else:
                st.error("La forja está sobrecalentada. Intente en unos minutos.")