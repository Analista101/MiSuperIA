import streamlit as st
from docxtpl import DocxTemplate, RichText
import io
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="F.R.I.D.A.Y. - 26ª Com. Pudahuel", page_icon="🟢", layout="wide")

# 2. ESTILO TÁCTICO DE ALTA VISIBILIDAD (CSS)
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #FFFFFF !important; }
    
    /* BARRA LATERAL: Fondo verde y texto BLANCO CRÍTICO */
    [data-testid="stSidebar"] {
        background-color: #004A2F !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important; /* Forza todo a blanco en la barra lateral */
        font-weight: bold !important;
    }

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
    
    /* LETRAS CUERPO: VERDE OSCURO Y GRUESAS */
    label, .stMarkdown p, .stTextInput label, .stTextArea label, .stTabs [data-baseweb="tab"] {
        color: #004A2F !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
    }

    /* BOTONES VERDES INSTITUCIONALES */
    div.stButton > button {
        background-color: #004A2F !important;
        color: #FFFFFF !important;
        border: 2px solid #C5A059 !important;
        font-weight: bold !important;
        width: 100% !important;
        height: 3.5em !important;
    }
    
    /* Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] { background-color: #004A2F; border-radius: 5px; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; }
    .stTabs [aria-selected="true"] { background-color: #C5A059 !important; color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. BARRA LATERAL (Logo y Datos en Blanco)
with st.sidebar:
    # Fuente de logo de respaldo estable
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Logotipo_de_Carabineros_de_Chile.svg/640px-Logotipo_de_Carabineros_de_Chile.svg.png", width=130)
    st.markdown("### 🟢 CONFIGURACIÓN DE FIRMA")
    nombre_f = st.text_input("Oficial (Línea 1)", value="KARINA JOFRE RICKENBERG")
    grado_f = st.text_input("Grado (Línea 2)", value="Capitán de Carabineros")
    cargo_f = st.text_input("Cargo (Línea 3)", value="COMISARIO (S)")
    st.markdown("---")
    st.markdown("#### **UNIDAD:**\n26ª Comisaría Pudahuel")
    st.markdown(f"#### **FECHA:**\n{datetime.now().strftime('%d/%m/%Y')}")

# 4. ENCABEZADO PRINCIPAL
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
        # Formato de firma según imagen enviada
        rt = RichText()
        rt.add(datos['n'].upper(), bold=True)
        rt.add('\n')
        rt.add(datos['g'], bold=False)
        rt.add('\n')
        rt.add(datos['c'].upper(), bold=True)
        datos['firma_completa'] = rt
        
        # Fecha fondo
        now = datetime.now()
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        datos['fecha_fondo'] = f"PUDAHUEL, {now.day} DE {meses[now.month-1].upper()} DE {now.year}"
        
        doc.render(datos)
        output = io.BytesIO()
        doc.save(output)
        return output.getvalue()
    except:
        st.error(f"Error: Asegúrese de que '{nombre_plantilla}' esté en GitHub.")
        return None

# 6. PESTAÑAS
tab1, tab2, tab3 = st.tabs(["📄 ACTA STOP MENSUAL", "📈 STOP TRIMESTRAL", "📍 INFORME GEO"])

with tab1:
    with st.form("form_m"):
        st.markdown("### 📝 FORMULARIO: ACTA DE SESIÓN MENSUAL")
        c1, c2 = st.columns(2)
        with c1:
            sem = st.text_input("Semana de estudio")
            fec = st.text_input("Fecha de sesión")
        with c2:
            comp = st.text_input("Compromisos Institucionales")
        
        prob = st.text_area("Problemáticas Delictuales (26ª Comisaría)")
        btn = st.form_submit_button("🛡️ PROCESAR ACTA")

    if btn:
        datos_m = {
            'semana': sem.upper(),
            'fecha_sesion': fec.upper(),
            'c_carabineros': (comp if comp else "SIN COMPROMISO").upper(),
            'problematica': prob.upper(),
            'n': nombre_f, 'g': grado_f, 'c': cargo_f
        }
        archivo = generar_word("ACTA STOP MENSUAL.docx", datos_m)
        if archivo:
            st.download_button("⬇️ DESCARGAR ACTA (WORD)", archivo, f"ACTA_{sem}.docx")