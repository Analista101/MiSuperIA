import streamlit as st
import pandas as pd
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
import gspread
from google.oauth2.service_account import Credentials
import base64
import io
import PyPDF2

st.set_page_config(page_title="JARVIS: Protocolo Diana Total", layout="wide")

# --- 🔑 CONFIGURACIÓN DE SEGURIDAD Y GOOGLE SHEETS ---
# SUSTITUYE ESTO POR EL ID DE TU HOJA (ESTÁ EN LA URL)
ID_DE_TU_HOJA = "TU_ID_AQUI"

def conectar_google_sheets():
    try:
        # Usamos las credenciales que subiremos a st.secrets o un archivo json
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Para esta versión rápida, asumimos que compartiste la hoja como "Editor" con "Cualquier persona con el enlace"
        gc = gspread.public_open(f"https://docs.google.com/spreadsheets/d/{ID_DE_TU_HOJA}")
        return gc.get_worksheet(0)
    except:
        return None

# --- PROTOCOLO DE MEMORIA (EVITA ERRORES) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

api_key_groq = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else ""

# --- FUNCIONES MAESTRAS ---
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

def buscar_web(query):
    try:
        with DDGS() as ddgs:
            resultados = [r['body'] for r in ddgs.text(query, max_results=2)]
            return " ".join(resultados)
    except: return "Acceso a red limitado."

st.title("🛰️ Proyecto JARVIS: Protocolo Diana")

tab1, tab2, tab3, tab4 = st.tabs(["💬 Centro de Comando", "📊 Análisis de Datos", "📸 Editor Óptico", "🎨 Laboratorio Artístico"])

# --- PESTAÑA 1: CHAT + MEMORIA EN GOOGLE SHEETS ---
with tab1:
    st.subheader("🎙️ Interfaz de Voz y Memoria en la Nube")
    hoja = conectar_google_sheets()
    
    if hoja: st.success("🛰️ Conexión con Google Sheets: ESTABLE")
    else: st.warning("⚠️ No se detectó la base de datos. Verifique los permisos de compartir.")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Diga algo, Srta. Diana..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("Analizando sistemas..."):
            client = Groq(api_key=api_key_groq)
            sys_msg = "Eres JARVIS. Sofisticado, británico y eficiente. Responde siempre con elegancia."
            
            mensajes_completos = [{"role": "system", "content": sys_msg}] + st.session_state.messages
            response = client.chat.completions.create(messages=mensajes_completos, model="llama-3.3-70b-versatile").choices[0].message.content

            with st.chat_message("assistant"): 
                st.markdown(response)
                hablar(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})

            # ¡AQUÍ ESTÁ TU CÓDIGO DE GOOGLE SHEETS!
            if hoja:
                try:
                    nueva_fila = [prompt, response] # Columna A: Usuario, Columna B: JARVIS
                    hoja.append_row(nueva_fila) 
                    st.toast("✅ Memoria guardada en la nube")
                except:
                    st.error("Error al escribir en la nube.")

# --- (El resto de pestañas de Excel, Editor y Artista se mantienen igual que antes) ---