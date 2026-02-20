import streamlit as st
from docxtpl import DocxTemplate, RichText
import io
from datetime import datetime
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="F.R.I.D.A.Y. - 26ª Com. Pudahuel", page_icon="🟢", layout="wide")

# 2. INYECCIÓN DE CSS DE ALTA PRIORIDAD (Protocolo de Fuerza)
st.markdown("""
    <style>
    /* FORZAR BARRA LATERAL */
    [data-testid="stSidebar"] {
        background-color: #004A2F !important;
    }
    /* FORZAR TEXTOS EN BARRA LATERAL A BLANCO */
    [data-testid="stSidebar"] .stText, 
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h4 {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    /* FORZAR BOTONES VERDES */
    .stButton > button, .stFormSubmitButton > button {
        background-color: #004A2F !important;
        color: #FFFFFF !important;
        border: 2px solid #C5A059 !important;
        font-weight: bold !important;
        width: 100% !important;
    }

    /* ENCABEZADO */
    .header-institucional {
        background-color: #004A2F;
        padding: 10px;
        border-radius: 10px;
        color: white;
        text-align: center;
        border: 2px solid #C5A059;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. BARRA LATERAL
with st.sidebar:
    # Verificamos si el logo existe localmente para evitar la imagen rota
    if os.path.exists("logo.png"):
        st.image("logo.png", width=140)
    else:
        # Respaldo si aún no sube el archivo
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Logotipo_de_Carabineros_de_Chile.svg/300px-Logotipo_de_Carabineros_de_Chile.svg.png", width=130)
    
    st.markdown("### 🟢 CONFIGURACIÓN DE FIRMA")
    nombre_f = st.text_input("Oficial", value="DIANA SANDOVAL ASTUDILLO")
    grado_f = st.text_input("Grado", value="C.P.R. Analista Social")
    cargo_f = st.text_input("Cargo", value="OFICINA DE OPERACIONES")
    
    st.markdown("---")
    st.markdown("#### **UNIDAD:**")
    st.write("26ª Comisaría Pudahuel") # Forzado a blanco por el CSS
    st.markdown(f"#### **FECHA:** {datetime.now().strftime('%d/%m/%Y')}")

# 4. CUERPO
st.markdown('<div class="header-institucional"><h2>CARABINEROS DE CHILE</h2><h4>SISTEMA F.R.I.D.A.Y.</h4></div>', unsafe_allow_html=True)

# Pestañas
tab1, tab2 = st.tabs(["📄 ACTA STOP", "📊 OTROS"])

with tab1:
    with st.form("form"):
        sem = st.text_input("Semana")
        prob = st.text_area("Problemática")
        submit = st.form_submit_button("🛡️ PROCESAR ACTA") # Debe verse verde

    if submit:
        # Lógica de firma con formato de imagen (Negrita/Normal/Negrita)
        st.success("Analizando...")