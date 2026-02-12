import streamlit as st
import pandas as pd
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
import gspread
import base64
import io
import PyPDF2

# --- CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(page_title="JARVIS: Protocolo Diana Total", layout="wide")

# --- 🔑 IDENTIFICACIÓN DE LA BASE DE DATOS ---
# ID extraído de tu enlace: 1ch6QcydRrTJhIVmpHLNtP1Aq60bmaZibefV3IcBu90o
ID_DE_TU_HOJA = "1ch6QcydRrTJhIVmpHLNtP1Aq60bmaZibefV3IcBu90o"

def conectar_google_sheets():
    try:
        # Conexión mediante el enlace público con permisos de editor
        url = f"https://docs.google.com/spreadsheets/d/{ID_DE_TU_HOJA}"
        gc = gspread.public_open(url)
        return gc.get_worksheet(0)
    except Exception as e:
        return None

# --- PROTOCOLO DE MEMORIA DE SESIÓN ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Seguridad para la llave de Groq
api_key_groq = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else ""

# --- FUNCIONES MAESTRAS DE JARVIS ---
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

def buscar_web(query):
    try:
        with DDGS() as ddgs:
            resultados = [r['body'] for r in ddgs.text(query, max_results=2)]
            return " ".join(resultados)
    except:
        return "Acceso a satélites limitado, Srta. Diana."

# --- INTERFAZ PRINCIPAL ---
st.title("🛰️ Proyecto JARVIS: Protocolo Diana")

tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Centro de Comando", 
    "📊 Análisis de Datos", 
    "📸 Editor Óptico", 
    "🎨 Laboratorio Artístico"
])

# --- PESTAÑA 1: CHAT + VOZ + GOOGLE SHEETS ---
with tab1:
    st.subheader("🎙️ Interfaz de Voz y Memoria en la Nube")
    
    # Intentar conectar con la hoja
    hoja = conectar_google_sheets()
    
    if hoja:
        st.success("🛰️ Conexión con Google Sheets: ESTABLE")
    else:
        st.error("⚠️ Error de enlace. Asegúrese de que la hoja esté compartida como 'Editor' para cualquier persona con el enlace.")

    # Mostrar historial de la sesión actual
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Entrada de Chat
    if prompt := st.chat_input("Sistemas listos. ¿En qué puedo ayudarla, Srta. Diana?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Analizando sistemas..."):
            # Lógica de búsqueda web si es necesario
            contexto_web = ""
            if any(p in prompt.lower() for p in ["noticias", "clima", "hoy", "quién"]):
                contexto_web = f"\nInformación de red: {buscar_web(prompt)}"

            # Llamada a la IA (Groq)
            client = Groq(api_key=api_key_groq)
            sys_msg = f"Eres JARVIS. Sofisticado, británico y eficiente. Responde siempre con elegancia a la Srta. Diana. {contexto_web}"
            
            mensajes_completos = [{"role": "system", "content": sys_msg}] + st.session_state.messages
            
            response = client.chat.completions.create(
                messages=mensajes_completos,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content

            # Mostrar respuesta y hablar
            with st.chat_message("assistant"):
                st.markdown(response)
                hablar(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})

            # GUARDAR EN GOOGLE SHEETS
            if hoja:
                try:
                    # Añade la fila: Columna A (Usuario), Columna B (JARVIS)
                    hoja.append_row([prompt, response])
                    st.toast("✅ Memoria sincronizada con Google Drive")
                except Exception as e:
                    st.error(f"Error de escritura: {e}")

# --- PESTAÑA 2: EXCEL ---
with tab2:
    st.header("📊 Procesamiento de Datos")
    opcion_ex = st.radio("Módulo:", ["Leer Excel Local", "Crear Reporte"])
    if opcion_ex == "Leer Excel Local":
        file_ex = st.file_uploader("Subir archivo .xlsx:", type=['xlsx'])
        if file_ex:
            df = pd.read_excel(file_ex)
            st.dataframe(df)
    else:
        if st.button("Generar Reporte Stark"):
            df_new = pd.DataFrame({'Proyecto': ['Diana IA'], 'Estado': ['JARVIS Nivel 5']})
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_new.to_excel(writer, index=False)
            st.download_button("Descargar Reporte", output.getvalue(), "stark_report.xlsx")

# --- PESTAÑA 3: EDITOR DE FOTOS ---
with tab3:
    st.header("📸 Reconocimiento Óptico")
    img_file = st.file_uploader("Sube una imagen:", type=['jpg', 'png'], key="img_jarvis")
    if img_file:
        img = Image.open(img_file)
        f = st.selectbox("Filtro:", ["Original", "Escala de Grises", "Bordes"])
        if f == "Escala de Grises": img = ImageOps.grayscale(img)
        elif f == "Bordes": img = img.filter(ImageFilter.FIND_EDGES)
        st.image(img, use_container_width=True)

# --- PESTAÑA 4: GENERADOR DE ARTE ---
with tab4:
    st.header("🎨 Laboratorio de Diseño")
    desc = st.text_input("Descripción del diseño:", key="art_desc")
    if st.button("🚀 Iniciar Renderizado"):
        with st.spinner("Generando visualización..."):
            url = f"https://image.pollinations.ai/prompt/{desc.replace(' ', '%20')}?model=flux"
            st.image(url, caption=f"Visualización Stark: {desc}")