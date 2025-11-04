import os

import gspread
import polars as pl
import streamlit as st
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json")
SHEET_ID = os.getenv("SHEET_ID")
DEFAULT_SHEET_NAME = os.getenv("DEFAULT_SHEET_NAME", "Hoja 1")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_gsheet_client():
    """
    Inicializa y devuelve un cliente autenticado de Google Sheets usando una cuenta de servicio

    Este método lee las credenciales desde el archivo JSON especificado en SERVICE_ACCOUNT_FILE
    y aplica los permisos definidos en la lista SCOPES.
    Devuelve un objeto gspread.Client que permite leer, escribir y actualizar
    datos en hojas de cálculo de Google Sheets

    Returns
    -------
    gspread.Client
        Cliente autenticado listo para interactuar con la API de Google Sheets
    """
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return gspread.authorize(creds)


@st.cache_data(ttl=300)
def read_sheet(sheet_id: str, sheet_name: str = "Hoja 1") -> pl.DataFrame:
    """
    Lee los datos de una hoja específica de Google Sheets y los devuelve como un DataFrame de Polars

    Esta función utiliza un cliente autenticado de Google Sheets para acceder a una hoja
    identificada por su ID y nombre. Obtiene todos los registros disponibles en formato
    de lista de diccionarios
    y los convierte a un objeto pl.DataFrame para su posterior manipulación dentro de la aplicación

    Parameters
    ----------
    sheet_id : str
        ID único del documento de Google Sheets (se encuentra entre /d/ y /edit en la URL)
    sheet_name : str, optional
        Nombre de la hoja dentro del documento, por defecto "Hoja 1"

    Returns
    -------
    pl.DataFrame
        DataFrame de Polars con los datos leídos desde la hoja especificada
    """
    client = get_gsheet_client()
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    data = sheet.get_all_records()
    return pl.DataFrame(data)


def append_row(sheet_id: str, row: list, sheet_name: str = "Hoja 1"):
    """
    Agrega una nueva fila al final de una hoja específica en Google Sheets

    Utiliza el cliente autenticado para abrir la hoja indicada y añadir
    los valores provistos en la lista `row`.
    Cada elemento de la lista representa una celda dentro de la nueva fila.
    Es útil para registrar nuevos productos, variantes o entradas de presupuesto
    sin sobrescribir los datos existentes

    Parameters
    ----------
    sheet_id : str
        ID único del documento de Google Sheets (se encuentra entre /d/ y /edit en la URL)
    row : list
        Lista de valores que se insertarán como una nueva fila en la hoja
    sheet_name : str, optional
        Nombre de la hoja dentro del documento, por defecto "Hoja 1"
    """
    client = get_gsheet_client()
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    sheet.append_row(row)


if __name__ == "__main__":
    acc = read_sheet(SHEET_ID, DEFAULT_SHEET_NAME)
    print(acc)
