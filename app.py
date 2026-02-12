import streamlit as st
from PIL import Image, ImageOps, ImageFilter
from groq import Groq

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Diana IA Pro", layout="wide")

# 2. MEMORIA DEL CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. SEGURIDAD (SECRETS)
# Aquí intenta leer la llave que pegaste en la web de Streamlit
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    # Si no la encuentra (como en tu PC), la pide en la barra lateral
    api_key = st.sidebar.text_input("Introduce Groq API Key:", type="password")

st.title("🌌 Diana IA: Versión en la Nube")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("🖼️ Visión")
    archivo = st.file_uploader("Sube una foto", type=['jpg', 'png', 'jpeg'])
    if archivo:
        img = Image.open(archivo)
        st.image(img, use_container_width=True)

with col2:
    st.header("💬 Chat Inteligente")
    # Mostrar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada de chat
    if prompt := st.chat_input("¿En qué puedo ayudarte hoy, Diana?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if not api_key:
            st.error("Falta la API Key en los Secrets o en la barra lateral.")
        else:
            try:
                client = Groq(api_key=api_key)
                completion = client.chat.completions.create(
                    messages=st.session_state.messages,
                    model="llama-3.3-70b-versatile"
                )
                response = completion.choices[0].message.content
                with st.chat_message("assistant"):
                    st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {e}")