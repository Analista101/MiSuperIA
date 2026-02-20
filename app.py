import streamlit as st
from docxtpl import DocxTemplate, RichText
import io
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="F.R.I.D.A.Y. - 26ª Com. Pudahuel", page_icon="🟢", layout="wide")

# 2. ESTILO DE ALTA PRIORIDAD (CSS)
st.markdown("""
    <style>
    /* Fondo General */
    .stApp { background-color: #FFFFFF !important; }
    
    /* BARRA LATERAL: Fondo verde y TEXTO BLANCO */
    [data-testid="stSidebar"] {
        background-color: #004A2F !important;
    }
    /* Forzar texto de UNIDAD y labels a BLANCO */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] span {
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    /* BOTONES VERDES INSTITUCIONALES */
    div.stButton > button, .stFormSubmitButton > button {
        background-color: #004A2F !important;
        color: #FFFFFF !important;
        border: 2px solid #C5A059 !important;
        font-weight: bold !important;
        width: 100% !important;
        height: 3.5em !important;
    }

    /* PESTAÑAS (TABS) EN VERDE */
    .stTabs [data-baseweb="tab-list"] { background-color: #004A2F !important; border-radius: 5px; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; font-weight: bold !important; }
    .stTabs [aria-selected="true"] { background-color: #C5A059 !important; color: #000000 !important; }

    /* ENCABEZADO CENTRADO */
    .header-institucional {
        background-color: #004A2F;
        padding: 15px;
        border-radius: 10px;
        color: #FFFFFF !important;
        text-align: center;
        border: 2px solid #C5A059;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. BARRA LATERAL (Sidebar)
with st.sidebar:
    # Intento de carga de logo con URL directa y estable
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Logotipo_de_Carabineros_de_Chile.svg/800px-Logotipo_de_Carabineros_de_Chile.svg.png", width=140)
    
    st.markdown("### 🟢 CONFIGURACIÓN DE FIRMA")
    nombre_f = st.text_input("Nombre Oficial", value="DIANA SANDOVAL ASTUDILLO")
    grado_f = st.text_input("Grado", value="C.P.R. Analista Social")
    cargo_f = st.text_input("Cargo", value="OFICINA DE OPERACIONES")
    
    st.markdown("---")
    st.markdown("#### **UNIDAD:**")
    st.write("26ª Comisaría Pudahuel") # Este texto ahora será blanco por el CSS
    st.markdown(f"#### **FECHA:** {datetime.now().strftime('%d/%m/%Y')}")

# 4. ENCABEZADO PRINCIPAL
st.markdown("""
    <div class="header-institucional">
        <h2 style="color: white; margin:0; font-size: 1.8rem;">CARABINEROS DE CHILE</h2>
        <h3 style="color: #C5A059; margin:0; font-size: 1.2rem;">SISTEMA F.R.I.D.A.Y. | PREFECTURA OCCIDENTE</h3>
    </div>
    """, unsafe_allow_html=True)

# 5. LÓGICA DE FIRMA Y DOCUMENTO
def generar_word(nombre_plantilla, datos):
    try:
        doc = DocxTemplate(nombre_plantilla)
        # Formato de firma solicitado (Imagen image_25fb57)
        rt = RichText()
        rt.add(datos['n'].upper(), bold=True)
        rt.add('\n')
        rt.add(datos['g'], bold=False)
        rt.add('\n')
        rt.add(datos['c'].upper(), bold=True)
        datos['firma_completa'] = rt
        
        doc.render(datos)
        output = io.BytesIO()
        doc.save(output)
        return output.getvalue()
    except:
        return None

# 6. PESTAÑAS
tab1, tab2, tab3 = st.tabs(["📄 ACTA STOP MENSUAL", "📈 STOP TRIMESTRAL", "📍 INFORME GEO"])

with tab1:
    with st.form("form_mensual"):
        c1, c2 = st.columns(2)
        with c1:
            sem = st.text_input("Semana de estudio")
            fec = st.text_input("Fecha de sesión")
        with c2:
            comp = st.text_input("Compromiso Carabineros")
        
        prob = st.text_area("Problemática Delictual 26ª Comisaría")
        submit = st.form_submit_button("🛡️ PROCESAR ACTA MENSUAL")

    if submit:
        datos = {
            'semana': sem.upper(), 'fecha_sesion': fec.upper(),
            'c_carabineros': (comp if comp else "SIN COMPROMISO").upper(),
            'problematica': prob.upper(),
            'n': nombre_f, 'g': grado_f, 'c': cargo_f
        }
        archivo = generar_word("ACTA STOP MENSUAL.docx", datos)
        if archivo:
            st.download_button("⬇️ DESCARGAR WORD", archivo, f"ACTA_{sem}.docx")