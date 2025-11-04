"""
Módulo Google Sheets para TuCosto App
-------------------------------------

Provee funciones para leer y actualizar hojas de Google Sheets usando
una cuenta de servicio. Adaptado para Streamlit Cloud usando `st.secrets`.
Los datos se devuelven como Polars DataFrame para un manejo eficiente
de información en la app.
"""

import json

import gspread
import polars as pl
import streamlit as st
from google.oauth2.service_account import Credentials

# ===========================
# Configuración de permisos
# ===========================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# ===========================
# Cliente de Google Sheets
# ===========================
@st.cache_resource
def get_gsheet_client() -> gspread.Client:
    """
    Inicializa y devuelve un cliente autenticado de Google Sheets usando
    la cuenta de servicio cargada desde Streamlit Secrets.

    Returns
    -------
    gspread.Client
        Cliente autenticado listo para interactuar con la API de Google Sheets.
    """
    try:
        service_account_info = json.loads(st.secrets["google"]["service_account_json"])
        creds = Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES
        )
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"No se pudo autenticar el cliente de Google Sheets: {e}")
        raise


# ===========================
# Lectura de hojas
# ===========================
@st.cache_data(ttl=300)
def read_sheet(sheet_id: str, sheet_name: str = "Hoja 1") -> pl.DataFrame:
    """
    Lee los datos de una hoja específica de Google Sheets y devuelve un
    DataFrame de Polars.

    Parameters
    ----------
    sheet_id : str
        ID único del documento de Google Sheets
    sheet_name : str, optional
        Nombre de la hoja dentro del documento, por defecto "Hoja 1"

    Returns
    -------
    pl.DataFrame
        DataFrame de Polars con los datos leídos desde la hoja especificada.
    """
    try:
        client = get_gsheet_client()
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        data = sheet.get_all_records()
        return pl.DataFrame(data)
    except Exception as e:
        st.error(f"No se pudo leer la hoja '{sheet_name}': {e}")
        return pl.DataFrame([])


# ===========================
# Agregar filas
# ===========================
def append_row(sheet_id: str, row: list, sheet_name: str = "Hoja 1"):
    """
    Agrega una nueva fila al final de una hoja específica en Google Sheets.

    Parameters
    ----------
    sheet_id : str
        ID único del documento de Google Sheets
    row : list
        Lista de valores que se insertarán como una nueva fila
    sheet_name : str, optional
        Nombre de la hoja dentro del documento, por defecto "Hoja 1"
    """
    try:
        client = get_gsheet_client()
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        # Convertir todo a string para evitar errores
        row_str = [str(cell) for cell in row]
        sheet.append_row(row_str)
    except Exception as e:
        st.error(f"No se pudo agregar la fila a '{sheet_name}': {e}")


# ===========================
# Testeo local (opcional)
# ===========================
if __name__ == "__main__":
    try:
        sid = st.secrets["google"]["sheet_id"]
        sheet_to_read = st.secrets["google"].get("sheet_name", "Hoja 1")
        df = read_sheet(sid, sheet_to_read)
        print(df)
    except Exception as e:
        print(f"No se pudo cargar la hoja: {e}")
