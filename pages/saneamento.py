import dash
from src.layouts import area_layout

dash.register_page(__name__, path="/saneamento", name="Saneamento")

def layout():
    return area_layout("SANEAMENTO", "saneamento", "Execução das despesas classificadas na função Saneamento.")
