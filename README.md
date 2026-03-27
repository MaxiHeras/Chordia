# Chordia

Diccionario e identificador de acordes (Streamlit), misma funcionalidad que [diccionario-acordes](https://github.com/MaxiHeras/diccionario-acordes) con el código organizado en módulos para facilitar mejoras.

## Ejecutar en local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud

- Main file: `app.py`
- Python: ver `runtime.txt`

Opcional: en **Settings → Secrets** define `APP_PUBLIC_URL` con la URL pública de la app (para el QR y el pie del PDF). Si no está definida, se usa el enlace del repositorio por defecto.

## Estructura

| Ruta | Rol |
|------|-----|
| `app.py` | Entrada Streamlit |
| `chordia/config.py` | URLs y constantes de despliegue |
| `chordia/data.py` | Carga CSV (Google Sheets) |
| `chordia/chords.py` | Notas y filtros sobre filas |
| `chordia/display.py` | Detalle de acorde en la UI |
| `chordia/pdf.py` | Generación de PDF |
| `chordia/styles.py` | CSS global |
| `chordia/ui/` | Sidebar y panel principal |
| carpetas `MAYOR`, `MENOR`, … | Diagramas PNG (raw GitHub) |
