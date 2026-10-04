import dash
from src.layouts import area_layout

dash.register_page(__name__, path="/transporte", name="Transporte")

def layout(**kwargs):
    return area_layout("TRANSPORTE", "transporte", "Execução das despesas classificadas na função Transporte.")
