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
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound

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
def get_gsheet_client():
    """
    Inicializa y devuelve un cliente autenticado de Google Sheets usando
    la cuenta de servicio cargada desde Streamlit Secrets.

    Returns
    -------
    gspread.Client
        Cliente autenticado listo para interactuar con Google Sheets.
    """
    try:
        service_account_info = json.loads(st.secrets["google"]["service_account_json"])
        creds = Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES
        )
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"No se pudo autenticar la cuenta de servicio: {e}")
        raise


# ===========================
# Listar hojas (opcional)
# ===========================
def list_sheets(sheet_id: str):
    """
    Devuelve los nombres de todas las hojas de un documento.
    """
    client = get_gsheet_client()
    try:
        sh = client.open_by_key(sheet_id)
        return [ws.title for ws in sh.worksheets()]
    except SpreadsheetNotFound:
        st.error(f"No se encontró la hoja con ID {sheet_id}")
        return []
    except Exception as e:
        st.error(f"Error al listar hojas: {e}")
        return []


# ===========================
# Lectura de hojas
# ===========================
@st.cache_data(ttl=300)
def read_sheet(sheet_id: str, sheet_name: str = None) -> pl.DataFrame:
    """
    Lee los datos de una hoja específica y devuelve un DataFrame de Polars.
    """
    client = get_gsheet_client()
    try:
        sh = client.open_by_key(sheet_id)
        if sheet_name is None:
            sheet_name = st.secrets["google"].get("sheet_name", sh.sheet1.title)
        ws = sh.worksheet(sheet_name)
        data = ws.get_all_records()
        return pl.DataFrame(data)
    except WorksheetNotFound:
        st.error(f"No se pudo leer la hoja '{sheet_name}': hoja no encontrada")
        return pl.DataFrame()
    except SpreadsheetNotFound:
        st.error(f"No se pudo acceder al documento: ID {sheet_id} inválido")
        return pl.DataFrame()
    except Exception as e:
        st.error(f"Error al leer la hoja: {e}")
        return pl.DataFrame()


# ===========================
# Agregar filas
# ===========================
def append_row(sheet_id: str, row: list, sheet_name: str = None):
    """
    Agrega una nueva fila al final de una hoja específica.
    """
    client = get_gsheet_client()
    try:
        sh = client.open_by_key(sheet_id)
        if sheet_name is None:
            sheet_name = st.secrets["google"].get("sheet_name", sh.sheet1.title)
        ws = sh.worksheet(sheet_name)
        ws.append_row(row)
        st.success(f"Fila agregada correctamente a '{sheet_name}'")
    except WorksheetNotFound:
        st.error(f"No se pudo encontrar la hoja '{sheet_name}'")
    except SpreadsheetNotFound:
        st.error(f"No se pudo acceder al documento: ID {sheet_id} inválido")
    except Exception as e:
        st.error(f"Error al agregar fila: {e}")


# ===========================
# Testeo local (opcional)
# ===========================
if __name__ == "__main__":
    try:
        sheet_id = st.secrets["google"]["sheet_id"]
        print("Hojas disponibles:", list_sheets(sheet_id))
        df = read_sheet(sheet_id)
        print(df)
    except Exception as e:
        print(f"No se pudo cargar la hoja: {e}")
