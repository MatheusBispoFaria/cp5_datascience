import dash
from src.layouts import area_layout

dash.register_page(__name__, path="/urbanismo", name="Urbanismo")

def layout(**kwargs):
    return area_layout("URBANISMO", "urbanismo", "Execução das despesas classificadas na função Urbanismo.")
