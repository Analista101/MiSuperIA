import streamlit as st
from docxtpl import DocxTemplate
import io
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="F.R.I.D.A.Y. - 26ª Com. Pudahuel", page_icon="🟢", layout="wide")

# 2. ESTILO TÁCTICO (CSS)
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #004A2F !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; font-weight: bold !important; }
    .header-institucional {
        background-color: #004A2F;
        padding: 15px;
        border-radius: 10px;
        color: #FFFFFF !important;
        text-align: center;
        border: 2px solid #C5A059;
    }
    label, .stMarkdown p, .stTextInput label, .stTextArea label {
        color: #004A2F !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
    }
    div.stButton > button {
        background-color: #004A2F !important;
        color: #FFFFFF !important;
        border: 2px solid #C5A059 !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. BARRA LATERAL CON CONFIGURACIÓN DE FIRMA
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a2/Logotipo_de_Carabineros_de_Chile.svg", width=120)
    st.markdown("### 🟢 CONFIGURACIÓN DE FIRMA")
    # CAMPOS QUE USTED SOLICITÓ PARA PERSONALIZAR LA FIRMA
    nombre_firma = st.text_input("Nombre del Oficial", value="DIANA SANDOVAL ASTUDILLO")
    grado_firma = st.text_input("Grado", value="C.P.R. Analista Social")
    cargo_firma = st.text_input("Cargo", value="OFICINA DE OPERACIONES")
    st.markdown("---")
    st.write(f"**UNIDAD:** 26ª Com. Pudahuel")

# 4. ENCABEZADO
st.markdown("""
    <div class="header-institucional">
        <h2 style="color: white; margin:0; font-size: 1.8rem;">CARABINEROS DE CHILE</h2>
        <h3 style="color: #C5A059; margin:0; font-size: 1.2rem;">SISTEMA F.R.I.D.A.Y. | PREFECTURA OCCIDENTE</h3>
    </div>
    """, unsafe_allow_html=True)

# 5. LÓGICA DE GENERACIÓN
def generar_word(nombre_plantilla, datos):
    try:
        doc = DocxTemplate(nombre_plantilla)
        # Fecha en formato institucional
        fecha_larga = datetime.now().strftime('%d de %B de %Y')
        datos['fecha_fondo'] = f"Pudahuel, {fecha_larga}".upper()
        
        doc.render(datos)
        output = io.BytesIO()
        doc.save(output)
        return output.getvalue()
    except:
        st.error(f"Error técnico: Verifique que '{nombre_plantilla}' esté en su GitHub.")
        return None

# 6. PESTAÑAS
tab1, tab2, tab3 = st.tabs(["📄 ACTA STOP MENSUAL", "📈 STOP TRIMESTRAL", "📍 INFORME GEO"])

with tab1:
    with st.form("form_mensual"):
        c1, c2 = st.columns(2)
        with c1:
            semana = st.text_input("Semana de estudio")
            fecha_sesion = st.text_input("Fecha de sesión")
        with c2:
            c_carabineros = st.text_input("Compromiso Carabineros")
        
        problematica = st.text_area("Problemática Delictual 26ª Comisaría")
        submit_mensual = st.form_submit_button("🛡️ PROCESAR ACTA MENSUAL")

    if submit_mensual:
        # Se captura la firma de la barra lateral y se pasa a MAYÚSCULAS
        datos = {
            'semana': semana.upper(),
            'fecha_sesion': fecha_sesion.upper(),
            'c_carabineros': (c_carabineros if c_carabineros else "SIN COMPROMISO").upper(),
            'problematica': problematica.upper(),
            'nom_oficial': nombre_firma.upper(),
            'grado_oficial': grado_firma.upper(),
            'cargo_oficial': cargo_firma.upper()
        }
        archivo = generar_word("ACTA STOP MENSUAL.docx", datos)
        if archivo:
            st.download_button(label="⬇️ DESCARGAR ACTA", data=archivo, file_name=f"ACTA_STOP_{semana}.docx")

# Los otros módulos (Trimestral y GEO) usarán las mismas variables nombre_firma, grado_firma, etc.