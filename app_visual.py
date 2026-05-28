import streamlit as st
import requests

# =========================================
# CONFIGURACIÓN DE LA PÁGINA
# =========================================
st.set_page_config(
    page_title="Predicción Riesgo Fetal",
    page_icon="👶",
    layout="wide"
)

# =========================================
# OCULTAR BOTONES DE NUMBER_INPUT (CSS)
# =========================================
ocultar_botones_css = """
<style>
[data-testid="stNumberInputStepDown"] {
    display: none !important;
}
[data-testid="stNumberInputStepUp"] {
    display: none !important;
}
</style>
"""
st.markdown(ocultar_botones_css, unsafe_allow_html=True)

# =========================================
# TÍTULO
# =========================================
st.title("👶 Sistema de Análisis de Cardiotocografía")
st.markdown("""
Ingrese los valores obtenidos del monitor fetal para predecir el estado de salud fetal.
""")

# =========================================
# CONTENEDOR PARA EL MENSAJE DE EJEMPLO
# =========================================
mensaje_ejemplo = st.empty()

# =========================================
# FORMULARIO
# =========================================
col1, col2 = st.columns(2)

# Agregamos el atributo 'placeholder' a cada campo con sus respectivos valores
with col1:
    lb = st.number_input("LB (Frecuencia Basal)", format="%.1f", value=None, placeholder="120")
    ac = st.number_input("AC (Aceleraciones)", format="%.3f", value=None, placeholder="0")
    astv = st.number_input("ASTV (% Tiempo Variabilidad Anormal)", format="%.1f", value=None, placeholder="73")
    mstv = st.number_input("MSTV (Variabilidad Media)", format="%.2f", value=None, placeholder="0.5")
    altv = st.number_input("ALTV (% Tiempo Variabilidad Alta)", format="%.1f", value=None, placeholder="43")

with col2:
    mltv = st.number_input("MLTV (Variabilidad Media Largo Plazo)", format="%.2f", value=None, placeholder="2.4")
    dp = st.number_input("DP (Desaceleraciones Prolongadas)", format="%.3f", value=None, placeholder="0")
    mean = st.number_input("Mean (Media)", format="%.2f", value=None, placeholder="137")
    median = st.number_input("Median (Mediana)", format="%.2f", value=None, placeholder="121")
    mode = st.number_input("Mode (Moda)", format="%.2f", value=None, placeholder="120")

# Agrupamos todos los valores para evaluar si están vacíos
valores_inputs = [lb, ac, astv, mstv, altv, mltv, dp, mean, median, mode]

# =========================================
# BOTÓN DE PREDICCIÓN
# =========================================
if st.button("🔍 Predecir Estado Fetal"):
    
    # Validación: Verificar que no falten datos antes de enviar a la API
    if any(v is None for v in valores_inputs):
        st.warning("⚠️ Por favor, complete todos los campos numéricos antes de predecir.")
    else:
        # Datos enviados a la API
        payload = {
            "AC": ac,
            "LB": lb,
            "ASTV": astv,
            "MSTV": mstv,
            "ALTV": altv,
            "MLTV": mltv,
            "DP": dp,
            "Mean": mean,
            "Median": median,
            "Mode": mode
        }

        try:
            # =========================================
            # URL DE TU API EN RENDER
            # =========================================
            API_URL = "https://apifetal.onrender.com/predecir"

            # Enviar datos
            response = requests.post(API_URL, json=payload)

            # Verificar respuesta
            if response.status_code == 200:
                res = response.json()
                st.divider()

                # =========================================
                # RESULTADO
                # =========================================
                st.subheader("📊 Resultado del Análisis")

                estado = res["estado"]
                nsp = res["NSP"]

                confianza_str = str(res["confianza"]).replace("%", "")
                confianza_num = float(confianza_str)

                # =========================================
                # MOSTRAR RESULTADO SEGÚN EL RIESGO
                # =========================================
                if nsp == 1:
                    st.success(
                        f"""
                        ✅ Estado Normal
                        
                        Confianza del modelo: {confianza_num:.2f}%
                        """
                    )
                elif nsp == 2:
                    st.warning(
                        f"""
                        ⚠️ Estado Sospechoso
                        
                        Confianza del modelo: {confianza_num:.2f}%
                        """
                    )
                else:
                    st.error(
                        f"""
                        🚨 Estado Patológico
                        
                        Confianza del modelo: {confianza_num:.2f}%
                        """
                    )

                # Mostrar datos extra
                st.info(f"Clasificación obtenida: {estado}")

            else:
                st.error(f"Error en la API: {response.status_code}")

        except Exception as e:
            st.error(f"No se pudo conectar con la API.\n\nError: {e}")

# =========================================
# FOOTER
# =========================================
st.markdown("---")
st.caption("Sistema Inteligente de Predicción de Riesgo Fetal con FastAPI + Streamlit + XGBoost")
