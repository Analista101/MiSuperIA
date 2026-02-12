import streamlit as st
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
import PyPDF2
import requests
from gtts import gTTS
import base64
import io

st.set_page_config(page_title="Diana IA: Super App Total", layout="wide")

# --- FUNCIONES DE VOZ ---
def hablar(texto):
    tts = gTTS(text=texto, lang='es')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    data = fp.read()
    b64 = base64.b64encode(data).decode()
    md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    st.markdown(md, unsafe_allow_html=True)

# --- SEGURIDAD Y MEMORIA ---
api_key_groq = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else ""
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🚀 Diana Súper IA: Edición Siri + Herramientas")

# --- LAS PESTAÑAS (Para que no se pierda nada) ---
pestana1, pestana2, pestana3 = st.tabs(["🎙️ Chat & Voz", "📸 Editor Pro", "🎨 Artista IA"])

# --- PESTAÑA 1: CHAT, PDF Y VOZ ---
with pestana1:
    st.subheader("Conversación Inteligente")
    archivo_pdf = st.file_uploader("¿Quieres que analice un PDF?", type=['pdf'])
    texto_pdf = ""
    if archivo_pdf:
        lector = PyPDF2.PdfReader(archivo_pdf)
        for pagina in lector.pages:
            texto_pdf += pagina.extract_text()
        st.success("✅ PDF cargado.")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Dime algo o usa el micro de tu teclado..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        client = Groq(api_key=api_key_groq)
        instruccion = f"Contexto PDF: {texto_pdf[:2000]}" if texto_pdf else ""
        full_msj = [{"role": "system", "content": instruccion}] + st.session_state.messages
        
        with st.spinner("Pensando..."):
            response = client.chat.completions.create(messages=full_msj, model="llama-3.3-70b-versatile").choices[0].message.content
            with st.chat_message("assistant"): 
                st.markdown(response)
                hablar(response) # ¡Aquí habla!
            st.session_state.messages.append({"role": "assistant", "content": response})

# --- PESTAÑA 2: EDITOR DE FOTOS ---
with pestana2:
    st.header("📸 Edición de Fotos")
    img_file = st.file_uploader("Sube una imagen", type=['jpg', 'png'], key="editor")
    if img_file:
        img = Image.open(img_file)
        filtro = st.radio("Efecto:", ["Original", "Blanco y Negro", "Contornos", "Borroso"])
        if filtro == "Blanco y Negro": img = ImageOps.grayscale(img)
        elif filtro == "Contornos": img = img.filter(ImageFilter.FIND_EDGES)
        elif filtro == "Borroso": img = img.filter(ImageFilter.BLUR)
        st.image(img, use_container_width=True)

# --- PESTAÑA 3: CREADOR DE IMÁGENES ---
with pestana3:
    st.header("🎨 Generador de Arte")
    desc = st.text_input("¿Qué dibujo?", placeholder="Ej: Un astronauta en Marte")
    estilo = st.selectbox("Estilo:", ["Realista", "Cyberpunk", "Óleo", "Dibujo"])
    if st.button("🚀 Crear Imagen"):
        with st.spinner("Dibujando..."):
            prompt_final = f"{desc}, {estilo} style, highly detailed, 8k"
            url = f"https://image.pollinations.ai/prompt/{prompt_final.replace(' ', '%20')}"
            st.image(url, caption=f"Arte: {desc}")