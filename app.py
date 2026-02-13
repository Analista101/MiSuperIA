import streamlit as st
import pandas as pd
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
import base64
import io

# --- CONFIGURACIÓN DE SISTEMAS ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# ID de su hoja (Solo para lectura por ahora para evitar errores)
ID_DE_TU_HOJA = "1ch6QcydRrTJhIVmpHLNtP1Aq60bmaZibefV3IcBu90o"

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- MÓDULO DE BÚSQUEDA (FORZADO) ---
def buscar_internet(query):
    try:
        with DDGS() as ddgs:
            # Forzamos una búsqueda amplia para obtener datos reales de 2026
            search_results = list(ddgs.text(f"{query} hoy 2026", max_results=5))
            return "\n".join([r['body'] for r in search_results])
    except Exception as e:
        return f"Error de conexión satelital: {e}"

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

# --- INTERFAZ ---
st.title("🛰️ Proyecto JARVIS: Protocolo Diana")

# Intentar conectar a la base de datos (Modo estable)
try:
    url_csv = f"https://docs.google.com/spreadsheets/d/{ID_DE_TU_HOJA}/export?format=csv"
    pd.read_csv(url_csv)
    st.success("🛰️ Conexión de lectura: ESTABLE")
except:
    st.warning("⚠️ Sensores de base de datos en modo local.")

# Chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("¿Qué desea consultar, Srta. Diana?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.spinner("Accediendo a la red global..."):
        # PASO CRUCIAL: Buscamos SIEMPRE en internet para asegurar frescura
        info_actual = buscar_internet(prompt)
        
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        # System Prompt con esteroides para evitar que use datos viejos
        sys_msg = f"""Eres JARVIS. Estamos en FEBRERO DE 2026.
        Tu conocimiento interno es antiguo, por lo que DEBES usar exclusivamente 
        la siguiente información actual para responder a la Srta. Diana:
        
        {info_actual}
        
        Si la información de arriba no contiene la respuesta, utiliza tu capacidad 
        de análisis para razonar con la fecha actual (2026). Responde con elegancia."""

        try:
            response = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content

            with st.chat_message("assistant"):
                st.markdown(response)
                hablar(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error en el procesador Groq: {e}")