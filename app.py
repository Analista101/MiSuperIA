import streamlit as st  # <--- ESTO DEBE SER LA LÍNEA 1
import pandas as pd
from PIL import Image, ImageOps
import google.generativeai as genai
import edge_tts
import asyncio
import base64, io, datetime, requests
from streamlit_mic_recorder import mic_recorder

# --- 1. CONFIGURACIÓN ESTRUCTURAL (Debe ir antes de usar st.secrets) ---
st.set_page_config(page_title="JARVIS: Protocolo Diana", layout="wide", page_icon="🛰️")

# --- 2. VERIFICACIÓN DE SECRETOS Y NÚCLEO ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model_chat = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    st.error("⚠️ Error Crítico: Falta la GOOGLE_API_KEY en los secretos de la plataforma.")
    st.stop() # JARVIS detiene la ejecución si no hay energía (API KEY)

# --- 3. ESTÉTICA STARK ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #0a192f 0%, #020617 100%); color: #00f2ff; }
    .arc-reactor {
        width: 80px; height: 80px; border-radius: 50%; margin: 20px auto;
        background: radial-gradient(circle, #fff 0%, #00f2ff 40%, transparent 70%);
        box-shadow: 0 0 30px #00f2ff; border: 2px solid #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# ... (El resto de las funciones hablar y las pestañas continúan igual)