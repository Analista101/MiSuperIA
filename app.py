import streamlit as st
import pandas as pd
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
import gspread
import base64
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="JARVIS: Protocolo Diana Total", layout="wide")

# ID de tu hoja conectada
ID_DE_TU_HOJA = "1ch6QcydRrTJhIVmpHLNtP1Aq60bmaZibefV3IcBu90o"

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- FUNCIONES DE SISTEMA ---
def conectar_google_sheets():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{ID_DE_TU_HOJA}"
        gc = gspread.public_open(url)
        return gc.get_worksheet(0)
    except: return None

def hablar(texto):
    try:
        tts = gTTS(text=texto, lang='es')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(md, unsafe_allow_html=True)
    except: pass

def enviar_correo_stark(destinatario, asunto, mensaje):
    remitente = st.secrets["EMAIL_USER"] # Configura esto en Secrets
    password = st.secrets["EMAIL_PASS"] # Configura esto en Secrets
    try:
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = asunto
        msg.attach(MIMEText(mensaje, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return "Mensaje enviado, Srta. Diana."
    except Exception as e:
        return f"Fallo en la conexión: {e}"

# --- INTERFAZ ---
st.title("🛰️ Proyecto JARVIS: Protocolo Diana")

tabs = st.tabs(["💬 Comando & Email", "📊 Datos", "📸 Óptico", "🎨 Laboratorio"])

with tabs[0]:
    hoja = conectar_google_sheets()
    if hoja: st.success("🛰️ Memoria en la Nube: CONECTADA")
    
    # Módulo de Email
    with st.expander("✉️ Redactar Correo Oficial"):
        c1, c2 = st.columns(2)
        dest = c1.text_input("Destinatario:")
        asu = c2.text_input("Asunto:")
        cuerpo = st.text_area("Contenido del mensaje:")
        if st.button("🚀 Transmitir Correo"):
            res = enviar_correo_stark(dest, asu, cuerpo)
            st.info(res)
            hablar(res)

    st.divider()
    # Chat
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Diga algo, Srta. Diana..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            messages=[{"role": "system", "content": "Eres JARVIS, sofisticado y eficiente."}] + st.session_state.messages,
            model="llama-3.3-70b-versatile"
        ).choices[0].message.content

        with st.chat_message("assistant"):
            st.markdown(response)
            hablar(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        if hoja: hoja.append_row([prompt, response]) # Guarda en Google Sheets

# (Las pestañas de Datos, Óptico y Laboratorio siguen funcionando igual)