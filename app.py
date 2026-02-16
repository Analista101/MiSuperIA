import streamlit as st
from groq import Groq
from PIL import Image
from streamlit_paste_button import paste_button # El nuevo sensor táctico
from streamlit_mic_recorder import mic_recorder
import io, base64

# --- 1. ESTÉTICA DE LA TORRE STARK ---
st.set_page_config(page_title="JARVIS v130", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #010409; color: #00f2ff; }
    .arc-reactor {
        width: 55px; height: 55px; border-radius: 50%; margin: 10px auto;
        background: radial-gradient(circle, #fff 0%, #00f2ff 40%, transparent 70%);
        box-shadow: 0 0 20px #00f2ff; border: 2px solid #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- 2. NÚCLEO INDEPENDIENTE ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    modelo_vision = "llama-3.2-11b-vision-preview"
    modelo_texto = "llama-3.3-70b-versatile"
else:
    st.error("🚨 SRTA. DIANA: ACCESO DENEGADO. REVISE SECRETS.")
    st.stop()

# --- 3. INTERFAZ CENTRALIZADA ---
st.title("🛰️ TERMINAL DE COMANDO HÍBRIDA")

tabs = st.tabs(["💬 COMANDO Y CAPTURAS", "📊 ANÁLISIS DOCS", "🎨 LABORATORIO"])

with tabs[0]:
    st.subheader("📋 Sensor de Portapapeles e IA")
    
    col_a, col_b = st.columns([1, 4])
    with col_a:
        mic_recorder(start_prompt="🎙️", stop_prompt="🛰️", key="mic_130")
    
    # --- LA SOLUCIÓN DEFINITIVA ---
    # Este botón detectará automáticamente si tiene una imagen copiada
    pasted_image = paste_button(label="📋 PEGAR CAPTURA (CTRL+V)")

    chat_msg = st.chat_input("Instrucciones para la imagen o consulta general...")

    if pasted_image.image_data is not None:
        img = pasted_image.image_data
        st.image(img, caption="Imagen pegada desde el portapapeles", width=400)
        
        if chat_msg:
            with st.spinner("JARVIS analizando captura..."):
                try:
                    # Convertir el objeto de imagen a base64
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    res = client.chat.completions.create(
                        model=modelo_vision,
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"JARVIS, atiende a la Srta. Diana: {chat_msg}"},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                            ]
                        }]
                    )
                    st.write(res.choices[0].message.content)
                except Exception as e:
                    st.error(f"Falla en sensor: {e}")
    
    elif chat_msg:
        # Lógica de texto puro si no hay imagen
        res = client.chat.completions.create(
            model=modelo_texto,
            messages=[{"role": "user", "content": chat_msg}]
        )
        st.write(res.choices[0].message.content)

# Pestañas de Análisis y Laboratorio (Código previo se mantiene integrado)