import streamlit as st
from groq import Groq
import PyPDF2

# Librería nueva para que la IA hable (Text-to-Speech)
from gtts import gTTS 
import base64

st.set_page_config(page_title="Diana IA Pro: Modo Siri", layout="wide")

# Función para que la IA hable
def hablar(texto):
    tts = gTTS(text=texto, lang='es')
    tts.save("respuesta.mp3")
    with open("respuesta.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# SEGURIDAD
api_key_groq = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else ""

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🎙️ Diana IA: Modo Conversación")

# --- INTERFAZ DE VOZ ---
st.write("### Haz clic en el micrófono de tu teclado o usa el chat:")

if prompt := st.chat_input("Dime algo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    client = Groq(api_key=api_key_groq)
    with st.spinner("Escuchando y pensando..."):
        response = client.chat.completions.create(
            messages=st.session_state.messages, 
            model="llama-3.3-70b-versatile"
        ).choices[0].message.content
        
        with st.chat_message("assistant"): 
            st.markdown(response)
            # ¡AQUÍ ESTÁ LA MAGIA!
            hablar(response) 
        
        st.session_state.messages.append({"role": "assistant", "content": response})