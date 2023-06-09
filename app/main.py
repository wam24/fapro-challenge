import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException

MONTH_IN_SPANISH = {
    "Jan": 'Ene',
    "Feb": "Feb",
    "Mar": "Mar",
    "Apr": "Abr",
    "May": "May",
    "Jun": 'Jun',
    "Jul": 'Jul',
    "Aug": 'Ago',
    "Sep": 'Sep',
    "Oct": 'Oct',
    "Nov": 'Nov',
    "Dec": 'Dic'
}


def get_data_table(date):
    if isinstance(date, str):
        date = check_date(date)
    request_api = requests.get(f'https://www.sii.cl/valores_y_fechas/uf/uf{date.year}.htm')
    page_html = request_api.content
    status_code = request_api.status_code
    if status_code == 404:
        return "No se pudo obtener información, el año que busca no existe"
    elif status_code == 200:
        # Crear un objeto BeautifulSoup con el contenido HTML
        soup = BeautifulSoup(page_html, 'html.parser')

        month_name = date.strftime("%b")
        # Buscar la tabla HTML en el objeto BeautifulSoup
        tabla = soup.find("div", id="mes_all")
        # Imprimir la tabla HTML
        table_html = str(tabla.table)
        html_to_dataframe = pd.read_html(table_html)[0]
        month_filter = MONTH_IN_SPANISH.get(month_name)
        day_filter = (date - timedelta(days=1)).day
        data_info = html_to_dataframe.get(month_filter).get(day_filter)
        return data_info if not pd.isna(data_info) else 'La fecha suministrada no cuenta con datos disponibles'


def check_date(date_str):
    # Lista de formatos de fecha
    formats = ['%d-%m-%Y', '%d/%m/%Y', '%d.%m.%Y']
    if not isinstance(date_str, str):
        return None
    for format_date in formats:
        try:
            # Convertir el string en un objeto datetime
            date = datetime.strptime(date_str, format_date)
            return date
        except ValueError:
            pass

    # Si no se pudo convertir con ningún formato, devolver None
    return None


app = FastAPI()


@app.get("/sii")
async def fetch_sii(date: str | None = None):
    today = datetime.today()
    year_now = today.year
    if date and not check_date(date):
        raise HTTPException(status_code=400, detail="Debe colocar un formato de fecha. Ej: dd/mm/yyyy")
    else:
        date = check_date(date)
        if date:
            if date.year < 2013:
                raise HTTPException(status_code=400, detail="La fecha debe ser mayor a 2012")
            elif date.year > year_now:
                raise HTTPException(status_code=400, detail=f"La fecha debe ser menor o igual al {year_now}")

            return get_data_table(date)
    raise HTTPException(status_code=400,
                        detail=f"Debe especificar la fecha en la url, Ej. /sii?date={datetime.strftime(today, '%d/%m/%Y')}")
