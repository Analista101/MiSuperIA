import streamlit as st
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
import PyPDF2
import requests
import io

st.set_page_config(page_title="Diana IA Artista Gratis", layout="wide")

# SEGURIDAD (Solo Groq para el chat)
api_key_groq = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else ""

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🌌 Diana Súper IA: Edición Artista Gratuita")

pestana1, pestana2, pestana3 = st.tabs(["💬 Chat & PDF", "📸 Editor de Fotos", "🎨 Creador de Imágenes"])

# --- PESTAÑA 1: CHAT ---
with pestana1:
    archivo_pdf = st.file_uploader("¿Analizamos un PDF?", type=['pdf'])
    texto_pdf = ""
    if archivo_pdf:
        lector = PyPDF2.PdfReader(archivo_pdf)
        for pagina in lector.pages:
            texto_pdf += pagina.extract_text()
        st.success("✅ PDF cargado")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Dime algo..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        client = Groq(api_key=api_key_groq)
        instruccion = f"Contexto PDF: {texto_pdf[:1000]}" if texto_pdf else ""
        full_msj = [{"role": "system", "content": instruccion}] + st.session_state.messages
        response = client.chat.completions.create(messages=full_msj, model="llama-3.3-70b-versatile").choices[0].message.content
        with st.chat_message("assistant"): st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- PESTAÑA 2: EDITOR ---
with pestana2:
    img_file = st.file_uploader("Sube una foto", type=['jpg', 'png'])
    if img_file:
        img = Image.open(img_file)
        st.image(img, caption="Original")

# --- PESTAÑA 3: GENERADOR GRATIS ---
with pestana3:
    st.header("🎨 Genera imágenes sin llaves")
    descripcion = st.text_input("¿Qué quieres que dibuje?", placeholder="Ej: Un paisaje futurista de una ciudad rosa")
    
    if st.button("🚀 Crear Obra"):
        if descripcion:
            with st.spinner("Dibujando..."):
                # Usamos Pollinations AI (Es gratis y no pide llaves)
                url = f"https://image.pollinations.ai/prompt/{descripcion.replace(' ', '%20')}"
                response = requests.get(url)
                if response.status_code == 200:
                    st.image(response.content, caption=f"Arte para Diana: {descripcion}")
                    st.download_button("Descargar Obra", response.content, "ia_arte.png")
                else:
                    st.error("El servidor de dibujo está ocupado, intenta en un momento.")
        else:
            st.warning("Escribe una descripción primero.")