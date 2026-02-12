import streamlit as st
from PIL import Image, ImageOps, ImageFilter
from groq import Groq

# CONFIGURACIÓN PRO
st.set_page_config(page_title="Diana IA Pro", layout="wide")

# MEMORIA DEL CHAT (Si no existe, la creamos)
if "messages" not in st.session_state:
    st.session_state.messages = []

# DISEÑO FUTURISTA
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #4CAF50; border-radius: 10px; color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌌 Diana IA: Edición Definitiva")

# BARRA LATERAL
with st.sidebar:
    st.header("⚙️ Panel de Control")
    api_key = st.text_input("Groq API Key:", type="password")
    if st.button("Limpiar Chat"):
        st.session_state.messages = []

col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("🖼️ Visión y Edición")
    archivo = st.file_uploader("Sube una foto", type=['jpg', 'png', 'jpeg'])
    if archivo:
        img = Image.open(archivo)
        filtro = st.selectbox("Efecto IA:", ["Original", "Grises", "Bordes", "Desenfoque"])
        
        if filtro == "Grises": img = ImageOps.grayscale(img)
        elif filtro == "Bordes": img = img.filter(ImageFilter.FIND_EDGES)
        elif filtro == "Desenfoque": img = img.filter(ImageFilter.BLUR)
        
        st.image(img, use_container_width=True)
        # BOTÓN DE DESCARGA (Deseo C)
        st.download_button("Descargar Imagen", data=archivo, file_name="ia_editada.png")

with col2:
    st.header("💬 Chat con Memoria (Deseo B)")
    
    # Mostrar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada de chat
    if prompt := st.chat_input("¿En qué piensas, Diana?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if not api_key:
            st.error("Pega tu llave en la izquierda.")
        else:
            client = Groq(api_key=api_key)
            completion = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile"
            )
            response = completion.choices[0].message.content
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})