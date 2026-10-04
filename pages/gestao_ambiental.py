import dash
from src.layouts import area_layout

dash.register_page(__name__, path="/gestao-ambiental", name="Gestão Ambiental")

def layout(**kwargs):
    return area_layout("GESTÃO AMBIENTAL", "gestao-ambiental", "Execução das despesas classificadas na função Gestão Ambiental.")
