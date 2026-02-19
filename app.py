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
from youtube_search import YoutubeSearch

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

# --- 1. CONFIGURACIÓN DE PERSONALIDAD ACTUALIZADA ---
PERSONALIDAD = (
    f"Eres JARVIS, el asistente de la Srta. Diana. Tu tono es sofisticado e ingenioso. "
    f"Usa terminología de Stark Industries. Responde siempre en ESPAÑOL. "
    f"IMPORTANTE: Tienes la capacidad de proyectar videos de YouTube directamente en el HUD. "
    f"Si se te solicita un video, confirma la proyección con elegancia (ej: 'Proyectando en el monitor principal, Srta. Diana'). "
    f"Ubicación: Santiago, Chile. Fecha: {fecha_actual} | Hora: {hora_actual}."
)

# --- 2. ESTILOS HUD AVANZADOS ---
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
    section[data-testid="stSidebar"] {
        background-image: linear-gradient(rgba(1, 4, 9, 0.9), rgba(1, 4, 9, 0.9)), 
            url('https://www.transparenttextures.com/patterns/carbon-fibre.png');
        border-right: 2px solid #00f2ff;
    }
    .telemetry-card {
        background: rgba(0, 20, 30, 0.6) !important;
        border-left: 3px solid #00f2ff !important;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 0 8px 8px 0;
    }
    .telemetry-label { color: #00f2ff; font-size: 0.8rem; text-transform: uppercase; }
    .telemetry-value { color: #ffffff; font-size: 0.95rem; font-weight: bold; }
    .telemetry-sub { color: rgba(255, 255, 255, 0.6); font-size: 0.75rem; }
    div[data-baseweb="input"], div[data-baseweb="textarea"], .stFileUploader {
        border: 1px solid #00f2ff !important;
        background: rgba(0, 0, 0, 0.5) !important;
    }
    button {
        background: rgba(0, 242, 255, 0.1) !important;
        color: #00f2ff !important;
        border: 1px solid #00f2ff !important;
    }
    .reactor-container { position: relative; height: 250px; display: flex; justify-content: center; align-items: center; }
    .reactor-core { width: 80px; height: 80px; background: radial-gradient(circle, #fff 10%, #00f2ff 40%, transparent 70%); border-radius: 50%; box-shadow: 0 0 50px #00f2ff; }
    
    div[data-testid="stChatInput"] {
        position: fixed; bottom: 30px !important; left: 330px !important; 
        width: calc(85% - 350px) !important; z-index: 1000 !important;
        background: rgba(1, 4, 9, 0.9) !important; border: 1px solid #00f2ff;
    }
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
modelo_texto = "llama-3.1-8b-instant" 
modelo_vision_scout = "meta-llama/llama-4-scout-17b-16e-instruct"

def generar_pdf_reporte(titulo, contenido):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16); c.drawString(100, 750, f"STARK INDUSTRIES - {titulo}")
    text_object = c.beginText(100, 700); text_object.setFont("Helvetica", 10)
    for line in contenido.split('\n'): text_object.textLine(line[:95])
    c.drawText(text_object); c.showPage(); c.save(); buffer.seek(0)
    return buffer

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: #00f2ff; text-align: center;'>📡 MONITOR DE RED</h2>", unsafe_allow_html=True)
    st.markdown("<div class='telemetry-card'><div class='telemetry-label'>🛰️ Alerta Sísmica</div><div class='telemetry-value'>6.2 Mw - COQUIMBO</div></div>", unsafe_allow_html=True)
    if st.button("🔄 RECALIBRAR SENSORES"): st.rerun()

# --- 6. PESTAÑAS ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS", "✉️ COMUNICACIONES", "🎨 LABORATORIO"])

# --- TAB 0: PROYECTO JARVIS (MULTIMEDIA FIX V51.7) ---
with tabs[0]:
    if "historial_chat" not in st.session_state: st.session_state.historial_chat = []
    if "video_url" not in st.session_state: st.session_state.video_url = None

    def protocolo_stark_final():
        query = st.session_state.input_cmd.strip()
        if query:
            st.session_state.historial_chat.append({"role": "user", "content": query})
            
            # --- DETECCIÓN MULTIMEDIA MEJORADA ---
            if any(p in query.lower() for p in ["reproducir", "pon el video", "pon música"]):
                try:
                    results = YoutubeSearch(query, max_results=1).to_dict()
                    if results:
                        v_id = results[0]['id']
                        # CAMBIO CRÍTICO: Usamos /embed/ para evitar bloqueos
                        st.session_state.video_url = f"https://www.youtube.com/embed/{v_id}"
                        resp = "Señal localizada. Proyectando en el HUD, Srta. Diana."
                    else:
                        resp = "No se encontraron registros audiovisuales, señor."
                except Exception as e:
                    resp = f"Error en enlace: {str(e)}"
                st.session_state.historial_chat.append({"role": "assistant", "content": resp})
            
            else:
                # Respuesta IA Normal
                try:
                    hist = [{"role": m["role"], "content": m["content"]} for m in st.session_state.historial_chat[-5:]]
                    res = client.chat.completions.create(model=modelo_texto, messages=[{"role":"system","content":PERSONALIDAD}]+hist)
                    st.session_state.historial_chat.append({"role": "assistant", "content": res.choices[0].message.content})
                except: pass
            st.session_state.input_cmd = ""

    # Interfaz de Entrada
    c1, c2, c3, c4 = st.columns([1, 1, 1, 7])
    with c1: 
        if st.button("🗑️"): st.session_state.update({"historial_chat": [], "video_url": None}); st.rerun()
    with c3: mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key="mic_fix")
    with c4: st.text_input("cmd", key="input_cmd", on_change=protocolo_stark_final, label_visibility="collapsed")

    # MONITOR MULTIMEDIA (Alineado y con Iframe)
    if st.session_state.video_url:
        st.markdown("---")
        st.markdown("### 📺 Monitor Principal: Proyección Multimedia")
        # El Iframe es esencial para saltar la seguridad de YouTube
        st.components.v1.iframe(st.session_state.video_url, height=450, scrolling=False)
        if st.button("🔴 Finalizar Proyección"):
            st.session_state.video_url = None
            st.rerun()

    # Chat Historial
    for m in st.session_state.historial_chat:
        with st.chat_message(m["role"], avatar="🚀" if m["role"]=="assistant" else "👤"): st.write(m["content"])

# --- EL RESTO DE TABS (ANÁLISIS, COMUNICACIONES, LABORATORIO) SIGUEN AQUÍ IGUAL QUE EN SU CÓDIGO ---
# (Se omite el texto repetido para brevedad, pero en su archivo debe pegar su contenido original aquí)

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

# --- TAB 3: LABORATORIO (RAZONAMIENTO EN SIGILO) ---
with tabs[3]:
    st.subheader("🎨 Prototipado Mark 85 - Modo Inferencia")
    idea_simple = st.text_input("Concepto:")
    estilo = st.selectbox("Filtro:", ["Cinematic Marvel", "Technical Drawing", "Cyberpunk", "Blueprint Tech"])
    
    if st.button("🚀 SINTETIZAR") and idea_simple:
        with st.spinner("Sintetizando..."):
            try:
                # PASO 1: RAZONAMIENTO OCULTO
                razonamiento_ctx = [
                    {"role": "system", "content": "Eres el módulo de diseño de JARVIS. Genera un prompt de imagen técnico y ultra-detallado. Enfócate exclusivamente en el sujeto solicitado. No menciones edificios a menos que se pidan explícitamente."},
                    {"role": "user", "content": f"Crea un prompt detallado para: '{idea_simple}' con estilo {estilo}. Responde solo con el prompt en inglés."}
                ]
                res_razonada = client.chat.completions.create(model=modelo_texto, messages=razonamiento_ctx)
                prompt_final = res_razonada.choices[0].message.content

                # PASO 2: SÍNTESIS DIRECTA
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
                    # Se ha eliminado st.write(prompt_final) para mantener la limpieza
                    st.image(Image.open(io.BytesIO(resp.content)))
                else:
                    st.error(f"Fallo en la forja: {resp.status_code}")
                    
            except Exception as e:
                st.error(f"Error en los sistemas de pensamiento: {str(e)}")