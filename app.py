import streamlit as st
import pandas as pd
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
import base64
import io
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN DE LA TERMINAL ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# Inyección de CSS: Estética Stark y Reactor Arc Seguro
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #0a192f 0%, #020617 100%); color: #00f2ff; }
    .arc-container { display: flex; justify-content: center; padding: 20px; }
    .arc-reactor {
        width: 120px; height: 120px; border-radius: 50%;
        background: radial-gradient(circle, #fff 0%, #00f2ff 40%, transparent 70%);
        box-shadow: 0 0 50px #00f2ff, inset 0 0 25px #00f2ff;
        border: 4px solid #00f2ff;
        animation: pulse 2.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.05); opacity: 1; box-shadow: 0 0 70px #00f2ff; }
        100% { transform: scale(1); opacity: 0.8; }
    }
    .stTabs [data-baseweb="tab"] { color: #00f2ff !important; border: 1px solid #00f2ff; border-radius: 5px; margin: 5px; padding: 10px; }
    .stTabs [aria-selected="true"] { background-color: #00f2ff !important; color: black !important; box-shadow: 0 0 15px #00f2ff; }
    .stChatMessage { background-color: rgba(26, 28, 35, 0.9); border: 1px solid #00f2ff; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORES DE SISTEMA ---
def buscar_red_global(consulta):
    try:
        with DDGS() as ddgs:
            r = list(ddgs.text(f"{consulta} hoy 2026", max_results=3))
            return "\n".join([i['body'] for i in r]) if r else "SISTEMA_OFFLINE"
    except: return "SISTEMA_OFFLINE"

def enviar_correo_stark(destinatario, asunto, mensaje):
    remitente = st.secrets["EMAIL_USER"]
    password = st.secrets["EMAIL_PASS"] # Sincronizado con su captura
    try:
        msg = MIMEMultipart()
        msg['From'] = f"J.A.R.V.I.S. <{remitente}>"
        msg['To'] = destinatario
        msg['Subject'] = asunto
        msg.attach(MIMEText(mensaje, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error de transmisión: {str(e)}")
        return False

def hablar(texto):
    try:
        tts = gTTS(text=texto, lang='es', tld='es')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

# --- INTERFAZ PRINCIPAL ---
st.markdown("<h1 style='text-align: center;'>🛰️ PROTOCOLO: DIANA</h1>", unsafe_allow_html=True)
st.markdown('<div class="arc-container"><div class="arc-reactor"></div></div>', unsafe_allow_html=True)

tabs = st.tabs(["💬 COMANDO CENTRAL", "📊 ANÁLISIS OMNI", "📸 ÓPTICO", "📧 MENSAJERÍA"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Pestaña 0: JARVIS Chat
with tabs[0]:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Diga sus órdenes, Srta. Diana..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("Sincronizando con satélites Stark..."):
            datos = buscar_red_global(prompt)
            fecha = datetime.datetime.now().strftime("%d de febrero de 2026")
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            # Personalización de voz y comportamiento
            sys_msg = f"Eres JARVIS. Hoy es {fecha}. Datos: {datos}. Habla con elegancia británica, sé eficiente y llama a la usuaria 'Srta. Diana'."
            
            res = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content

            with st.chat_message("assistant"):
                st.markdown(res)
                hablar(res)
            st.session_state.messages.append({"role": "assistant", "content": res})

# Pestaña 1: Análisis Omni-Formato
with tabs[1]:
    st.header("📊 Procesamiento de Datos Multi-Sistema")
    f = st.file_uploader("Subir CSV, XLSX, JSON", type=['csv', 'xlsx', 'json'])
    if f:
        df = pd.read_csv(f) if 'csv' in f.name else pd.read_excel(f) if 'xlsx' in f.name else pd.read_json(f)
        st.dataframe(df, use_container_width=True)
        st.metric("Registros Analizados", len(df))

# Pestaña 3: Mensajería Directa (Nueva)
with tabs[3]:
    st.header("📧 Transmisor de Comunicaciones")
    dest = st.text_input("Destinatario:", value="sandoval0193@gmail.com")
    asunto = st.text_input("Asunto:", value="Recordatorio de Reunión")
    cuerpo = st.text_area("Mensaje:", value="Sr. Sandoval, por instrucción de la Srta. Diana, le recuerdo nuestra reunión programada para mañana.")
    
    if st.button("🚀 ENVIAR CORREO"):
        with st.spinner("Transmitiendo señal..."):
            if enviar_correo_stark(dest, asunto, cuerpo):
                st.success(f"Señal enviada con éxito a {dest}. Confirmación registrada.")
                hablar("El mensaje ha sido transmitido con éxito, Srta. Diana.")