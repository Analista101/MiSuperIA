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

# --- 2. PROTOCOLOS DE SOPORTE (PDF Y CORREO) ---
def generar_pdf_reporte(titulo, contenido):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "STARK INDUSTRIES - REPORTE DE INTELIGENCIA")
    c.setFont("Helvetica", 10)
    c.drawString(100, 735, f"Fecha: {fecha_actual} | Hora: {hora_actual}")
    c.line(100, 725, 500, 725)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 700, f"Asunto: {titulo}")
    text_object = c.beginText(100, 675)
    text_object.setFont("Helvetica", 10)
    lines = contenido.split('\n')
    for line in lines:
        if text_object.getY() < 50:
            c.drawText(text_object)
            c.showPage()
            text_object = c.beginText(100, 750)
            text_object.setFont("Helvetica", 10)
        text_object.textLine(line[:95])
    c.drawText(text_object)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def enviar_correo_stark(dest, asunto, cuerpo):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls(); server.login(GMAIL_USER, GMAIL_PASS)
        msg = MIMEMultipart(); msg['From'] = GMAIL_USER; msg['To'] = dest; msg['Subject'] = asunto
        msg.attach(MIMEText(cuerpo, 'plain'))
        server.send_message(msg); server.quit()
        return True
    except: return False

# --- 3. AUTENTICACIÓN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown('<div class="arc-reactor"></div>', unsafe_allow_html=True)
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

# --- 5. DISEÑO HUD ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at center, #0a192f 0%, #010409 100%) !important; color: #00f2ff !important; font-family: 'Courier New', monospace; }
    .arc-reactor { width: 80px; height: 80px; border-radius: 50%; margin: 10px auto; background: radial-gradient(circle, #fff 0%, #00f2ff 30%, transparent 70%); box-shadow: 0 0 30px #00f2ff; animation: pulse 2s infinite ease-in-out; }
    @keyframes pulse { 0% { transform: scale(1); opacity: 0.8; } 50% { transform: scale(1.05); opacity: 1; } 100% { transform: scale(1); opacity: 0.8; } }
    </style>
    <div class="arc-reactor"></div>
    <div style="text-align: center; color: #00f2ff; font-size: 10px; letter-spacing: 3px; margin-bottom: 20px;">SISTEMA JARVIS | PROTOCOLO DIANA STARK</div>
""", unsafe_allow_html=True)

# --- 6. PESTAÑAS (MÓDULOS UNIFICADOS) ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS", "✉️ COMUNICACIONES", "🎨 LABORATORIO"])

# --- TAB 0: COMANDO CENTRAL (MARK 184 - VOZ Y ANTI-REPETICIÓN) ---
with tabs[0]:
    if "historial_chat" not in st.session_state: 
        st.session_state.historial_chat = []
    
    # Renderizado del historial en el HUD
    for m in st.session_state.historial_chat:
        avatar = "🚀" if m["role"] == "assistant" else "👤"
        with st.chat_message(m["role"], avatar=avatar):
            st.write(m["content"])

    col_mic, col_chat = st.columns([1, 12])
    with col_mic:
        # Grabación con clave única para evitar interferencias
        audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key="mic_v184")
    
    with col_chat:
        prompt = st.chat_input("Esperando órdenes, señorita...")

    texto_a_procesar = None

    # Protocolo Anti-Eco: Verificamos si es un audio nuevo
    if audio_data and 'bytes' in audio_data:
        audio_hash = hash(audio_data['bytes'])
        if "last_audio_hash" not in st.session_state or st.session_state.last_audio_hash != audio_hash:
            try:
                with st.spinner("Descifrando mensaje de voz..."):
                    trans = client.audio.transcriptions.create(
                        file=("voice.wav", audio_data['bytes']), 
                        model="whisper-large-v3", 
                        language="es"
                    )
                    texto_a_procesar = trans.text
                    st.session_state.last_audio_hash = audio_hash
            except Exception as e:
                st.error(f"Falla en enlace de voz: {e}")
    elif prompt:
        texto_a_procesar = prompt

    if texto_a_procesar:
        st.session_state.historial_chat.append({"role": "user", "content": texto_a_procesar})
        
        with st.spinner("Sintonizando respuesta..."):
            ctx = [{"role": "system", "content": PERSONALIDAD}] + st.session_state.historial_chat[-6:]
            res = client.chat.completions.create(model=modelo_texto, messages=ctx)
            ans = res.choices[0].message.content
            
            st.session_state.historial_chat.append({"role": "assistant", "content": ans})
            
            # --- PROTOCOLO DE VOZ JARVIS (SÍNTESIS NATIVA) ---
            js_speech = f"""
                <script>
                var msg = new SpeechSynthesisUtterance({repr(ans)});
                var voices = window.speechSynthesis.getVoices();
                
                // Buscamos una voz masculina sofisticada
                var seleccionada = voices.find(v => v.name.includes('Male') || v.name.includes('Jorge') || v.name.includes('Google español'));
                if(seleccionada) msg.voice = seleccionada;

                msg.lang = 'es-ES';
                msg.pitch = 0.85; // Tono grave
                msg.rate = 0.95;  // Velocidad calmada
                window.speechSynthesis.speak(msg);
                </script>
            """
            st.components.v1.html(js_speech, height=0)
            
            # Guardamos en memoria permanente si el sistema está conectado
            guardar_memoria_permanente(texto_a_procesar, ans)
            
            st.rerun()

# --- TAB 1: ANÁLISIS (SISTEMA DE RAZONAMIENTO PROFUNDO MARK 185) ---
with tabs[1]:
    st.subheader("📊 Centro de Inteligencia con Pensamiento Crítico")
    file = st.file_uploader("Cargar evidencia para análisis con Qwen-3 Reasoning", type=['pdf','docx','xlsx','png','jpg','jpeg'], key="scanner_v185")
    
    if file and st.button("🔍 INICIAR PROTOCOLO DE RAZONAMIENTO"):
        with st.spinner("JARVIS está reflexionando sobre los datos..."):
            try:
                res_content = ""
                thinking_process = ""
                title = "REPORTE DE INTELIGENCIA ESTRATÉGICA"

                # Prompt optimizado para modelos de razonamiento (Zero-Shot)
                PROMPT_REASONING = (
                    "Analiza este documento de manera exhaustiva para la Srta. Diana Stark. "
                    "Divide tu respuesta en: 1. Resumen de Alto Nivel, 2. Hallazgos Críticos, "
                    "3. Análisis de Riesgos y 4. Recomendaciones de Ingeniería/Negocio. "
                    "Sé extremadamente preciso y lógico."
                )

                # 1. Procesamiento de Texto (PDF/DOCX/EXCEL) usando Qwen-3 Reasoning
                if file.type in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
                    
                    if file.type == "application/pdf":
                        pdf = PyPDF2.PdfReader(file); txt = "".join([p.extract_text() for p in pdf.pages])
                    elif file.type == "application/xlsx":
                        df = pd.read_excel(file); txt = df.to_string()
                    else:
                        doc = docx.Document(file); txt = "\n".join([p.text for p in doc.paragraphs])

                    # LLAMADA AL MODELO DE RAZONAMIENTO
                    response = client.chat.completions.create(
                        model="qwen/qwen3-32b", # El nuevo núcleo de razonamiento
                        messages=[{"role": "user", "content": f"{PROMPT_REASONING}\n\nContenido:\n{txt[:8000]}"}],
                        reasoning_format="raw" # Esto nos permite extraer el bloque <think>
                    )
                    
                    full_res = response.choices[0].message.content
                    
                    # Separar el pensamiento de la respuesta
                    if "<think>" in full_res and "</think>" in full_res:
                        thinking_process = full_res.split("<think>")[1].split("</think>")[0]
                        res_content = full_res.split("</think>")[1]
                    else:
                        res_content = full_res

                # 2. Procesamiento de Imágenes (Mantenemos Llama-4 Scout por su visión superior)
                elif file.type.startswith('image/'):
                    img = Image.open(file).convert("RGB")
                    st.image(img, width=500)
                    buf = io.BytesIO(); img.save(buf, format="JPEG"); b64 = base64.b64encode(buf.getvalue()).decode()
                    
                    res = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[{"role": "user", "content": [{"type": "text", "text": PROMPT_REASONING}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}]
                    )
                    res_content = res.choices[0].message.content

                # UI de Resultados
                if thinking_process:
                    with st.expander("🧠 VER PROCESO DE RAZONAMIENTO DE JARVIS"):
                        st.info(thinking_process)

                if res_content:
                    st.markdown("---")
                    st.markdown(res_content)
                    
                    # Generar PDF
                    pdf_file = generar_pdf_reporte(title, res_content)
                    st.download_button("📥 DESCARGAR REPORTE ESTRATÉGICO", pdf_file, f"Stark_Intelligence_{hora_actual}.pdf", "application/pdf")

            except Exception as e:
                st.error(f"Error en los servidores de razonamiento: {e}")
                
# --- TAB 2: COMUNICACIONES ---
with tabs[2]:
    st.subheader("✉️ Centro de Despacho Gmail")
    c1, c2 = st.columns(2)
    with c1: dest = st.text_input("Para:", value=GMAIL_USER)
    with c2: asun = st.text_input("Asunto:", value="Reporte Stark")
    cuer = st.text_area("Mensaje:")
    if st.button("🚀 ENVIAR CORREO"):
        if enviar_correo_stark(dest, asun, cuer): st.success("Mensaje enviado con éxito, señorita.")
        else: st.error("Error en servidor SMTP.")

# --- TAB 3: LABORATORIO ---
with tabs[3]:
    st.subheader("🎨 Estación Mark 85")
    col_p, col_f = st.columns([2, 1])
    with col_p: idea = st.text_input("Prototipo:", key="lab_v181")
    with col_f: 
        estilo = st.selectbox("Filtro:", ["Cinematic Marvel", "Technical Drawing", "Cyberpunk", "Industrial Stark"])
    if st.button("🚀 SINTETIZAR") and idea:
        with st.spinner("Sintetizando..."):
            url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
            resp = requests.post(url, headers={"Authorization": f"Bearer {HF_TOKEN}"}, json={"inputs": f"{idea}, {estilo} style"})
            if resp.status_code == 200: st.image(Image.open(io.BytesIO(resp.content)))
            else: st.error("Error en sintetizador.")