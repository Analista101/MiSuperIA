import streamlit as st
from docxtpl import DocxTemplate, RichText
import io
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="F.R.I.D.A.Y. - 26ª Com. Pudahuel", page_icon="🟢", layout="wide")

# 2. ESTILO DE FUERZA BRUTA (CSS) - Prioridad Máxima
st.markdown("""
    <style>
    /* 1. BARRA LATERAL: FONDO VERDE Y TODO EL TEXTO BLANCO */
    [data-testid="stSidebar"] {
        background-color: #004A2F !important;
    }
    /* Selector específico para el texto de la unidad y labels en sidebar */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    /* 2. BOTONES VERDES INSTITUCIONALES (Selectores múltiples para asegurar el color) */
    div.stButton > button, div.stFormSubmitButton > button {
        background-color: #004A2F !important;
        color: #FFFFFF !important;
        border: 2px solid #C5A059 !important;
        font-weight: bold !important;
        width: 100% !important;
        height: 3.5em !important;
        border-radius: 8px !important;
    }
    
    /* Efecto al pasar el mouse por el botón */
    div.stButton > button:hover {
        background-color: #006341 !important;
        border-color: #FFFFFF !important;
    }

    /* 3. ENCABEZADO CENTRADO */
    .header-institucional {
        background-color: #004A2F;
        padding: 20px;
        border-radius: 10px;
        color: #FFFFFF !important;
        text-align: center;
        border: 3px solid #C5A059;
        margin-bottom: 25px;
    }

    /* 4. TEXTO CUERPO (Fondo blanco): Verde y grueso */
    .stApp label, .stMarkdown p, .stTextArea label {
        color: #004A2F !important;
        font-weight: 800 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. BARRA LATERAL
with st.sidebar:
    # Logo usando un enlace de respaldo altamente confiable
    st.image("https://raw.githubusercontent.com/F-R-I-D-A-Y-Analyst/Project/main/logo.png", width=150, caption="") 
    # Si el de arriba falla, este es el oficial de Wikimedia
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Logotipo_de_Carabineros_de_Chile.svg/300px-Logotipo_de_Carabineros_de_Chile.svg.png")

    st.markdown("### 🟢 CONFIGURACIÓN DE FIRMA")
    nombre_f = st.text_input("Nombre Oficial", value="KARINA JOFRE RICKENBERG")
    grado_f = st.text_input("Grado", value="Capitán de Carabineros")
    cargo_f = st.text_input("Cargo", value="COMISARIO (S)")
    st.markdown("---")
    st.markdown("#### **UNIDAD:**")
    st.markdown("26ª Comisaría Pudahuel") # Este texto ahora será blanco
    st.markdown(f"#### **FECHA:**\n{datetime.now().strftime('%d/%m/%Y')}")

# 4. CUERPO PRINCIPAL
st.markdown("""
    <div class="header-institucional">
        <h1 style="color: white; margin:0;">CARABINEROS DE CHILE</h1>
        <h3 style="color: #C5A059; margin:0;">SISTEMA F.R.I.D.A.Y. | PREFECTURA OCCIDENTE</h3>
    </div>
    """, unsafe_allow_html=True)

# 5. PESTAÑAS
tab1, tab2, tab3 = st.tabs(["📄 ACTA STOP MENSUAL", "📈 STOP TRIMESTRAL", "📍 INFORME GEO"])

with tab1:
    with st.form("form_acta"):
        st.markdown("### 📝 FORMULARIO: ACTA DE SESIÓN MENSUAL")
        col1, col2 = st.columns(2)
        with col1:
            sem = st.text_input("Semana de estudio")
            fec = st.text_input("Fecha de sesión")
        with col2:
            comp = st.text_input("Compromisos Institucionales")
        
        prob = st.text_area("Problemáticas Delictuales Analizadas")
        # El botón aquí será VERDE por el CSS arriba
        submit = st.form_submit_button("🛡️ PROCESAR Y GENERAR")

    if submit:
        # Lógica de firma con formato de imagen
        st.success("Documento procesado. El botón de descarga aparecerá a continuación.")
        # Aquí iría la función de generar_word que ya tenemos.