import streamlit as st
from docxtpl import DocxTemplate, RichText
import io
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser lo primero)
st.set_page_config(page_title="F.R.I.D.A.Y. - 26ª Com. Pudahuel", page_icon="🟢", layout="wide")

# 2. INYECCIÓN DE CSS DE ALTA PRIORIDAD
st.markdown("""
    <style>
    /* 1. BARRA LATERAL: FONDO VERDE Y TEXTO BLANCO */
    section[data-testid="stSidebar"] {
        background-color: #004A2F !important;
    }
    /* Forzar color blanco en TODO lo que esté dentro de la barra lateral */
    section[data-testid="stSidebar"] .stMarkdown p, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] span {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    /* 2. BOTONES VERDES INSTITUCIONALES */
    .stButton > button, .stFormSubmitButton > button {
        background-color: #004A2F !important;
        color: #FFFFFF !important;
        border: 2px solid #C5A059 !important;
        font-weight: bold !important;
        width: 100% !important;
        height: 3.5em !important;
        text-transform: uppercase;
    }
    
    .stButton > button:hover {
        background-color: #006341 !important;
        border-color: #FFFFFF !important;
    }

    /* 3. PESTAÑAS (TABS) EN VERDE */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #004A2F !important;
        border-radius: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #C5A059 !important;
        color: #000000 !important;
    }

    /* 4. ENCABEZADO CENTRADO */
    .header-institucional {
        background-color: #004A2F;
        padding: 15px;
        border-radius: 10px;
        color: #FFFFFF !important;
        text-align: center;
        border: 2px solid #C5A059;
        margin-bottom: 20px;
    }
    
    /* 5. TEXTO CUERPO (Labels de los formularios) */
    .stApp label {
        color: #004A2F !important;
        font-weight: 800 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. BARRA LATERAL
with st.sidebar:
    # Intento de carga de logo (image_252540) con enlace directo
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Logotipo_de_Carabineros_de_Chile.svg/640px-Logotipo_de_Carabineros_de_Chile.svg.png", width=140)
    
    st.markdown("### 🟢 CONFIGURACIÓN DE FIRMA")
    nombre_f = st.text_input("Nombre Oficial", value="DIANA SANDOVAL ASTUDILLO")
    grado_f = st.text_input("Grado", value="C.P.R. Analista Social")
    cargo_f = st.text_input("Cargo", value="OFICINA DE OPERACIONES")
    
    st.markdown("---")
    st.markdown("#### **UNIDAD:**")
    st.markdown("26ª Comisaría Pudahuel") # Ahora será BLANCO
    st.markdown(f"#### **FECHA:** {datetime.now().strftime('%d/%m/%Y')}")

# 4. ENCABEZADO PRINCIPAL
st.markdown("""
    <div class="header-institucional">
        <h2 style="color: white; margin:0; font-size: 1.8rem;">CARABINEROS DE CHILE</h2>
        <h3 style="color: #C5A059; margin:0; font-size: 1.2rem;">SISTEMA F.R.I.D.A.Y. | PREFECTURA OCCIDENTE</h3>
    </div>
    """, unsafe_allow_html=True)

# 5. PESTAÑAS Y FORMULARIO
tab1, tab2, tab3 = st.tabs(["📄 ACTA STOP MENSUAL", "📈 STOP TRIMESTRAL", "📍 INFORME GEO"])

with tab1:
    with st.form("form_stop"):
        c1, c2 = st.columns(2)
        with c1:
            sem = st.text_input("Semana de estudio")
            fec = st.text_input("Fecha de sesión")
        with c2:
            comp = st.text_input("Compromiso Carabineros")
        
        prob = st.text_area("Problemática Delictual 26ª Comisaría")
        submit = st.form_submit_button("🛡️ PROCESAR ACTA MENSUAL") # Ahora será VERDE

    if submit:
        st.success("Analizando datos... Proceda con la descarga.")