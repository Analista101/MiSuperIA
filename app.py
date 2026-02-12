import streamlit as st
import pandas as pd
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
from duckduckgo_search import DDGS
from gtts import gTTS
import base64
import io
import PyPDF2

st.set_page_config(page_title="JARVIS: Protocolo Diana Total", layout="wide")

# --- PROTOCOLO DE MEMORIA (EVITA ERRORES) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CONFIGURACIÓN DE LLAVES ---
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
    except: return "Acceso a red limitado, Srta. Diana."

st.title("🛰️ Proyecto JARVIS: Protocolo Diana")

# --- LAS 4 PESTAÑAS DEL SISTEMA ---
tab1, tab2, tab3, tab4 = st.tabs(["💬 Centro de Comando", "📊 Análisis de Datos", "📸 Editor Óptico", "🎨 Laboratorio Artístico"])

# --- PESTAÑA 1: CHAT INTELIGENTE + VOZ + PDF ---
with tab1:
    st.subheader("🎙️ Interfaz de Voz y Análisis")
    archivo_pdf = st.file_uploader("Subir informe PDF:", type=['pdf'], key="jarvis_pdf")
    texto_pdf = ""
    if archivo_pdf:
        lector = PyPDF2.PdfReader(archivo_pdf)
        for pagina in lector.pages: texto_pdf += pagina.extract_text()
        st.success("Sistemas: PDF analizado.")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Diga algo, Srta. Diana..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("Analizando sistemas..."):
            contexto_web = ""
            if any(p in prompt.lower() for p in ["noticias", "clima", "hoy", "quien"]):
                contexto_web = f"\nDatos de red: {buscar_web(prompt)}"

            client = Groq(api_key=api_key_groq)
            sys_msg = f"Eres JARVIS. Sofisticado y eficiente. Contexto PDF: {texto_pdf[:1000]}. {contexto_web}"
            
            mensajes_completos = [{"role": "system", "content": sys_msg}] + st.session_state.messages
            
            response = client.chat.completions.create(
                messages=mensajes_completos,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content

            with st.chat_message("assistant"): 
                st.markdown(response)
                hablar(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# --- PESTAÑA 2: EXCEL ---
with tab2:
    st.header("📊 Procesamiento de Datos")
    opcion_ex = st.radio("Módulo:", ["Leer", "Crear"])
    if opcion_ex == "Leer":
        file_ex = st.file_uploader("Subir Excel:", type=['xlsx'])
        if file_ex:
            df = pd.read_excel(file_ex)
            st.dataframe(df)
    else:
        if st.button("Generar Informe Stark"):
            df_new = pd.DataFrame({'Proyecto': ['Diana IA'], 'Nivel': ['JARVIS Total']})
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
        f = st.selectbox("Filtro de Análisis:", ["Original", "Escala de Grises", "Detección de Bordes"])
        if f == "Escala de Grises": img = ImageOps.grayscale(img)
        elif f == "Detección de Bordes": img = img.filter(ImageFilter.FIND_EDGES)
        st.image(img, use_container_width=True)

# --- PESTAÑA 4: GENERADOR DE ARTE ---
with tab4:
    st.header("🎨 Laboratorio de Diseño")
    desc = st.text_input("Descripción del diseño:", key="art_desc")
    estilo = st.selectbox("Estilo Visual:", ["Cinematográfico", "Realista", "Cyberpunk", "Plano"])
    if st.button("🚀 Iniciar Renderizado"):
        with st.spinner("Generando visualización..."):
            url = f"https://image.pollinations.ai/prompt/{desc.replace(' ', '%20')}, {estilo} style, 8k, masterpiece?model=flux"
            st.image(url, caption=f"Visualización Stark: {desc}")