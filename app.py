import streamlit as st
import pandas as pd
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
import PyPDF2
import requests
from gtts import gTTS
import base64
import io

st.set_page_config(page_title="Diana Súper IA: Todo en Uno", layout="wide")

# --- FUNCIONES DE APOYO (VOZ) ---
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

# --- CONFIGURACIÓN ---
api_key_groq = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else ""
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🚀 Diana Súper IA: Edición Total")

# --- LAS 4 PESTAÑAS MÁGICAS ---
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat & Voz", "📊 Excel Pro", "📸 Editor Pro", "🎨 Artista IA"])

# --- PESTAÑA 1: CHAT Y PDF ---
with tab1:
    st.subheader("🎙️ Conversa y analiza documentos")
    archivo_pdf = st.file_uploader("Sube un PDF", type=['pdf'], key="pdf_chat")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if prompt := st.chat_input("Escribe o usa el micro de tu teclado..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        client = Groq(api_key=api_key_groq)
        response = client.chat.completions.create(messages=st.session_state.messages, model="llama-3.3-70b-versatile").choices[0].message.content
        with st.chat_message("assistant"): 
            st.markdown(response)
            hablar(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- PESTAÑA 2: EXCEL ---
with tab2:
    st.header("📊 Herramientas de Excel")
    modo_ex = st.radio("Acción:", ["Leer Excel", "Crear Excel"])
    if modo_ex == "Leer Excel":
        file_ex = st.file_uploader("Sube archivo .xlsx", type=['xlsx'])
        if file_ex:
            df = pd.read_excel(file_ex)
            st.dataframe(df)
    else:
        if st.button("Generar Excel de Prueba"):
            df_new = pd.DataFrame({'Nombre': ['Diana'], 'Estado': ['Súper IA Activada']})
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_new.to_excel(writer, index=False)
            st.download_button("Descargar Excel", output.getvalue(), "mi_tabla.xlsx")

# --- PESTAÑA 3: EDITOR ---
with tab3:
    st.header("📸 Filtros de Imagen")
    img_file = st.file_uploader("Sube una foto", type=['jpg', 'png'], key="img_edit")
    if img_file:
        img = Image.open(img_file)
        filtro = st.selectbox("Filtro:", ["Original", "Blanco y Negro", "Borroso"])
        if filtro == "Blanco y Negro": img = ImageOps.grayscale(img)
        elif filtro == "Borroso": img = img.filter(ImageFilter.BLUR)
        st.image(img)

# --- PESTAÑA 4: ARTISTA ---
with tab4:
    st.header("🎨 Creador de Arte")
    desc = st.text_input("¿Qué dibujo hoy?", key="desc_art")
    if st.button("🚀 Crear Imagen"):
        with st.spinner("Dibujando..."):
            url = f"https://image.pollinations.ai/prompt/{desc.replace(' ', '%20')}?width=1024&height=1024&model=flux"
            st.image(url, caption=f"Arte para Diana: {desc}")