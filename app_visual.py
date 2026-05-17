import streamlit as st
import requests

# Configuración de la página
st.set_page_config(page_title="Predicción Riesgo Fetal", page_icon="👶")

st.title("👶 Sistema de Análisis de Cardiotocografía")
st.markdown("""
Ingrese los valores obtenidos del monitor fetal para predecir el estado de salud (NSP).
""")

# Crear dos columnas para que el formulario no sea tan largo
col1, col2 = st.columns(2)

with col1:
    lb = st.number_input("LB (Frecuencia Basal)", format="%.1f")
    ac = st.number_input("AC (Aceleraciones)", format="%.3f")
    astv = st.number_input("ASTV (% Tiempo Variabilidad Anormal)")
    mstv = st.number_input("MSTV (Variabilidad Media)")
    altv = st.number_input("ALTV (% Tiempo Variabilidad Alta)")

with col2:
    mltv = st.number_input("MLTV (Variabilidad Media Largo Plazo)")
    dp = st.number_input("DP (Desaceleraciones Prolongadas)", format="%.3f")
    mean = st.number_input("Mean (Media)")
    median = st.number_input("Median (Mediana)")
    mode = st.number_input("Mode (Moda)")

# Botón de predicción
if st.button("🔍 Predecir Estado Fetal"):
    # Preparar los datos para la API
    payload = {
        "AC": ac, "LB": lb, "ASTV": astv, "MSTV": mstv, "ALTV": altv,
        "MLTV": mltv, "DP": dp, "Mean": mean, "Median": median, "Mode": mode
    }
    
    try:
        # Llamada a tu API de FastAPI (asegúrate de que esté corriendo)
        response = requests.post("http://127.0.0.1:8000/predecir", json=payload)
        res = response.json()
        
        # Mostrar resultado con colores según el riesgo
        st.subheader(f"Resultado: {res['estado']}")
        confianza_str = str(res['confianza']).replace('%', '')
        confianza_num = float(confianza_str)

        if res['NSP'] == 1:
            st.success(f"Estado Normal (Confianza: {confianza_num:.2f}%)")
        elif res['NSP'] == 2:
            st.warning(f"Estado Sospechoso (Confianza: {confianza_num:.2f}%)")
        else:
            st.error(f"Estado Patológico (Confianza: {confianza_num:.2f}%)")
            
    except Exception as e:
        st.error(f"No se pudo conectar con la API. ¿Está encendida? Error: {e}")

#Lo ejecutas con: streamlit run app_visual.py