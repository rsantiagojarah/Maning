import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from scipy.optimize import fsolve
import os

def calcular_propiedades_hidraulicas(Q, D, n, S):
    try:
        g = 9.81  # Aceleración gravitacional (m/s^2)
        R = D / 2  # Radio de la tubería (m)
        
        def ecuacion_manning(y):
            """Ecuación de Manning para una tubería parcialmente llena."""
            # Validar que y esté en el rango válido (0 < y < D)
            if y <= 0 or y >= 2 * R:
                return float('inf')
            
            A = area_hidraulica(y, R)
            P = perimetro_mojado(y, R)
            if P == 0:
                return float('inf')
            Rh = A / P
            return (1 / n) * A * (Rh ** (2/3)) * (S ** 0.5) - Q
        
        def area_hidraulica(y, R):
            """Calcula el área hidráulica de la sección."""
            # Validar entrada para evitar errores en arccos
            if y <= 0:
                return 0
            if y >= 2 * R:
                return np.pi * R ** 2  # Área completa de la tubería
            
            cos_val = 1 - y / R
            # Asegurar que el valor esté en el rango válido para arccos
            cos_val = np.clip(cos_val, -1, 1)
            theta = 2 * np.arccos(cos_val)
            return (R ** 2) * (theta - np.sin(theta)) / 2
        
        def perimetro_mojado(y, R):
            """Calcula el perímetro mojado."""
            # Validar entrada para evitar errores en arccos
            if y <= 0:
                return 0
            if y >= 2 * R:
                return 2 * np.pi * R  # Perímetro completo de la tubería
            
            cos_val = 1 - y / R
            # Asegurar que el valor esté en el rango válido para arccos
            cos_val = np.clip(cos_val, -1, 1)
            theta = 2 * np.arccos(cos_val)
            return R * theta
        
        def espejo_agua(y, R):
            """Calcula el ancho del espejo de agua."""
            if y <= 0:
                return 0
            if y >= 2 * R:
                return 0  # Tubería completamente llena, no hay espejo de agua
            
            discriminant = 2 * R * y - y ** 2
            if discriminant < 0:
                return 0
            return 2 * np.sqrt(discriminant)
        
        # Solución para el tirante normal con mejor valor inicial
        y_inicial = R * 0.7  # Usar un valor inicial que represente aprox. 70% del radio
        
        try:
            y_normal = fsolve(ecuacion_manning, y_inicial, xtol=1e-12)[0]
        except:
            # Si falla, intentar con diferentes valores iniciales
            for factor in [0.1, 0.3, 0.7, 0.9]:
                try:
                    y_inicial = R * factor
                    y_normal = fsolve(ecuacion_manning, y_inicial, xtol=1e-12)[0]
                    break
                except:
                    continue
            else:
                raise ValueError("No se pudo encontrar solución para el tirante normal")
        
        # Validar que la solución sea física
        if y_normal <= 0 or y_normal >= 2 * R:
            raise ValueError("Solución no física para el tirante normal")
        
        A = area_hidraulica(y_normal, R)
        P = perimetro_mojado(y_normal, R)
        Rh = A / P
        V = Q / A  # Velocidad media
        T = espejo_agua(y_normal, R)  # Ancho del espejo de agua
        
        # Número de Froude para tuberías circulares: Fr = V / sqrt(g * Rh)
        Fr = V / np.sqrt(g * Rh)
        
        return {
            "Tirante Normal (m)": round(y_normal, 4),
            "Área Hidráulica (m²)": round(A, 4),
            "Espejo de Agua (m)": round(T, 4),
            "Número de Froude": round(Fr, 4),
            "Perímetro Mojado (m)": round(P, 4),
            "Radio Hidráulico (m)": round(Rh, 4),
            "Velocidad (m/s)": round(V, 4)
        }
    
    except Exception as e:
        # Retornar valores de error si no se puede calcular
        return {
            "Tirante Normal (m)": "ERROR",
            "Área Hidráulica (m²)": "ERROR",
            "Espejo de Agua (m)": "ERROR",
            "Número de Froude": "ERROR",
            "Perímetro Mojado (m)": "ERROR",
            "Radio Hidráulico (m)": "ERROR",
            "Velocidad (m/s)": "ERROR",
            "Error": str(e)
        }

# Ventana para seleccionar archivo de entrada
root = tk.Tk()
root.withdraw()

try:
    archivo_entrada = filedialog.askopenfilename(
        title="Seleccione el archivo de datos", 
        filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
    )
    
    if not archivo_entrada:
        messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo")
        exit()

    # Leer datos
    if archivo_entrada.endswith(".csv"):
        df = pd.read_csv(archivo_entrada)
    elif archivo_entrada.endswith(".xlsx"):
        df = pd.read_excel(archivo_entrada)
    else:
        messagebox.showerror("Error", "Formato de archivo no soportado")
        exit()

    # Verificar que las columnas necesarias estén presentes
    columnas_necesarias = ["Caudal", "Diametro", "Rugosidad", "Pendiente"]
    columnas_faltantes = [col for col in columnas_necesarias if col not in df.columns]
    
    if columnas_faltantes:
        messagebox.showerror("Error", f"Faltan las siguientes columnas: {', '.join(columnas_faltantes)}")
        exit()

    # Iterar sobre las filas y calcular propiedades
    resultados = []
    for _, row in df.iterrows():
        resultado = calcular_propiedades_hidraulicas(
            row["Caudal"], 
            row["Diametro"], 
            row["Rugosidad"], 
            row["Pendiente"]
        )
        resultados.append({**row, **resultado})

    # Convertir a DataFrame
    df_resultado = pd.DataFrame(resultados)

    # Ventana para seleccionar archivo de salida
    archivo_salida = filedialog.asksaveasfilename(
        title="Guardar archivo de resultados", 
        defaultextension=".csv", 
        filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
    )
    
    if not archivo_salida:
        messagebox.showwarning("Advertencia", "No se seleccionó archivo de salida")
        exit()

    # Verificar permisos de escritura
    directorio = os.path.dirname(archivo_salida)
    if not os.access(directorio, os.W_OK):
        messagebox.showerror("Error", f"No hay permisos de escritura en el directorio: {directorio}")
        exit()

    # Verificar si el archivo ya existe y está abierto
    if os.path.exists(archivo_salida):
        try:
            # Intentar abrir el archivo para verificar si está en uso
            with open(archivo_salida, 'r+'):
                pass
        except PermissionError:
            messagebox.showerror("Error", f"El archivo {archivo_salida} está abierto en otra aplicación. Ciérrelo e intente nuevamente.")
            exit()

    # Guardar archivo
    try:
        if archivo_salida.endswith(".csv"):
            df_resultado.to_csv(archivo_salida, index=False)
        elif archivo_salida.endswith(".xlsx"):
            df_resultado.to_excel(archivo_salida, index=False)
        
        messagebox.showinfo("Éxito", f"Archivo guardado exitosamente en: {archivo_salida}")
        
    except PermissionError:
        messagebox.showerror("Error", "Error de permisos al guardar el archivo. Verifique que no esté abierto en otra aplicación.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al guardar el archivo: {str(e)}")

except Exception as e:
    messagebox.showerror("Error", f"Error general: {str(e)}")

finally:
    root.destroy()
