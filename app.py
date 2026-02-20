import streamlit as st
from docxtpl import DocxTemplate, RichText
import io
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="F.R.I.D.A.Y. - 26ª Com. Pudahuel", page_icon="🟢", layout="wide")

# 2. ESTILO TÁCTICO (Restauración de Botones Verdes y Diseño Centrado)
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #FFFFFF !important; }
    
    /* BARRA LATERAL VERDE */
    [data-testid="stSidebar"] { background-color: #004A2F !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; font-weight: bold !important; }

    /* ENCABEZADO CENTRADO */
    .header-institucional {
        background-color: #004A2F;
        padding: 15px;
        border-radius: 10px;
        color: #FFFFFF !important;
        text-align: center;
        border: 2px solid #C5A059;
    }
    
    /* LETRAS CUERPO: VERDE OSCURO Y GRUESAS */
    label, .stMarkdown p, .stTextInput label, .stTextArea label {
        color: #004A2F !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
    }

    /* BOTONES VERDES CON LETRA BLANCA (RESTAURADOS) */
    div.stButton > button {
        background-color: #004A2F !important;
        color: #FFFFFF !important;
        border: 2px solid #C5A059 !important;
        font-weight: bold !important;
        width: 100%;
        height: 3em;
    }
    
    /* PESTAÑAS */
    .stTabs [data-baseweb="tab-list"] { background-color: #004A2F; border-radius: 5px; }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #C5A059 !important; color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. BARRA LATERAL
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a2/Logotipo_de_Carabineros_de_Chile.svg", width=120)
    st.markdown("### 🟢 CONFIGURACIÓN DE FIRMA")
    nombre_input = st.text_input("Nombre del Oficial", value="KARINA JOFRE RICKENBERG")
    grado_input = st.text_input("Grado (Minúsculas)", value="Capitán de Carabineros")
    cargo_input = st.text_input("Cargo", value="COMISARIO (S)")
    st.markdown("---")
    st.write("26ª Comisaría Pudahuel")

# 4. ENCABEZADO
st.markdown("""
    <div class="header-institucional">
        <h2 style="color: white; margin:0; font-size: 1.8rem;">CARABINEROS DE CHILE</h2>
        <h3 style="color: #C5A059; margin:0; font-size: 1.2rem;">SISTEMA F.R.I.D.A.Y. | PREFECTURA OCCIDENTE</h3>
    </div>
    """, unsafe_allow_html=True)

# 5. LÓGICA DE GENERACIÓN CON FORMATO DE FIRMA
def generar_word(nombre_plantilla, datos):
    try:
        doc = DocxTemplate(nombre_plantilla)
        
        # Aplicamos el formato especial de firma usando RichText para el Word
        rt_nombre = RichText(datos['nombre'].upper(), bold=True)
        rt_grado = RichText(datos['grado'], bold=False)
        rt_cargo = RichText(datos['cargo'].upper(), bold=True)
        
        # Unimos las piezas para el Word
        datos['firma_completa'] = f"{rt_nombre}\n{rt_grado}\n{rt_cargo}"
        
        # Fecha fondo
        fecha_larga = datetime.now().strftime('%d de %B de %Y')
        datos['fecha_fondo'] = f"Pudahuel, {fecha_larga}".upper()
        
        doc.render(datos)
        output = io.BytesIO()
        doc.save(output)
        return output.getvalue()
    except:
        st.error(f"Error: Asegúrese de tener '{nombre_plantilla}' en GitHub.")
        return None

# 6. PESTAÑAS
tab1, tab2, tab3 = st.tabs(["📄 ACTA STOP MENSUAL", "📈 STOP TRIMESTRAL", "📍 INFORME GEO"])

with tab1:
    with st.form("form_mensual"):
        c1, c2 = st.columns(2)
        with c1:
            semana = st.text_input("Semana de estudio")
            fecha_s = st.text_input("Fecha de sesión")
        with c2:
            c_carab = st.text_input("Compromiso Carabineros")
        
        prob = st.text_area("Problemática Delictual 26ª Comisaría")
        submit_mensual = st.form_submit_button("🛡️ PROCESAR ACTA MENSUAL")

    if submit_mensual:
        datos = {
            'semana': semana.upper(),
            'fecha_sesion': fecha_s.upper(),
            'c_carabineros': (c_carab if c_carab else "SIN COMPROMISO").upper(),
            'problematica': prob.upper(),
            'nombre': nombre_input,
            'grado': grado_input,
            'cargo': cargo_input
        }
        archivo = generar_word("ACTA STOP MENSUAL.docx", datos)
        if archivo:
            st.download_button(label="⬇️ DESCARGAR ACTA", data=archivo, file_name=f"ACTA_STOP_{semana}.docx")