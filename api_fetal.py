from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np

# 1. Definición de la aplicación
app = FastAPI(
    title="API de Predicción de Estado Fetal",
    description="API para la investigación de Cardiotocografía usando XGBoost",
    version="2.0"
)

# 2. Modelo de datos con tus 10 variables exactas
class FetalData(BaseModel):
    AC: float
    LB: float
    ASTV: float
    MSTV: float
    ALTV: float
    MLTV: float
    DP: float
    Mean: float
    Median: float
    Mode: float

# 3. Carga del Modelo (Sin escalador, según tu entrenamiento)
try:
    # Asegúrate de que el nombre coincida con el archivo que descargaste de Colab
    model = joblib.load('xgboost_model.joblib')
    print("✅ Modelo XGBoost cargado correctamente.")
except Exception as e:
    print(f"❌ Error al cargar el modelo: {e}")

@app.get("/")
def home():
    return {"mensaje": "API de Cardiotocografía activa. Usa el endpoint /predecir"}

# 5. Endpoint de Predicción
@app.post("/predecir")
def predecir(data: FetalData):
    try:
        # Convertir datos recibidos en un DataFrame
        # El orden de las columnas debe ser el MISMO que en el entrenamiento
        input_dict = data.dict()
        input_data = pd.DataFrame([input_dict])
        
        # ⚠️ IMPORTANTE: No usamos scaler.transform porque no escalaste en el entrenamiento.
        
        # Realizar la predicción
        # prediccion devolverá 0, 1 o 2 debido al 'y - 1' del entrenamiento
        prediccion_cruda = model.predict(input_data)
        probabilidades = model.predict_proba(input_data)
        
        # 4. REVERTIR EL AJUSTE (Sumar 1 para volver a los estados originales 1, 2, 3)
        resultado_nsp = int(prediccion_cruda[0]) + 1
        
        # Mapeo de significado
        estados = {1: "Normal", 2: "Sospechoso", 3: "Patologico"}
        
        return {
            "NSP": resultado_nsp,
            "estado": estados.get(resultado_nsp, "Desconocido"),
            "confianza": f"{round(np.max(probabilidades) * 100, 2)}%"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la predicción: {str(e)}")

# Para ejecutar: uvicorn api_fetal:app --reload