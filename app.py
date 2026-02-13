import streamlit as st
import pandas as pd
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
import gspread
import base64
import io

# --- CONFIGURACIÓN DE SISTEMAS STARK ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# ID de tu base de datos (Verificado)
ID_DE_TU_HOJA = "1ch6QcydRrTJhIVmpHLNtP1Aq60bmaZibefV3IcBu90o"

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- MÓDULO 1: BÚSQUEDA SATELITAL (INTERNET EN TIEMPO REAL) ---
def buscar_en_red(consulta):
    try:
        with DDGS() as ddgs:
            # Buscamos los resultados más recientes para evitar datos de 2023
            resultados = [r['body'] for r in ddgs.text(consulta, max_results=3)]
            return "\n".join(resultados)
    except Exception as e:
        return f"Error en sensores de red: {e}"

# --- MÓDULO 2: CONEXIÓN A BASE DE DATOS (CORREGIDO) ---
def conectar_google_sheets():
    try:
        # Usamos pandas para una lectura rápida y compatible
        url_csv = f"https://docs.google.com/spreadsheets/d/{ID_DE_TU_HOJA}/export?format=csv"
        df = pd.read_csv(url_csv)
        return df
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

# --- INTERFAZ DE USUARIO ---
st.title("🛰️ Proyecto JARVIS: Protocolo Diana")

tabs = st.tabs(["💬 Comando Central", "📊 Análisis Stark", "📸 Óptico", "🎨 Laboratorio"])

with tabs[0]:
    # Verificar conexión
    db = conectar_google_sheets()
    if db is not None:
        st.success("🛰️ Enlace con Google Sheets: ESTABLE")
    else:
        st.warning("⚠️ Sensores de base de datos en modo lectura limitada.")

    # Mostrar historial
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Entrada de comandos
    if prompt := st.chat_input("Sistemas listos. ¿Qué desea, Srta. Diana?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Consultando satélites y procesando..."):
            # Obligar a JARVIS a buscar en internet para temas actuales
            contexto_web = ""
            palabras_clave = ["clima", "tiempo", "noticias", "hoy", "precio", "bitcoin", "dólar"]
            
            if any(p in prompt.lower() for p in palabras_clave):
                contexto_web = buscar_en_red(prompt)

            # Configuración de la IA con fecha actualizada de 2026
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            # El System Prompt es la clave para que no use datos de 2023
            sys_msg = f"""Eres JARVIS, el asistente personal de la Srta. Diana. 
            Estamos en el año 2026. Tu base de datos interna está desactualizada, 
            por lo que DEBES confiar en estos datos de búsqueda para responder:
            {contexto_web}
            
            Responde con el estilo de JARVIS: educado, eficiente y británico."""

            mensajes_completos = [{"role": "system", "content": sys_msg}] + st.session_state.messages
            
            completion = client.chat.completions.create(
                messages=mensajes_completos,
                model="llama-3.3-70b-versatile"
            )
            
            response = completion.choices[0].message.content

            with st.chat_message("assistant"):
                st.markdown(response)
                hablar(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})

# --- LAS DEMÁS PESTAÑAS (ANÁLISIS, ÓPTICO, LABORATORIO) ---
with tabs[1]:
    st.header("📊 Procesamiento de Datos")
    archivo = st.file_uploader("Subir archivo Excel/CSV", type=['xlsx', 'csv'])
    if archivo:
        df_subido = pd.read_excel(archivo) if 'xlsx' in archivo.name else pd.read_csv(archivo)
        st.dataframe(df_subido)

with tabs[2]:
    st.header("📸 Reconocimiento Óptico")
    img_file = st.file_uploader("Sube una imagen", type=['jpg', 'png'])
    if img_file:
        img = Image.open(img_file)
        filtro = st.selectbox("Efecto:", ["Ninguno", "Gris", "Bordes"])
        if filtro == "Gris": img = ImageOps.grayscale(img)
        elif filtro == "Bordes": img = img.filter(ImageFilter.FIND_EDGES)
        st.image(img)

with tabs[3]:
    st.header("🎨 Laboratorio Artístico")
    desc = st.text_input("Describe tu diseño:")
    if st.button("Generar Renderizado"):
        url_art = f"https://image.pollinations.ai/prompt/{desc.replace(' ', '%20')}?model=flux"
        st.image(url_art, caption="Visualización Stark")