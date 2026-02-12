import streamlit as st
from PIL import Image
from groq import Groq
import PyPDF2
import requests

st.set_page_config(page_title="Diana IA: Cerebro Artístico", layout="wide")

# SEGURIDAD
api_key_groq = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else ""

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🌌 Diana Súper IA: Cerebro Artístico Activado")

pestana1, pestana2, pestana3 = st.tabs(["💬 Chat & PDF", "📸 Editor", "🎨 Creador de Imágenes"])

with pestana1:
    # --- CHAT DE SIEMPRE ---
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if prompt := st.chat_input("Dime algo..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        client = Groq(api_key=api_key_groq)
        response = client.chat.completions.create(messages=st.session_state.messages, model="llama-3.3-70b-versatile").choices[0].message.content
        with st.chat_message("assistant"): st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

with pestana3:
    st.header("🎨 Generador de Alta Calidad")
    descripcion = st.text_input("¿Qué quieres que dibuje?", placeholder="Ej: Una astronauta en un bosque mágico")
    
    # OPCIONES DE ESTILO
    estilo = st.selectbox("Elige un estilo:", ["Realista", "Dibujo Animado", "Cyberpunk", "Óleo", "Arte Digital"])
    
    if st.button("🚀 Crear Obra Maestra"):
        if descripcion:
            with st.spinner("Tu cerebro artístico está diseñando..."):
                # ESTE ES EL TRUCO: Le añadimos palabras mágicas a tu descripción
                mejorador = ", highly detailed, 8k resolution, cinematic lighting, masterpiece, trending on artstation"
                prompt_final = f"{descripcion}, {estilo} style {mejorador}"
                
                url = f"https://image.pollinations.ai/prompt/{prompt_final.replace(' ', '%20')}"
                
                response = requests.get(url)
                if response.status_code == 200:
                    st.image(response.content, caption=f"Resultado: {descripcion} (Estilo: {estilo})")
                    st.download_button("Descargar mi Obra", response.content, "diana_arte.png")
                else:
                    st.error("El servidor de dibujo está saturado. ¡Intenta de nuevo!")