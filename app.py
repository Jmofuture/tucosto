"""
Modulo TuCosto
"""

import gspread
import polars as pl
import streamlit as st
from dotenv import load_dotenv
from google.auth.exceptions import DefaultCredentialsError

from services.google_sheets import read_sheet

# === CONFIGURACIÓN BASE ===
load_dotenv()

SHEET_ID = st.secrets["google"]["sheet_id"]
DEFAULT_SHEET_NAME = st.secrets["google"]["default_sheet_name"]
NAME = "Deliotti"

st.set_page_config(page_title="TuCosto App", layout="centered")

st.title(f"🧮 Bienvenido a TuCosto App, {NAME}")
st.write("Gestioná tus Material, cantidades y costos de forma simple y visual.")

st.sidebar.header("⚙️ Panel de control")
st.sidebar.text("Selecciona un material y agregalo 👇")

# === ESTADO DE SESIÓN ===
if "Material" not in st.session_state:
    st.session_state["Material"] = pl.DataFrame(
        {
            "Material": pl.Series([], dtype=pl.Utf8),
            "Cantidad": pl.Series([], dtype=pl.Int64),
            "Costo unitario": pl.Series([], dtype=pl.Float64),
            "Costo total": pl.Series([], dtype=pl.Float64),
        }
    )

# === LECTURA DE DATOS ===
try:
    df = read_sheet(SHEET_ID, DEFAULT_SHEET_NAME)

    # Validar columnas necesarias
    if all(col in df.columns for col in ["Materiales", "Costo"]):
        materiales = df["Materiales"].to_list()
        costos = df["Costo"].to_list()
        data_materiales = dict(zip(materiales, costos))

        # === SIDEBAR ===
        material_seleccionado = st.sidebar.selectbox("🧱 Material", materiales)
        cantidad = st.sidebar.number_input("🔢 Cantidad", min_value=1, step=1, value=1)

        costo_unitario = data_materiales.get(material_seleccionado, 0.0)
        costo_total = costo_unitario * cantidad

        st.sidebar.info(f"💲 Costo total: {costo_total:.2f}")

        if st.sidebar.button("➕ Agregar Material"):
            nuevo_Material = pl.DataFrame(
                {
                    "Material": [material_seleccionado],
                    "Cantidad": [cantidad],
                    "Costo unitario": [costo_unitario],
                    "Costo total": [costo_total],
                }
            )

            # Concatenar asegurando que ambos sean DataFrames válidos
            if st.session_state["Material"].height == 0:
                st.session_state["Material"] = nuevo_Material
            else:
                st.session_state["Material"] = pl.concat(
                    [st.session_state["Material"], nuevo_Material], how="vertical"
                )

            st.sidebar.success(f"✅ Material agregado: {material_seleccionado}")

    else:
        st.warning("No se encontraron las columnas 'Materiales' o 'Costo' en la hoja.")

except (gspread.exceptions.APIError, DefaultCredentialsError) as e:
    st.error(f"⚠️ No se pudieron cargar los datos de Google Sheets:\n{e}")

# === CONTENIDO PRINCIPAL ===
st.markdown("## 📋 Material agregados")

Material_df = st.session_state["Material"]

if Material_df.height > 0:
    st.dataframe(Material_df, use_container_width=True)

    total_general = Material_df["Costo total"].sum()
    st.markdown(f"### 💰 Total general: **${total_general:.2f}**")

    if st.button("🗑️ Vaciar Material"):
        st.session_state["Material"] = Material_df.head(0)
        st.success("Lista de Material vaciada correctamente.")
else:
    st.info("Todavía no agregaste ningún Material.")
