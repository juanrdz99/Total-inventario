import pytesseract
from PIL import Image, ImageGrab
import re
import streamlit as st
import pandas as pd

# Ruta de Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.title("Power BI - Totales de Inventario")

st.write("📌 Puedes **subir una imagen** o **pegarla en el portapapeles** y luego darle clic al botón.")

# Subida normal
uploaded_file = st.file_uploader("Sube una imagen", type=["png", "jpg", "jpeg"])

# Botón para pegar desde portapapeles
if st.button("📋 Usar imagen del portapapeles"):
    try:
        img = ImageGrab.grabclipboard()
        if img is None:
            st.error("⚠️ No se encontró una imagen en el portapapeles. Usa Win+Shift+S y copia la tabla.")
        else:
            st.image(img, caption="Imagen pegada desde portapapeles", use_container_width=True)
            uploaded_file = img  # reutilizamos el flujo normal
    except Exception as e:
        st.error(f"Error al leer portapapeles: {e}")

# Procesamiento
if uploaded_file:
    if not isinstance(uploaded_file, Image.Image):
        img = Image.open(uploaded_file)
    else:
        img = uploaded_file

    text = pytesseract.image_to_string(img, config="--psm 6")

    filas_objetivo = ["LINEA", "RETRABAJO", "SFT", "STOCK"]
    suma_total = 0
    resultados = {}

    for linea in text.split("\n"):
        linea_norm = linea.upper().replace("0", "O")
        for fila in filas_objetivo:
            if fila in linea_norm:
                numeros = re.findall(r"\d[\d.,]*", linea)
                if numeros:
                    valor_str = numeros[-1].replace(".", "").replace(",", "")
                    try:
                        valor = int(valor_str)
                        resultados[fila] = valor
                        suma_total += valor
                    except ValueError:
                        pass

    st.write("### Resultados")
    if resultados:
        # Convertimos a DataFrame
        df = pd.DataFrame(list(resultados.items()), columns=["Concepto", "Valor"])
        df.loc[len(df)] = ["TOTAL", suma_total]

        # Mostrar tabla sin índice
        st.write(df.to_html(index=False), unsafe_allow_html=True)

        # También exportamos CSV descargable (para Excel)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Descargar resultados en CSV",
            data=csv,
            file_name="totales_inventario.csv",
            mime="text/csv",
        )

    else:
        st.warning("⚠️ No se detectaron las filas LINEA, RETRABAJO, SFT o STOCK en la imagen.")
