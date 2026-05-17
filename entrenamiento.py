import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

def ejecutar_entrenamiento():
    # 1. CARGA DE DATOS
    path = 'DATA.csv'
    df = pd.read_csv(path, sep=';')
    df = df.dropna()

    # 2. SELECCIÓN DE VARIABLES CLAVE (Las 10 más relevantes para CTG)
    # Seleccionamos una mezcla de frecuencia basal, eventos y variabilidad
    variables_clave = [
        'LB',       # Frecuencia Basal
        'AC',       # Aceleraciones
        'UC',       # Contracciones
        'ASTV',     # Variabilidad corta (%)
        'MSTV',     # Variabilidad corta (valor medio)
        'ALTV',     # Variabilidad larga (%)
        'MLTV',     # Variabilidad larga (valor medio)
        'DP',       # Desaceleraciones prolongadas (Crítico para patologías)
        'Mean',     # Media de la FHR
        'Median'    # Mediana de la FHR
    ]
    
    X = df[variables_clave]
    y = df['NSP']

    # 3. DIVISIÓN DE DATOS
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. ESCALADO (Vital para que la API no falle)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 5. ENTRENAMIENTO CON BALANCEO
    # class_weight='balanced' corrige el error de que siempre prediga 1
    model = RandomForestClassifier(
        n_estimators=150, 
        random_state=42, 
        class_weight='balanced',
        max_depth=10
    )
    model.fit(X_train_scaled, y_train)

    # 6. EVALUACIÓN RÁPIDA
    y_pred = model.predict(X_test_scaled)
    print("--- Informe de Clasificación ---")
    print(classification_report(y_test, y_pred))

    # 7. GUARDAR ARCHIVOS
    joblib.dump(model, 'modelo_fetal.pkl')
    joblib.dump(scaler, 'scaler_fetal.pkl')
    print("\nÉxito: 'modelo_fetal.pkl' y 'scaler_fetal.pkl' creados.")

if __name__ == "__main__":
    ejecutar_entrenamiento()