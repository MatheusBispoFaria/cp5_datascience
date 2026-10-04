import dash
from src.layouts import area_layout

dash.register_page(__name__, path="/habitacao", name="Habitação")

def layout():
    return area_layout("HABITAÇÃO", "habitacao", "Execução das despesas classificadas na função Habitação.")
