import streamlit as st
import os
import io, base64, requests
import datetime, pytz
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
    f"Eres JARVIS, el asistente de la Srta. Diana. Tu tono es sofisticado, ingenioso y servicial. "
    f"Usa terminología de Stark Industries. Ubicación: Santiago, Chile. "
    f"Fecha: {fecha_actual} | Hora: {hora_actual}."
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
    button, div.stButton > button {
        background: rgba(0, 242, 255, 0.05) !important;
        color: #00f2ff !important;
        border: 1px solid #00f2ff !important;
        box-shadow: 0 0 8px rgba(0, 242, 255, 0.3) !important;
    }
    button[aria-label="🎙️"], button[aria-label="🛑"] {
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
    }
    .reactor-container { position: relative; height: 180px; display: flex; justify-content: center; align-items: center; }
    .reactor-core { 
        width: 60px; height: 60px; background: radial-gradient(circle, #fff 5%, #00f2ff 50%, transparent 80%); 
        border-radius: 50%; box-shadow: 0 0 50px #00f2ff;
        animation: pulse-breathe 2.5s infinite alternate ease-in-out; 
    }
    @keyframes pulse-breathe { 0% { transform: scale(1); opacity: 0.7; } 100% { transform: scale(1.1); opacity: 1; } }
    </style>
    <div class="reactor-container"><div class="reactor-core"></div></div>
""", unsafe_allow_html=True)

# --- 3. AUTENTICACIÓN ---
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='color:#00f2ff; text-align:center;'>🔐 ACCESO RESTRINGIDO</h2>", unsafe_allow_html=True)
        pass_in = st.text_input("Código Stark:", type="password")
        if st.button("DESBLOQUEAR"):
            if pass_in == ACCESS_PASSWORD:
                st.session_state["autenticado"] = True
                st.rerun()
    st.stop()

# --- 4. INICIALIZACIÓN IA ---
client = Groq(api_key=GROQ_API_KEY)
modelo_texto = "llama-3.3-70b-versatile"

def generar_pdf_reporte(titulo, contenido):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, f"STARK INDUSTRIES - {titulo}")
    text_object = c.beginText(100, 700)
    text_object.setFont("Helvetica", 10)
    for line in contenido.split('\n'): text_object.textLine(line[:95])
    c.drawText(text_object); c.showPage(); c.save(); buffer.seek(0)
    return buffer

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2ff;'>🛡️ E.S.T.A.D.O.</h2>", unsafe_allow_html=True)
    st.info(f"📅 {fecha_actual}\n⏰ {hora_actual}")
    if st.button("🔄 REINICIAR"):
        st.session_state.historial_chat = []
        st.rerun()

# --- 6. PESTAÑAS ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS", "✉️ DESPACHO", "🎨 LABORATORIO"])

# --- TAB 0: COMANDO CENTRAL (CONSOLIDADO) ---
with tabs[0]:
    if "historial_chat" not in st.session_state: st.session_state.historial_chat = []
    if "modo_fluido" not in st.session_state: st.session_state.modo_fluido = False
    
    st.session_state.modo_fluido = st.toggle("🎙️ MODO MANOS LIBRES", value=st.session_state.modo_fluido)
    
    for m in st.session_state.historial_chat:
        with st.chat_message(m["role"], avatar="🚀" if m["role"] == "assistant" else "👤"):
            st.markdown(m["content"])
            if "youtube.com" in m["content"] or "youtu.be" in m["content"]:
                # Extraer link si hay texto extra
                st.video(m["content"].split()[-1])

    col_mic, col_chat = st.columns([1, 10])
    with col_mic: audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="🛑", key="jarvis_mic")
    with col_chat: prompt = st.chat_input("Órdenes, Srta. Diana...")

    texto_final = None
    if audio_data and 'bytes' in audio_data:
        trans = client.audio.transcriptions.create(file=("v.wav", audio_data['bytes']), model="whisper-large-v3", language="es")
        texto_final = trans.text
    elif prompt: texto_final = prompt

    if texto_final:
        st.session_state.historial_chat.append({"role": "user", "content": texto_final})
        
        # Lógica de Video Directo
        if "reproduce" in texto_final.lower() and "python" in texto_final.lower():
            ans = "Desplegando tutorial de Python, señorita. Iniciando protocolos de aprendizaje."
            ans += "\n\nhttps://www.youtube.com/watch?v=nKPbfIU442g"
        else:
            ctx = [{"role": "system", "content": PERSONALIDAD}] + st.session_state.historial_chat[-6:]
            res = client.chat.completions.create(model=modelo_texto, messages=ctx)
            ans = res.choices[0].message.content
        
        st.session_state.historial_chat.append({"role": "assistant", "content": ans})
        
        js_speech = f"""
            <script>
            var msg = new SpeechSynthesisUtterance({repr(ans)});
            msg.lang = 'es-ES';
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

# --- TAB 1: ANÁLISIS ---
with tabs[1]:
    st.subheader("📊 Módulo de Análisis")
    archivo = st.file_uploader("Evidencia", type=['pdf','png','jpg'])
    if archivo and st.button("🔍 ANALIZAR"):
        with st.spinner("Escaneando..."):
            if archivo.type in ["image/png", "image/jpeg"]:
                b64 = base64.b64encode(archivo.read()).decode('utf-8')
                resp = client.chat.completions.create(model="llama-3.2-11b-vision-preview", messages=[{"role": "user", "content": [{"type": "text", "text": "Analiza técnicamente en español."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}])
                analisis = resp.choices[0].message.content
            else: analisis = "Documento procesado correctamente."
            st.markdown(analisis)
            st.download_button("📥 REPORTE", generar_pdf_reporte("ANÁLISIS", analisis), "Reporte.pdf")

# --- TAB 2: COMUNICACIONES ---
with tabs[2]:
    st.subheader("✉️ Despacho Stark")
    dest = st.text_input("Para:", value="diana@stark.com")
    asunto = st.text_input("Asunto:", value="INFORME")
    cuerpo = st.text_area("Mensaje:")
    if st.button("🚀 ENVIAR"):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587); server.starttls(); server.login(GMAIL_USER, GMAIL_PASS)
            msg = MIMEMultipart(); msg['From'], msg['To'], msg['Subject'] = GMAIL_USER, dest, asunto
            msg.attach(MIMEText(cuerpo, 'plain'))
            server.send_message(msg); server.quit(); st.success("Enviado.")
        except Exception as e: st.error(f"Error: {e}")

# --- TAB 3: LABORATORIO ---
with tabs[3]:
    st.subheader("🎨 Forja Mark 85")
    idea = st.text_input("Concepto:")
    if st.button("🔥 SINTETIZAR") and idea:
        with st.spinner("Sintetizando..."):
            API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            res = requests.post(API_URL, headers=headers, json={"inputs": f"{idea}, cinematic marvel style"})
            if res.status_code == 200: st.image(Image.open(io.BytesIO(res.content)))
            else: st.error("Error en la forja.")