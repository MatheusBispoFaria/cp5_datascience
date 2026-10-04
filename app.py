from __future__ import annotations

import dash
from dash import MATCH, Input, Output, State, callback, dcc, html
import dash_bootstrap_components as dbc

from src.analytics import (
    dispersao_diaria,
    intervalo_confianca_media_diaria,
    kpis,
    moeda,
    percentual,
)
from src.charts import (
    boxplot_regiao,
    corrplot,
    evolucao,
    execucao_subfuncao,
    histograma,
    pearson_scatter,
    por_regiao,
    programas,
)
from src.data_service import carregar_area, registros_rastreaveis


app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="CPSI | Despesas ES",
)
server = app.server

NAV = [
    ("Visão Geral", "/"),
    ("Urbanismo", "/urbanismo"),
    ("Transporte", "/transporte"),
    ("Habitação", "/habitacao"),
    ("Saneamento", "/saneamento"),
    ("Gestão Ambiental", "/gestao-ambiental"),
]

app.layout = html.Div(
    [
        dbc.Offcanvas(
            [
                html.Div("Áreas", className="menu-section-label"),
                html.Nav(
                    [dcc.Link(nome, href=href, className="menu-link") for nome, href in NAV],
                    className="menu-list",
                ),
                html.Div(
                    "Dados oficiais de despesas do Espírito Santo — 2024 e 2025",
                    className="menu-footnote",
                ),
            ],
            id="main-menu",
            title="Navegação",
            is_open=False,
            placement="start",
            scrollable=True,
        ),
        html.Header(
            [
                html.Button("☰", id="menu-button", className="hamburger", title="Abrir menu"),
                html.Div(
                    html.Strong("POC das Despesas Públicas do ES", className="brand-title"),
                    className="brand",
                ),
            ],
            className="topbar",
        ),
        html.Main(dash.page_container, className="content"),
    ],
    className="app-root",
)


@callback(
    Output("main-menu", "is_open"),
    Input("menu-button", "n_clicks"),
    State("main-menu", "is_open"),
    prevent_initial_call=True,
)
def toggle_menu(n_clicks, aberto):
    return not aberto


@callback(
    Output({"type": "filter-drawer", "area": MATCH}, "is_open"),
    Input({"type": "filter-button", "area": MATCH}, "n_clicks"),
    State({"type": "filter-drawer", "area": MATCH}, "is_open"),
    prevent_initial_call=True,
)
def toggle_filters(n_clicks, aberto):
    return not aberto


@callback(
    Output({"type": "graph-info-modal", "area": MATCH, "graph": MATCH}, "is_open"),
    Input({"type": "graph-info-button", "area": MATCH, "graph": MATCH}, "n_clicks"),
    State({"type": "graph-info-modal", "area": MATCH, "graph": MATCH}, "is_open"),
    prevent_initial_call=True,
)
def toggle_graph_info(n_clicks, aberto):
    return not aberto


@callback(
    Output({"type": "kpi-empenho", "area": MATCH}, "children"),
    Output({"type": "kpi-liquidado", "area": MATCH}, "children"),
    Output({"type": "kpi-pago", "area": MATCH}, "children"),
    Output({"type": "kpi-rap", "area": MATCH}, "children"),
    Output({"type": "graph-evolution", "area": MATCH}, "figure"),
    Output({"type": "graph-region", "area": MATCH}, "figure"),
    Output({"type": "graph-program", "area": MATCH}, "figure"),
    Output({"type": "graph-subfunction", "area": MATCH}, "figure"),
    Output({"type": "stat-ci", "area": MATCH}, "children"),
    Output({"type": "stat-median", "area": MATCH}, "children"),
    Output({"type": "stat-std", "area": MATCH}, "children"),
    Output({"type": "stat-cv", "area": MATCH}, "children"),
    Output({"type": "stat-pearson", "area": MATCH}, "children"),
    Output({"type": "graph-box", "area": MATCH}, "figure"),
    Output({"type": "graph-hist", "area": MATCH}, "figure"),
    Output({"type": "graph-corr", "area": MATCH}, "figure"),
    Output({"type": "graph-pearson", "area": MATCH}, "figure"),
    Output({"type": "record-count", "area": MATCH}, "children"),
    Output({"type": "records-table", "area": MATCH}, "data"),
    Input({"type": "filter-year", "area": MATCH}, "value"),
    Input({"type": "filter-date", "area": MATCH}, "start_date"),
    Input({"type": "filter-date", "area": MATCH}, "end_date"),
    Input({"type": "filter-region", "area": MATCH}, "value"),
    Input({"type": "filter-subfunction", "area": MATCH}, "value"),
    Input({"type": "filter-program", "area": MATCH}, "value"),
    Input({"type": "filter-unit", "area": MATCH}, "value"),
    State({"type": "area-store", "area": MATCH}, "data"),
)
def atualizar_area(anos, inicio, fim, regioes, subfuncoes, programas_filtro, unidades, area_info):
    funcao = area_info["funcao"]
    df = carregar_area(
        funcao,
        anos=anos,
        inicio=inicio,
        fim=fim,
        regioes=regioes,
        subfuncoes=subfuncoes,
        programas=programas_filtro,
        unidades=unidades,
    )

    resumo = kpis(df)
    ci = intervalo_confianca_media_diaria(df)
    disp = dispersao_diaria(df)
    fig_pearson, pearson = pearson_scatter(df)

    if ci["n"] >= 2:
        ci_texto = f"{moeda(ci['media'])} · [{moeda(ci['inferior'])}; {moeda(ci['superior'])}]"
    else:
        ci_texto = "Observações diárias insuficientes"

    pearson_texto = "—"
    if pearson["n"] >= 3 and pearson["r"] == pearson["r"]:
        pearson_texto = f"r = {pearson['r']:.3f} · p = {pearson['p']:.3g}"

    return (
        moeda(resumo["empenho"]),
        moeda(resumo["liquidado"]),
        moeda(resumo["pago"]),
        moeda(resumo["rap"]),
        evolucao(df),
        por_regiao(df),
        programas(df),
        execucao_subfuncao(df),
        ci_texto,
        moeda(disp["mediana"]) if disp["mediana"] == disp["mediana"] else "—",
        moeda(disp["desvio"]) if disp["desvio"] == disp["desvio"] else "—",
        percentual(disp["cv"]),
        pearson_texto,
        boxplot_regiao(df),
        histograma(df),
        corrplot(df),
        fig_pearson,
        f"{len(df):,}".replace(",", "."),
        registros_rastreaveis(df),
    )


if __name__ == "__main__":
    app.run(debug=True)
