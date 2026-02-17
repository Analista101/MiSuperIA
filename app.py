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
st.set_page_config(
    page_title="JARVIS - STARK INDUSTRIES", 
    page_icon="https://img.icons8.com/neon/256/iron-man.png", 
    layout="wide"
)

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

PERSONALIDAD = f"Eres JARVIS, el asistente de la Srta. Diana. Tono sofisticado. Santiago, Chile. {fecha_actual}."

# --- 2. ESTILOS VISUALES STARK (MAPA MUNDIAL Y NEÓN) ---
st.markdown("""
    <style>
    /* Fondo con Mapa Mundial Táctico */
    .stApp { 
        background-color: #010409 !important; 
        background-image: 
            radial-gradient(circle at 50% 50%, rgba(0, 242, 255, 0.1) 0%, transparent 80%),
            url('https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?q=80&w=2000&auto=format&fit=crop'); /* Mapa mundial estilizado */
        background-size: cover !important;
        background-attachment: fixed;
    }
    
    /* Detalles Neón y Botones */
    button, div.stButton > button, div.stDownloadButton > button { 
        background: rgba(0, 242, 255, 0.05) !important; 
        color: #00f2ff !important; 
        border: 1px solid #00f2ff !important; 
        text-transform: uppercase; 
        letter-spacing: 2px;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.2) !important;
    }
    
    /* Reactor Ark Palpitante */
    .reactor-container { 
        position: relative; 
        height: 200px; 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        margin-bottom: 20px;
    }
    .reactor-core { 
        width: 70px; 
        height: 70px; 
        background: radial-gradient(circle, #fff 5%, #00f2ff 50%, transparent 80%); 
        border-radius: 50%; 
        box-shadow: 0 0 60px #00f2ff, inset 0 0 20px #00f2ff; 
        animation: pulse 2s infinite alternate ease-in-out; 
    }
    @keyframes pulse { 
        from { transform: scale(0.9); opacity: 0.7; box-shadow: 0 0 30px #00f2ff; } 
        to { transform: scale(1.1); opacity: 1; box-shadow: 0 0 70px #00f2ff; } 
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
        pass_in = st.text_input("Código Stark:", type="password")
        if st.button("DESBLOQUEAR SISTEMA"):
            if pass_in == ACCESS_PASSWORD: st.session_state["autenticado"] = True; st.rerun()
    st.stop()

# --- 4. MODELOS ---
client = Groq(api_key=GROQ_API_KEY)
MODELO_CHAT = "llama-3.3-70b-versatile"
MODELO_VISION_SCOUT = "meta-llama/llama-4-scout-17b-16e-instruct"

def generar_pdf_reporte(titulo, contenido):
    buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=letter)
    c.setFont("Helvetica-Bold", 16); c.setStrokeColor("#00f2ff"); c.drawString(100, 750, f"STARK INDUSTRIES - {titulo}")
    tx = c.beginText(100, 680); tx.setFont("Helvetica", 10)
    for line in contenido.split('\n'): tx.textLine(line[:90])
    c.drawText(tx); c.showPage(); c.save(); buf.seek(0); return buf

# --- 5. SIDEBAR (HUD) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2ff; text-align:center;'>🛡️ E.S.T.A.D.O.</h2>", unsafe_allow_html=True)
    st.info(f"📅 **FECHA**: {fecha_actual}\n⏰ **HORA**: {hora_actual}")
    st.divider()
    st.subheader("🌐 Escaneo Ambiental")
    st.write("🌦️ **Clima**: Santiago - Despejado (32°C)")
    st.warning("⚠️ **Sismicidad**: Estable.")
    st.error("🔥 **Incendios**: Alerta roja activa.")
    if st.button("🔄 REINICIAR SISTEMAS"):
        st.session_state.historial_chat = []; st.rerun()

# --- 6. PESTAÑAS ---
tabs = st.tabs(["🗨️ COMANDO CENTRAL", "📊 ANÁLISIS SCOUT", "✉️ DESPACHO", "🎨 LABORATORIO"])

with tabs[0]:
    if "historial_chat" not in st.session_state: st.session_state.historial_chat = []
    if "modo_fluido" not in st.session_state: st.session_state.modo_fluido = False
    st.session_state.modo_fluido = st.toggle("🎙️ MODO MANOS LIBRES", value=st.session_state.modo_fluido)
    
    for m in st.session_state.historial_chat:
        with st.chat_message(m["role"], avatar="🚀" if m["role"] == "assistant" else "👤"):
            st.markdown(m["content"])
            if "youtube.com" in m["content"] or "youtu.be" in m["content"]:
                st.video(m["content"].split()[-1])

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
        ctx = [{"role": "system", "content": PERSONALIDAD}] + st.session_state.historial_chat[-5:]
        res = client.chat.completions.create(model=MODELO_CHAT, messages=ctx)
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

with tabs[1]:
    st.subheader("📊 Módulo de Inteligencia Llama-4-Scout")
    f = st.file_uploader("Cargar evidencia (PDF, Imagen, Excel)", type=['pdf','docx','png','jpg','xlsx'])
    if f and st.button("🔍 INICIAR ESCANEO EXHAUSTIVO"):
        with st.spinner("Sincronizando con Scout..."):
            try:
                if f.type in ["image/png", "image/jpeg"]:
                    img = Image.open(f)
                    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                    img.thumbnail((1024, 1024)); buf = io.BytesIO(); img.save(buf, format="JPEG")
                    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                    res = client.chat.completions.create(model=MODELO_VISION_SCOUT, messages=[{"role": "user", "content": [{"type": "text", "text": "Análisis técnico de la imagen."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}])
                    out = res.choices[0].message.content
                elif f.name.endswith('.xlsx'):
                    df = pd.read_excel(f)
                    out = f"Análisis de {len(df)} registros.\n{df.describe(include='all').to_string()}"
                elif f.name.endswith('.pdf'):
                    reader = PyPDF2.PdfReader(f)
                    texto = "".join([p.extract_text() for p in reader.pages[:5]])
                    res = client.chat.completions.create(model=MODELO_CHAT, messages=[{"role": "user", "content": f"Analiza este PDF: {texto}"}])
                    out = res.choices[0].message.content
                else: out = "Procesamiento completado."
                st.markdown(out)
                st.download_button("📥 REPORTE STARK", generar_pdf_reporte("ANÁLISIS SCOUT", out), "Reporte.pdf")
            except Exception as e: st.error(f"Fallo en sensor: {e}")

with tabs[2]:
    st.subheader("✉️ Despacho de Comunicaciones")
    dest = st.text_input("Para:", value=GMAIL_USER)
    asunto = st.text_input("Asunto:", value="REPORTE")
    cuerpo = st.text_area("Mensaje")
    f_adj = st.file_uploader("📎 Adjuntar archivo técnico", key="mail_adj")
    if st.button("🚀 ENVIAR"):
        try:
            srv = smtplib.SMTP('smtp.gmail.com', 587); srv.starttls(); srv.login(GMAIL_USER, GMAIL_PASS)
            msg = MIMEMultipart(); msg['From'], msg['To'], msg['Subject'] = GMAIL_USER, dest, asunto
            msg.attach(MIMEText(cuerpo, 'plain'))
            if f_adj:
                p = MIMEBase('application', 'octet-stream'); p.set_payload(f_adj.read()); encoders.encode_base64(p)
                p.add_header('Content-Disposition', f'attachment; filename={f_adj.name}'); msg.attach(p)
            srv.send_message(msg); srv.quit(); st.success("Enviado.")
        except Exception as e: st.error(f"Fallo: {e}")

with tabs[3]:
    st.subheader("🎨 Laboratorio de Prototipos")
    idea = st.text_input("Concepto:"); estilo = st.selectbox("Filtro:", ["Cinematic Marvel", "Digital Blueprint", "Cyberpunk", "Photorealistic"])
    if st.button("🔥 GENERAR") and idea:
        with st.spinner("Sintetizando..."):
            r = requests.post("https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0", headers={"Authorization": f"Bearer {HF_TOKEN}"}, json={"inputs": f"{idea}, {estilo} style"})
            if r.status_code == 200: st.image(Image.open(io.BytesIO(r.content)))
            else: st.error("Forja no disponible.")