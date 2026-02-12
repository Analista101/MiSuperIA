import streamlit as st
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
import PyPDF2

st.set_page_config(page_title="Diana Súper IA", layout="wide")

# 1. MEMORIA Y CONFIGURACIÓN DE PERSONALIDAD
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. SEGURIDAD AUTOMÁTICA
api_key = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else st.sidebar.text_input("API Key:", type="password")

# --- BARRA LATERAL (HERRAMIENTAS C y A) ---
with st.sidebar:
    st.header("🛠️ Herramientas Pro")
    modo = st.selectbox("Personalidad de la IA:", ["Asistente Pro", "Creativo", "Amigo Divertido"])
    
    st.divider()
    if st.button("🗑️ Borrar Memoria"):
        st.session_state.messages = []
        st.rerun()

st.title("🌌 Diana Súper IA: Edición Total")

pestana1, pestana2 = st.tabs(["💬 Chat & PDF", "🎨 Editor de Imágenes"])

# --- PESTAÑA 1: CHAT + PDF (HERRAMIENTA B) ---
with pestana1:
    st.subheader(f"Chat en modo: {modo}")
    
    archivo_pdf = st.file_uploader("¿Quieres que analice un PDF?", type=['pdf'])
    texto_pdf = ""
    if archivo_pdf:
        lector = PyPDF2.PdfReader(archivo_pdf)
        for pagina in lector.pages:
            texto_pdf += pagina.extract_text()
        st.success("✅ PDF leído. ¡Pregúntame lo que quieras sobre él!")

    # Mostrar historial
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Escribe aquí..."):
        # Ajuste de personalidad según lo elegido
        instruccion = f"Actúa como un {modo}. "
        if texto_pdf: instruccion += f"Contexto del PDF: {texto_pdf[:2000]}" # Lee los primeros 2000 caracteres
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        client = Groq(api_key=api_key)
        # Enviamos la personalidad como primer mensaje oculto
        full_messages = [{"role": "system", "content": instruccion}] + st.session_state.messages
        
        response = client.chat.completions.create(messages=full_messages, model="llama-3.3-70b-versatile").choices[0].message.content
        
        with st.chat_message("assistant"): st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- PESTAÑA 2: EDITOR DE FOTOS ---
with pestana2:
    st.header("🖼️ Edición Visual")
    img_file = st.file_uploader("Sube una imagen para editar", type=['jpg', 'png'])
    if img_file:
        img = Image.open(img_file)
        filtro = st.radio("Aplica un efecto:", ["Original", "Blanco y Negro", "Contornos", "Borroso"])
        
        if filtro == "Blanco y Negro": img = ImageOps.grayscale(img)
        elif filtro == "Contornos": img = img.filter(ImageFilter.FIND_EDGES)
        elif filtro == "Borroso": img = img.filter(ImageFilter.BLUR)
        
        st.image(img, use_container_width=True)