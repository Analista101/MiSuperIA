import streamlit as st
from PIL import Image, ImageOps, ImageFilter
from groq import Groq
import PyPDF2
from openai import OpenAI  # Importamos la herramienta de imágenes

st.set_page_config(page_title="Diana Súper IA Artista", layout="wide")

# 1. SEGURIDAD Y LLAVES
# Necesitaremos una llave de OpenAI para las imágenes
api_key_groq = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else ""
api_key_openai = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else ""

# 2. MEMORIA
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🌌 Diana Súper IA: Edición Artista")

# CREAMOS 3 PESTAÑAS
pestana1, pestana2, pestana3 = st.tabs(["💬 Chat & PDF", "📸 Editor de Fotos", "🎨 Generador de Imágenes"])

# --- PESTAÑA 1: CHAT & PDF ---
with pestana1:
    # (Aquí va tu código de chat y PDF que ya funciona)
    st.info("Usa el chat normal para hablar o analizar PDFs.")

# --- PESTAÑA 2: EDITOR DE FOTOS ---
with pestana2:
    # (Aquí va tu código de filtros que ya funciona)
    st.info("Sube fotos para aplicarles filtros.")

# --- PESTAÑA 3: GENERADOR DE IMÁGENES (NUEVO!) ---
with pestana3:
    st.header("🎨 Crea arte con IA")
    descripcion = st.text_input("Describe la imagen que quieres crear:", placeholder="Ej: Un gato astronauta pintado por Van Gogh")
    
    if st.button("🚀 Generar Imagen"):
        if not api_key_openai:
            st.error("Necesitas configurar tu OPENAI_API_KEY en los Secrets.")
        elif descripcion:
            with st.spinner("Creando tu obra de arte..."):
                try:
                    client_ai = OpenAI(api_key=api_key_openai)
                    response = client_ai.images.generate(
                        model="dall-e-3",
                        prompt=descripcion,
                        size="1024x1024",
                        quality="standard",
                        n=1,
                    )
                    url_imagen = response.data[0].url
                    st.image(url_imagen, caption=f"Resultado: {descripcion}")
                except Exception as e:
                    st.error(f"Hubo un error: {e}")
        else:
            st.warning("Escribe una descripción primero.")