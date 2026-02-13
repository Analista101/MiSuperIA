import streamlit as st
import pandas as pd
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
import base64
import io

# --- CONFIGURACIÓN DE SISTEMAS STARK ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

ID_DE_TU_HOJA = "1ch6QcydRrTJhIVmpHLNtP1Aq60bmaZibefV3IcBu90o"

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- MÓDULO DE BÚSQUEDA (CORREGIDO PARA 2026) ---
def buscar_internet(query):
    try:
        with DDGS() as ddgs:
            # Forzamos la búsqueda para que traiga datos de este año
            search_results = list(ddgs.text(f"{query} actual 2026", max_results=3))
            return "\n".join([r['body'] for r in search_results])
    except:
        return "No se pudo conectar con los satélites de búsqueda."

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

# --- INTERFAZ PRINCIPAL ---
st.title("🛰️ Proyecto JARVIS: Protocolo Diana")

tabs = st.tabs(["💬 Comando Central", "📊 Análisis Stark", "📸 Óptico", "🎨 Laboratorio"])

# --- PESTAÑA 1: CHAT + INTERNET ---
with tabs[0]:
    try:
        url_csv = f"https://docs.google.com/spreadsheets/d/{ID_DE_TU_HOJA}/export?format=csv"
        pd.read_csv(url_csv)
        st.success("🛰️ Enlace con Google Sheets: ESTABLE")
    except:
        st.warning("⚠️ Sensores de base de datos en modo local.")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("¿Qué desea, Srta. Diana?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("Consultando red global 2026..."):
            info_red = buscar_internet(prompt)
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            # System Prompt agresivo para forzar el año actual
            sys_msg = f"""Eres JARVIS. Estamos en FEBRERO DE 2026.
            Usa estos datos REALES para tu respuesta: {info_red}
            Si te preguntan por el clima o noticias, usa los datos de arriba.
            No digas que tu conocimiento es de 2023. Responde como un asistente británico."""

            response = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content

            with st.chat_message("assistant"):
                st.markdown(response)
                hablar(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# --- PESTAÑA 2: DATOS ---
with tabs[1]:
    st.header("📊 Procesamiento de Datos")
    archivo = st.file_uploader("Subir archivo Excel/CSV", type=['xlsx', 'csv'], key="stark_data")
    if archivo:
        df = pd.read_excel(archivo) if 'xlsx' in archivo.name else pd.read_csv(archivo)
        st.dataframe(df)

# --- PESTAÑA 3: FOTOS ---
with tabs[2]:
    st.header("📸 Reconocimiento Óptico")
    img_file = st.file_uploader("Sube una imagen", type=['jpg', 'png'], key="stark_vision")
    if img_file:
        img = Image.open(img_file)
        filtro = st.selectbox("Efecto:", ["Ninguno", "Gris", "Bordes"])
        if filtro == "Gris": img = ImageOps.grayscale(img)
        elif filtro == "Bordes": img = img.filter(ImageFilter.FIND_EDGES)
        st.image(img, use_container_width=True)

# --- PESTAÑA 4: ARTE ---
with tabs[3]:
    st.header("🎨 Laboratorio Artístico")
    desc = st.text_input("Describe tu diseño:", key="stark_art")
    if st.button("Generar Renderizado"):
        url_art = f"https://image.pollinations.ai/prompt/{desc.replace(' ', '%20')}?model=flux"
        st.image(url_art, caption="Visualización Stark")