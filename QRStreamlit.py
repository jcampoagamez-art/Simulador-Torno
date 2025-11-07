import streamlit as st
import pandas as pd
import math
import io
import datetime

st.set_page_config(page_title="Simulador Torno", layout="centered")

st.title("Simulador de Operaciones de Torno (Web)")

with st.expander("Instrucciones", expanded=True):
    st.write("Carga un Excel (opcional) o ingresa parámetros. Pulsa Calcular. Puedes descargar resultados en Excel.")

# Subir archivo (opcional)
uploaded = st.file_uploader("Sube archivo Excel (opcional)", type=["xlsx","xls"])
df = None
if uploaded:
    try:
        df = pd.read_excel(uploaded)
        st.success("Excel cargado")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Error leyendo Excel: {e}")

# Entradas
st.subheader("Entradas")
col1, col2 = st.columns(2)
with col1:
    operacion = st.selectbox("Operación", ["Desbaste","Acabado","Careado"])
    material = st.selectbox("Material", ["Acero 1020","Acero inoxidable","Metal Monel"])
    Di = st.number_input("Diámetro inicial (mm)", value=60.0)
    Df = st.number_input("Diámetro final (mm)", value=50.0)
with col2:
    L = st.number_input("Longitud de corte (mm)", value=80.0)
    # tabla de velocidades por defecto
    veloc_table = {
        ("Desbaste","Acero 1020"):28, ("Desbaste","Acero inoxidable"):8, ("Desbaste","Metal Monel"):15,
        ("Acabado","Acero 1020"):40, ("Acabado","Acero inoxidable"):14, ("Acabado","Metal Monel"):18,
        ("Careado","Acero 1020"):28, ("Careado","Acero inoxidable"):8, ("Careado","Metal Monel"):18
    }
    default_vc = veloc_table.get((operacion, material), 28)
    Vc = st.number_input("Velocidad de corte Vc (m/min)", value=float(default_vc))
    f = st.number_input("Avance f (mm/rev)", value=0.32, format="%.4f")
    ap = st.number_input("Profundidad ap (mm)", value=1.0)

if st.button("Calcular"):
    if any(x == 0 for x in [Di, Df, L, Vc, f, ap]):
        st.error("Completa valores válidos distintos de cero.")
    else:
        D_trab = (Di + Df) / 2.0
        N = (1000 * Vc) / (math.pi * D_trab)
        Vf = f * N
        T = L / Vf
        npas = (Di - Df) / (2 * ap)
        Tt = npas * T

        res = {
            "Fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Operación": operacion,
            "Material": material,
            "Diámetro inicial (mm)": Di,
            "Diámetro final (mm)": Df,
            "Longitud (mm)": L,
            "Vc (m/min)": Vc,
            "f (mm/rev)": f,
            "ap (mm)": ap,
            "N (rpm)": round(N,2),
            "Vf (mm/min)": round(Vf,2),
            "T (min)": round(T,2),
            "n_p": round(npas,2),
            "Tt (min)": round(Tt,2)
        }

        st.success("Cálculo completado")
        st.json(res)

        # descarga a Excel
        df_out = pd.DataFrame([res])
        towrite = io.BytesIO()
       
        st.markdown(
    """
    ---
    **🛠️ Nota:**  
    Este proyecto está delimitado únicamente para procesos en el torno, con los tipos de materiales propuestos en la ventana de arriba.  
    Próximamente trabajaremos para agregar más procesos de mecanizado. 🙂
    """
)



