import streamlit as st
import pandas as pd
from groq import Groq
from duckduckgo_search import DDGS
import io

st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide")

# --- SEGURIDAD DE MEMORIA (EVITA EL ERROR ROJO) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CONFIGURACIÓN ---
api_key_groq = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else ""

# --- FUNCIONES DE JARVIS ---
def buscar_web(query):
    try:
        with DDGS() as ddgs:
            resultados = [r['body'] for r in ddgs.text(query, max_results=2)]
            return " ".join(resultados)
    except: return "No pude acceder a los satélites en este momento."

st.title("🛰️ Proyecto JARVIS: Protocolo Diana")

tabs = st.tabs(["💬 Centro de Comando", "📊 Análisis de Datos", "🎨 Laboratorio Artístico"])

with tabs[0]:
    # Mostrar historial de forma segura
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Sistemas listos. ¿En qué puedo ayudarla, Srta. Diana?"):
        # Guardamos el mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("Consultando bases de datos..."):
            # Lógica inteligente de búsqueda
            contexto_web = ""
            if any(palabra in prompt.lower() for palabra in ["quien", "noticia", "clima", "hoy"]):
                contexto_web = f"\nInformación de último minuto: {buscar_web(prompt)}"

            client = Groq(api_key=api_key_groq)
            sys_msg = f"Eres JARVIS. Eres culto, sofisticado y eficiente. {contexto_web}"
            
            mensajes_para_ia = [{"role": "system", "content": sys_msg}] + st.session_state.messages
            
            response = client.chat.completions.create(
                messages=mensajes_para_ia,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content

            with st.chat_message("assistant"): st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})