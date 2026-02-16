import streamlit as st
from groq import Groq
from PIL import Image
import io, base64

# --- 1. ESTÉTICA DE LA TORRE STARK ---
st.set_page_config(page_title="JARVIS v129", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #010409; color: #00f2ff; }
    .arc-reactor {
        width: 50px; height: 50px; border-radius: 50%; margin: 10px auto;
        background: radial-gradient(circle, #fff 0%, #00f2ff 40%, transparent 70%);
        box-shadow: 0 0 20px #00f2ff; border: 1px solid #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
    /* Estilo para que la zona de pegado se vea integrada */
    .stFileUploader { border: 1px dashed #00f2ff; border-radius: 10px; padding: 10px; }
    </style>
    <div class="arc-reactor"></div>
    """, unsafe_allow_html=True)

# --- 2. NÚCLEO DE INTELIGENCIA ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    modelo_vision = "llama-3.2-11b-vision-preview"
else:
    st.stop()

# --- 3. INTERFAZ DE COMANDO HÍBRIDA ---
st.title("🛰️ TERMINAL DE COMANDO DIANA")

# Zona de Pegado (Aquí es donde debe hacer Ctrl+V)
st.write("📋 **ZONA DE PEGADO:** Haga clic abajo y pulse **Ctrl+V** para subir pantallazos.")
captura = st.file_uploader("", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")

# Barra de Chat
instruccion = st.chat_input("¿Qué desea que analice de esta captura, Srta. Diana?")

if captura:
    st.image(captura, width=350, caption="Captura detectada en el portapapeles")
    
    if instruccion:
        with st.chat_message("assistant"):
            try:
                encoded_img = base64.b64encode(captura.getvalue()).decode('utf-8')
                res = client.chat.completions.create(
                    model=modelo_vision,
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Actúa como JARVIS. {instruccion}"},
                            {"type": "image_url", "image_url": {"url": f"data:{captura.type};base64,{encoded_img}"}}
                        ]
                    }]
                )
                st.write(res.choices[0].message.content)
            except Exception as e:
                st.error(f"Falla en el sensor óptico: {e}")