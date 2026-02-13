import streamlit as st
import pandas as pd
from groq import Groq
from duckduckgo_search import DDGS
import datetime

# --- CONFIGURACIÓN DE LA TERMINAL ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# CSS Avanzado para efecto Holograma y Reactor
st.markdown("""
    <style>
    /* Fondo Espacial */
    .stApp {
        background: radial-gradient(circle, #0a192f 0%, #020617 100%);
        color: #00f2ff;
    }
    
    /* El Reactor Arc (CSS Puro para evitar enlaces rotos) */
    .arc-container {
        display: flex;
        justify-content: center;
        padding: 20px;
    }
    .arc-reactor {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: radial-gradient(circle, #fff 0%, #00f2ff 40%, transparent 70%);
        box-shadow: 0 0 50px #00f2ff, inset 0 0 30px #00f2ff;
        border: 4px solid #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.05); opacity: 1; box-shadow: 0 0 70px #00f2ff; }
        100% { transform: scale(1); opacity: 0.8; }
    }

    /* Títulos y Pestañas */
    h1 { text-shadow: 0 0 20px #00f2ff; font-family: 'Courier New', monospace; }
    .stTabs [data-baseweb="tab"] {
        color: #00f2ff !important;
        background-color: rgba(0, 242, 255, 0.05);
        border: 1px solid #00f2ff;
        border-radius: 5px;
        margin-right: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00f2ff !important;
        color: #000 !important;
        box-shadow: 0 0 15px #00f2ff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA CENTRAL ---
st.markdown("<h1 style='text-align: center;'>🛰️ PROTOCOLO: DIANA</h1>", unsafe_allow_html=True)

# Generador del Reactor Arc Holográfico
st.markdown('<div class="arc-container"><div class="arc-reactor"></div></div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

def buscar_red(consulta):
    try:
        with DDGS() as ddgs:
            r = list(ddgs.text(f"{consulta} hoy 2026", max_results=3))
            return "\n".join([i['body'] for i in r]) if r else "SIN_DATOS"
    except: return "SIN_DATOS"

tabs = st.tabs(["💬 COMANDO CENTRAL", "📊 ANÁLISIS STARK", "📸 ÓPTICO", "🎨 LABORATORIO"])

with tabs[0]:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("¿Sistemas listos, Srta. Diana?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.spinner("Analizando flujo de datos..."):
            info = buscar_red(prompt)
            fecha = datetime.datetime.now().strftime("%d de febrero de 2026")
            
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            sys_msg = f"Eres JARVIS. Hoy es {fecha}. Datos de red: {info}. Responde con precisión técnica y elegancia."

            response = client.chat.completions.create(
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages,
                model="llama-3.3-70b-versatile"
            ).choices[0].message.content

            with st.chat_message("assistant"): st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Resto de pestañas (Análisis, Óptico, Lab) con su lógica base...