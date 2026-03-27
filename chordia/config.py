"""URLs y parámetros centralizados."""

# Hoja "Acordes" exportada como CSV (Google Sheets).
URL_EXCEL = (
    "https://docs.google.com/spreadsheets/d/"
    "1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno"
    "/gviz/tq?tqx=out:csv&sheet=Acordes"
)

# Diagramas servidos desde raw GitHub de este repo (carpetas MAYOR, MENOR, … en la raíz).
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/MaxiHeras/Chordia/main"

PAGE_TITLE = "Chordia"

# Tras desplegar en Streamlit Cloud, conviene definir APP_PUBLIC_URL en Secrets
# para que el QR y el pie del PDF apunten a la app pública.
DEFAULT_APP_PUBLIC_URL = "https://github.com/MaxiHeras/Chordia"
