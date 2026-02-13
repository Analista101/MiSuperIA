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

# --- CONFIGURACIÓN DE SISTEMAS ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide")

# ID de tu base de datos conectada
ID_DE_TU_HOJA = "1ch6QcydRrTJhIVmpHLNtP1Aq60bmaZibefV3IcBu90o"

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- MÓDULO 1: BÚSQUEDA SATELITAL (INTERNET) ---
def buscar_en_red(consulta):
    try:
        with DDGS() as ddgs:
            # Buscamos los 3 resultados más relevantes
            resultados = [r['body'] for r in ddgs.text(consulta, max_results=3)]
            return "\n".join(resultados)
    except Exception as e:
        return "Conexión limitada a los satélites externos."

# --- MÓDULO 2: MEMORIA EN LA NUBE ---
def conectar_google_sheets():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{ID_DE_TU_HOJA}"
        gc = gspread.public_open(url)
        return gc.get_worksheet(0)
    except:
        return None

# --- MÓDULO 3: PROTOCOLO DE VOZ ---
def hablar(texto):
    try:
        tts = gTTS(text=texto, lang='es')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(md, unsafe_allow_html=True)
    except:
        pass

# --- INTERFAZ PRINCIPAL ---
st.title("🛰️ Proyecto JARVIS: Protocolo Diana")

tabs = st.tabs(["💬 Centro de Comando", "📊 Análisis", "📸 Óptico", "🎨 Laboratorio"])

with tabs[0]:
    hoja = conectar_google_sheets()
    if hoja: st.success("🛰️ Memoria Global: CONECTADA")
    else: st.warning("⚠️ Base de datos fuera de línea.")

    # Mostrar historial de la sesión
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # Entrada de comando
    if prompt := st.chat_input("Sistemas listos. ¿Qué desea, Srta. Diana?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("Procesando datos en tiempo real..."):
            # Lógica de detección de búsqueda (Internet)
            contexto_web = ""
            palabras_red = ["clima", "tiempo", "noticias", "hoy", "precio", "dólar", "bitcoin"]
            
            if any(p in prompt.lower() for p in palabras_red):
                contexto_web = f"\nInformación obtenida de la red: {buscar_en_red(prompt)}"

            # Llamada a la IA (Groq)
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            sys_msg = f"Eres JARVIS. Sofisticado, británico y eficiente. Responde con elegancia. Datos actuales: {contexto_web}"
            
            mensajes_completos = [{"role": "system", "content": sys_msg}] + st.session_state.messages
            
            response = client.chat.completions.create(
                messages=mensajes_completos,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content

            # Respuesta visual y sonora
            with st.chat_message("assistant"):
                st.markdown(response)
                hablar(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Guardar en Google Sheets
            if hoja:
                try:
                    hoja.append_row([prompt, response])
                    st.toast("✅ Memoria sincronizada")
                except: pass

# --- (Las pestañas de Datos, Óptico y Laboratorio se mantienen íntegras) ---