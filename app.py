import streamlit as st
import pandas as pd
from PIL import Image
from groq import Groq
from duckduckgo_search import DDGS
import datetime

# --- CONFIGURACIÓN E INTERFAZ STARK ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# Inyección de CSS para el diseño moderno
st.markdown("""
    <style>
    /* Fondo oscuro y fuentes */
    .stApp {
        background-color: #0e1117;
        color: #00d4ff;
    }
    /* Estilo de las pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1a1c23;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        color: #00d4ff;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00d4ff !important;
        color: black !important;
        font-weight: bold;
    }
    /* Contenedores de chat */
    .stChatMessage {
        background-color: #1a1c23;
        border: 1px solid #00d4ff;
        border-radius: 10px;
        box-shadow: 0 0 10px #00d4ff;
    }
    /* El Reactor Arc Central */
    .arc-reactor {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA DE JARVIS ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def buscar_red(consulta):
    try:
        with DDGS() as ddgs:
            r = list(ddgs.text(f"{consulta} 2026", max_results=3))
            return "\n".join([i['body'] for i in r]) if r else "SISTEMA_OFFLINE"
    except: return "SISTEMA_OFFLINE"

# --- INTERFAZ ---
st.markdown("<h1 style='text-align: center; color: #00d4ff;'>🛰️ PROTOCOLO: DIANA</h1>", unsafe_allow_html=True)

# Render del Reactor Arc (Visual)
st.markdown("""
    <div class="arc-reactor">
        <img src="https://i.pinimg.com/originals/24/76/01/2476013a57582967964402636d9d9361.gif" width="150">
    </div>
    """, unsafe_allow_html=True)

tabs = st.tabs(["💬 COMANDO CENTRAL", "📊 ANÁLISIS STARK", "📸 ÓPTICO", "🎨 LABORATORIO"])

with tabs[0]:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("¿Sistemas listos, Srta. Diana?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("Procesando..."):
            info = buscar_red(prompt)
            fecha = datetime.datetime.now().strftime("%d/%m/%Y")
            
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            sys_msg = f"Eres JARVIS. Hoy es {fecha}. Datos red: {info}. Responde como la IA de Tony Stark, usa términos técnicos y sé elegante."

            response = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content

            with st.chat_message("assistant"): st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# (Las demás pestañas mantienen su lógica pero heredan el estilo azul neón)