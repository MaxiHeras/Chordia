"""URLs y parámetros centralizados."""

from urllib.parse import quote

SPREADSHEET_ID = "1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno"


def sheet_csv_url(sheet_name: str) -> str:
    encoded_sheet = quote(sheet_name, safe="")
    return (
        "https://docs.google.com/spreadsheets/d/"
        f"{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet}"
    )


# Hoja principal de acordes.
URL_EXCEL = sheet_csv_url("Acordes")

# Se intentan en este orden para evitar problemas por mayúsculas/minúsculas.
SCALE_SHEET_CANDIDATES = ("Escalas", "ESCALAS", "escalas")
HARMONIZATION_SHEET_CANDIDATES = (
    "Armonización de escalas",
    "Armonizacion de escalas",
    "ARMONIZACION DE ESCALAS",
)

# Diagramas servidos desde raw GitHub de este repo (carpetas MAYOR, MENOR, … en la raíz).
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/MaxiHeras/Chordia/main"

PAGE_TITLE = "Chordia"

# Tras desplegar en Streamlit Cloud, conviene definir APP_PUBLIC_URL en Secrets
# para que el QR y el pie del PDF apunten a la app pública.
DEFAULT_APP_PUBLIC_URL = "https://github.com/MaxiHeras/Chordia"
