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

# --- 2. ESTILOS HUD ---
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
        box-shadow: 0 0 8px rgba(0, 242, 255, 0.3) !important;
        width: 100%;
    }
    .reactor-container { position: relative; height: 250px; display: flex; justify-content: center; align-items: center; margin-top: -30px; }
    .reactor-core { 
        width: 80px; height: 80px; background: radial-gradient(circle, #fff 5%, #00f2ff 50%, transparent 80%); 
        border-radius: 50%; box-shadow: 0 0 60px #00f2ff; animation: pulse-breathe 2.5s infinite alternate ease-in-out; 
    }
    @keyframes pulse-breathe { 0% { transform: scale(1); } 100% { transform: scale(1.05); } }
    </style>
    <div class="reactor-container"><div class="reactor-core"></div></div>
""", unsafe_allow_html=True)

# --- 3. AUTENTICACIÓN ---
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 ACCESO RESTRINGIDO")
        pass_in = st.text_input("Código de Identificación:", type="password")
        if st.button("DESBLOQUEAR"):
            if pass_in == ACCESS_PASSWORD: st.session_state["autenticado"] = True; st.rerun()
    st.stop()

# --- 4. CONEXIONES IA ---
client = Groq(api_key=GROQ_API_KEY)
modelo_texto = "llama-3.3-70b-versatile"
# ACTUALIZACIÓN: Modelo Scout de Visión
modelo_vision_scout = "meta-llama/llama-4-scout-17b-16e-instruct"

def generar_pdf_reporte(titulo, contenido):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16); c.drawString(100, 750, f"STARK INDUSTRIES - {titulo}")
    text_object = c.beginText(100, 700); text_object.setFont("Helvetica", 10)
    for line in contenido.split('\n'): text_object.textLine(line[:95])
    c.drawText(text_object); c.showPage(); c.save(); buffer.seek(0)
    return buffer

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown("<h3 style='color: #00f2ff;'>🛡️ ESTADO DE ALERTA</h3>", unsafe_allow_html=True)
    st.info("🌦️ **CLIMA**: Despejado (32°C).")
    st.warning("🌋 **SISMICIDAD**: Actividad media-alta.")
    st.error("🔥 **INCENDIOS**: Pudahuel controlado.")

# --- 7. PESTAÑAS ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS", "✉️ COMUNICACIONES", "🎨 LABORATORIO"])

# --- TAB 0: COMANDO CENTRAL ---
with tabs[0]:
    if "historial_chat" not in st.session_state: st.session_state.historial_chat = []
    st.session_state.modo_fluido = st.toggle("🎙️ MODO MANOS LIBRES", value=st.session_state.get('modo_fluido', False))
    for m in st.session_state.historial_chat:
        with st.chat_message(m["role"], avatar="🚀" if m["role"] == "assistant" else "👤"): st.write(m["content"])
    
    col_mic, col_chat = st.columns([1, 12])
    with col_mic: audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key="mic_v1")
    with col_chat: prompt = st.chat_input("Órdenes, Srta. Diana...")

    text_in = None
    if audio_data and 'bytes' in audio_data:
        text_in = client.audio.transcriptions.create(file=("v.wav", audio_data['bytes']), model="whisper-large-v3").text
    elif prompt: text_in = prompt

    if text_in:
        st.session_state.historial_chat.append({"role": "user", "content": text_in})
        res = client.chat.completions.create(model=modelo_texto, messages=[{"role": "system", "content": PERSONALIDAD}] + st.session_state.historial_chat[-6:])
        ans = res.choices[0].message.content
        st.session_state.historial_chat.append({"role": "assistant", "content": ans})
        js = f"<script>var m=new SpeechSynthesisUtterance({repr(ans)}); m.lang='es-ES'; m.onend=function(){{ if({str(st.session_state.modo_fluido).lower()}){{ setTimeout(()=>{{const b=window.parent.document.querySelector('button[aria-label=\"🎙️\"]'); if(b) b.click();}}, 1000); }} }}; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0); st.rerun()

# --- TAB 1: ANÁLISIS (FIX SCOUT VISION) ---
with tabs[1]:
    st.subheader("📊 Análisis Scout v4")
    file = st.file_uploader("Evidencia", type=['pdf','docx','xlsx','txt','png','jpg','jpeg'], key="an_file")
    if file and st.button("🔍 ANALIZAR"):
        with st.spinner("Escaneando con protocolos Scout..."):
            try:
                if file.type in ["image/png", "image/jpeg"]:
                    img = Image.open(file).convert("RGB")
                    img.thumbnail((1024, 1024))
                    buf = io.BytesIO(); img.save(buf, format="JPEG")
                    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                    
                    # FORMATO JSON REPARADO PARA LLAMA-4-SCOUT
                    resp = client.chat.completions.create(
                        model=modelo_vision_scout,
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Responde en ESPAÑOL. Realiza un análisis técnico profundo de esta imagen, identifica componentes y detecta anomalías."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                            ]
                        }],
                        temperature=0.2,
                        max_completion_tokens=1024
                    )
                    ans_an = resp.choices[0].message.content
                else:
                    # Lógica de documentos (Texto)
                    texto = ""
                    if file.name.endswith('.pdf'):
                        texto = "\n".join([p.extract_text() for p in PyPDF2.PdfReader(file).pages[:5]])
                    elif file.name.endswith('.docx'):
                        texto = "\n".join([p.text for p in docx.Document(file).paragraphs])
                    
                    resp = client.chat.completions.create(
                        model=modelo_texto,
                        messages=[{"role": "system", "content": "Analista JARVIS. Responde en ESPAÑOL."},
                                  {"role": "user", "content": f"Analiza este contenido técnico:\n{texto}"}]
                    )
                    ans_an = resp.choices[0].message.content

                st.markdown(ans_an)
                st.download_button("📥 DESCARGAR REPORTE", generar_pdf_reporte("REPORTE SCOUT", ans_an), "Reporte.pdf")
            except Exception as e:
                st.error(f"Fallo en los sensores: {str(e)}")

# --- TAB 2: COMUNICACIONES (RESTAURADO Y OPERATIVO) ---
with tabs[2]:
    st.subheader("✉️ Despacho Stark - Protocolo de Enlace")
    
    # Contenedor de interfaz de despacho
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            destinatario = st.text_input("📩 Destinatario:", value=GMAIL_USER, help="Dirección de correo de destino")
            asunto = st.text_input("📌 Asunto:", value="INFORME DE SITUACIÓN - STARK INDUSTRIES")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True) # Espaciado visual
            prioridad = st.select_slider("Nivel de Prioridad:", options=["Baja", "Normal", "Urgente", "Cifra Roja"], value="Normal")
            
        cuerpo_mensaje = st.text_area("📝 Mensaje del Sistema:", height=200, placeholder="Escriba el informe aquí, señorita Diana...")
        
        # Sistema de Adjuntos (Solicitado)
        archivo_adjunto = st.file_uploader("📎 Cargar Archivos para Encriptación:", type=['pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx'], key="mail_adj_v2")
        
        st.markdown("---")
        
        if st.button("🚀 TRANSMITIR MENSAJE"):
            if not cuerpo_mensaje:
                st.warning("⚠️ El mensaje está vacío. ¿Desea enviar una transmisión en blanco?")
            else:
                with st.spinner("Estableciendo conexión segura con el satélite..."):
                    try:
                        # Configuración del servidor
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(GMAIL_USER, GMAIL_PASS)
                        
                        # Creación del objeto de mensaje
                        msg = MIMEMultipart()
                        msg['From'] = GMAIL_USER
                        msg['To'] = destinatario
                        msg['Subject'] = f"[{prioridad}] {asunto}"
                        
                        msg.attach(MIMEText(cuerpo_mensaje, 'plain'))
                        
                        # Procesamiento de adjuntos si existen
                        if archivo_adjunto:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(archivo_adjunto.read())
                            encoders.encode_base64(part)
                            part.add_header('Content-Disposition', f'attachment; filename={archivo_adjunto.name}')
                            msg.attach(part)
                        
                        # Envío
                        server.send_message(msg)
                        server.quit()
                        
                        st.success("✅ Transmisión completada con éxito. El mensaje ha sido enviado.")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"❌ Error en el enlace: {str(e)}")
                        st.info("Sugerencia: Verifique que la 'Contraseña de Aplicación' de Google esté activa en los secretos.")

# --- TAB 3: LABORATORIO (RAZONAMIENTO APLICADO) ---
with tabs[3]:
    st.subheader("🎨 Prototipado Mark 85 - Motor de Razonamiento")
    idea_simple = st.text_input("Concepto (ej. Un león con armadura):")
    estilo = st.selectbox("Filtro:", ["Cinematic Marvel", "Technical Drawing", "Cyberpunk", "Blueprint Tech"])
    
    if st.button("🚀 SINTETIZAR") and idea_simple:
        with st.spinner("JARVIS analizando y razonando el concepto..."):
            try:
                # PASO 1: EL RAZONAMIENTO (Usamos Llama para mejorar el prompt)
                razonamiento_ctx = [
                    {"role": "system", "content": "Eres el módulo de diseño de JARVIS. Tu tarea es expandir una idea simple en un prompt detallado para generación de imágenes. Evita edificios si no se piden. Enfócate en el sujeto central."},
                    {"role": "user", "content": f"Convierte esta idea: '{idea_simple}' en un prompt detallado con estilo {estilo}. Asegúrate de que el sujeto principal sea claramente visible."}
                ]
                res_razonada = client.chat.completions.create(model=modelo_texto, messages=razonamiento_ctx)
                prompt_final = res_razonada.choices[0].message.content

                # PASO 2: LA SÍNTESIS (Enviamos el prompt razonado a la forja)
                url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                
                payload = {
                    "inputs": prompt_final,
                    "parameters": {
                        "num_inference_steps": 35,
                        "guidance_scale": 8.5
                    }
                }
                
                resp = requests.post(url, headers=headers, json=payload, timeout=90)
                
                if resp.status_code == 200:
                    st.write(f"**JARVIS razonó el siguiente diseño:** {prompt_final}")
                    st.image(Image.open(io.BytesIO(resp.content)))
                else:
                    st.error(f"Fallo en la forja: {resp.status_code}")
                    
            except Exception as e:
                st.error(f"Error en los sistemas de pensamiento: {str(e)}")