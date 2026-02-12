import streamlit as st
from groq import Groq
import PyPDF2
import requests

st.set_page_config(page_title="Diana IA Pro Max", layout="wide")

# 1. CONFIGURACIÓN DE SEGURIDAD
api_key_groq = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else ""

# 2. INICIALIZAR MEMORIA AVANZADA
if "messages" not in st.session_state:
    # El primer mensaje es el "System Prompt" que define su inteligencia
    st.session_state.messages = [
        {"role": "system", "content": "Eres Diana IA Pro, una asistente de élite. Eres precisa, inteligente y siempre verificas tus datos. Ayudas a Diana a tener éxito en sus proyectos."}
    ]

with st.sidebar:
    st.header("🧠 Ajustes de Inteligencia")
    # Control de precisión: 0 es exacto, 1 es creativo
    precision = st.slider("Nivel de Creatividad:", 0.0, 1.0, 0.4)
    
    if st.button("🗑️ Reiniciar Memoria"):
        st.session_state.messages = [{"role": "system", "content": "Eres Diana IA Pro..."}]
        st.rerun()

st.title("🚀 Diana IA: Edición Inteligencia Superior")

pestana1, pestana2 = st.tabs(["💬 Chat Inteligente", "🎨 Creador de Arte"])

with pestana1:
    # Lector de PDF integrado en la precisión
    archivo_pdf = st.file_uploader("Sube un PDF para análisis profundo", type=['pdf'])
    contexto_pdf = ""
    if archivo_pdf:
        lector = PyPDF2.PdfReader(archivo_pdf)
        for pagina in lector.pages:
            contexto_pdf += pagina.extract_text()
        st.success("✅ Documento analizado con precisión.")

    # Mostrar mensajes (saltando el mensaje de sistema)
    for m in st.session_state.messages[1:]:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Escribe tu consulta profesional..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        # Lógica de Inteligencia Superior
        client = Groq(api_key=api_key_groq)
        
        # Si hay PDF, se inyecta en el último mensaje para máxima precisión
        mensajes_con_contexto = st.session_state.messages.copy()
        if contexto_pdf:
            mensajes_con_contexto.append({"role": "system", "content": f"Contexto del PDF: {contexto_pdf[:5000]}"})

        with st.spinner("Pensando con precisión..."):
            completion = client.chat.completions.create(
                messages=mensajes_con_contexto,
                model="llama-3.3-70b-versatile",
                temperature=precision, # Aquí aplicamos el slider
                max_tokens=2048 # Más capacidad de respuesta
            )
            
            response = completion.choices[0].message.content
            with st.chat_message("assistant"): st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

with pestana2:
    st.info("El generador de imágenes ahora usa el Cerebro Artístico mejorado.")
    # (Aquí puedes mantener tu código de imágenes anterior)