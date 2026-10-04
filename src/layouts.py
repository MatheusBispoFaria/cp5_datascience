from __future__ import annotations

from dash import dash_table, dcc, html
import dash_bootstrap_components as dbc

from .data_service import area_metadata, dados_disponiveis, opcoes_area


GRAPH_LABELS = {
    "graph-evolution": "Evolução financeira",
    "graph-region": "Distribuição por localizador territorial",
    "graph-program": "Principais programas",
    "graph-subfunction": "Estágios financeiros por subfunção",
    "graph-box": "Boxplot por localizador territorial",
    "graph-hist": "Distribuição dos pagamentos",
    "graph-corr": "Correlação entre medidas financeiras",
    "graph-pearson": "Correlação de Pearson",
}


def _options(valores: list[str]) -> list[dict]:
    return [{"label": valor, "value": valor} for valor in valores]


def kpi_card(titulo: str, id_: dict, subtitulo: str = "") -> html.Div:
    return html.Div(
        [
            html.Div(titulo, className="kpi-label"),
            html.Div("—", id=id_, className="kpi-value"),
            html.Div(subtitulo, className="kpi-subtitle") if subtitulo else None,
        ],
        className="kpi-card",
    )


def graph_card(graph_id: dict) -> html.Div:
    area = graph_id["area"]
    graph_key = graph_id["type"]
    graph_label = GRAPH_LABELS.get(graph_key, "Análise do gráfico")

    info_button_id = {"type": "graph-info-button", "area": area, "graph": graph_key}
    modal_id = {"type": "graph-info-modal", "area": area, "graph": graph_key}

    return html.Div(
        [
            dcc.Graph(
                id=graph_id,
                config={
                    "displaylogo": False,
                    "displayModeBar": False,
                    "responsive": True,
                },
                className="graph",
            ),
            html.Button(
                "↗",
                id=info_button_id,
                className="graph-info-button",
                title="Abrir análise do gráfico",
                **{"aria-label": f"Abrir análise de {graph_label}"},
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(graph_label, className="graph-modal-title"),
                        close_button=True,
                    ),
                    dbc.ModalBody(
                        [
                            html.P(
                                "Espaço reservado para a interpretação analítica deste gráfico. "
                                "Aqui serão descritos os principais padrões observados no recorte selecionado.",
                                className="graph-modal-text",
                            ),
                            html.P(
                                "A análise final poderá destacar concentrações, diferenças entre grupos, "
                                "valores atípicos, tendências e limitações da leitura, sempre considerando "
                                "os filtros ativos na página.",
                                className="graph-modal-text",
                            ),
                            html.Div(
                                "Conteúdo provisório — será substituído pela análise real dos dados.",
                                className="graph-modal-placeholder",
                            ),
                        ]
                    ),
                ],
                id=modal_id,
                is_open=False,
                centered=True,
                size="lg",
                className="graph-analysis-modal",
            ),
        ],
        className="graph-card",
    )


def tabela_rastreabilidade(slug: str) -> html.Details:
    colunas = [
        {"name": "ID", "id": "Id"},
        {"name": "Ano", "id": "Ano", "type": "numeric"},
        {"name": "Data", "id": "Data"},
        {"name": "Subfunção", "id": "SubFuncao"},
        {"name": "Programa", "id": "Programa"},
        {"name": "Ação", "id": "Acao"},
        {"name": "Localizador", "id": "Subtitulo"},
        {"name": "Unidade gestora", "id": "UnidadeGestora"},
        {"name": "Empenhado", "id": "ValorEmpenho", "type": "numeric"},
        {"name": "Liquidado", "id": "ValorLiquidado", "type": "numeric"},
        {"name": "Pago", "id": "ValorPago", "type": "numeric"},
        {"name": "RAP", "id": "ValorRap", "type": "numeric"},
    ]

    return html.Details(
        [
            html.Summary("Ver registros utilizados no recorte"),
            html.Div(
                [
                    html.P(
                        "Tabela de rastreabilidade dos indicadores exibidos acima. "
                        "Não são carregados CPF/CNPJ/NIS, favorecidos ou dados bancários.",
                        className="traceability-note",
                    ),
                    dash_table.DataTable(
                        id={"type": "records-table", "area": slug},
                        columns=colunas,
                        data=[],
                        page_size=15,
                        page_action="native",
                        sort_action="native",
                        filter_action="native",
                        style_table={"overflowX": "auto"},
                        style_header={
                            "backgroundColor": "#0b4f8a",
                            "color": "white",
                            "fontWeight": "600",
                            "border": "1px solid #d9e0e7",
                        },
                        style_cell={
                            "fontFamily": "Segoe UI, Arial, sans-serif",
                            "fontSize": "12px",
                            "padding": "7px 8px",
                            "textAlign": "left",
                            "minWidth": "100px",
                            "maxWidth": "260px",
                            "whiteSpace": "normal",
                            "height": "auto",
                            "border": "1px solid #e8e8e8",
                            "color": "#111111",
                            "backgroundColor": "#ffffff",
                        },
                    ),
                ],
                className="traceability-body",
            ),
        ],
        className="traceability-panel",
    )


def area_layout(funcao: str, slug: str, descricao: str) -> html.Div:
    meta = area_metadata(funcao)
    opcoes = (
        opcoes_area(funcao)
        if dados_disponiveis()
        else {"anos": [], "regioes": [], "subfuncoes": [], "programas": [], "unidades": []}
    )

    alerta = None
    if not dados_disponiveis():
        alerta = dbc.Alert(
            "Dados ainda não encontrados. Coloque os quatro ZIPs de 2024 e os quatro ZIPs de 2025 na pasta data/raw e reinicie o app.",
            color="warning",
            className="mb-3",
        )

    return html.Div(
        [
            dcc.Store(
                id={"type": "area-store", "area": slug},
                data={"funcao": funcao, "slug": slug},
            ),
            dbc.Offcanvas(
                [
                    html.Div("Ano", className="filter-label"),
                    dcc.Dropdown(
                        id={"type": "filter-year", "area": slug},
                        options=[{"label": str(ano), "value": ano} for ano in opcoes["anos"]],
                        multi=True,
                        placeholder="2024 e 2025",
                    ),
                    html.Div("Período", className="filter-label"),
                    dcc.DatePickerRange(
                        id={"type": "filter-date", "area": slug},
                        min_date_allowed=meta.get("data_minima"),
                        max_date_allowed=meta.get("data_maxima"),
                        start_date=meta.get("data_minima"),
                        end_date=meta.get("data_maxima"),
                        display_format="DD/MM/YYYY",
                        className="filter-date",
                    ),
                    html.Div("Localizador territorial", className="filter-label"),
                    dcc.Dropdown(
                        id={"type": "filter-region", "area": slug},
                        options=_options(opcoes["regioes"]),
                        multi=True,
                        placeholder="Todos",
                    ),
                    html.Div("Subfunção", className="filter-label"),
                    dcc.Dropdown(
                        id={"type": "filter-subfunction", "area": slug},
                        options=_options(opcoes["subfuncoes"]),
                        multi=True,
                        placeholder="Todas",
                    ),
                    html.Div("Programa", className="filter-label"),
                    dcc.Dropdown(
                        id={"type": "filter-program", "area": slug},
                        options=_options(opcoes["programas"]),
                        multi=True,
                        placeholder="Todos",
                    ),
                    html.Div("Unidade gestora", className="filter-label"),
                    dcc.Dropdown(
                        id={"type": "filter-unit", "area": slug},
                        options=_options(opcoes["unidades"]),
                        multi=True,
                        placeholder="Todas",
                    ),
                    html.Div(
                        "Os filtros afetam todos os indicadores, gráficos e registros desta página.",
                        className="filter-help",
                    ),
                ],
                id={"type": "filter-drawer", "area": slug},
                title=f"Filtros — {funcao.title()}",
                placement="end",
                is_open=False,
                scrollable=True,
                className="filter-offcanvas",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H2(funcao.title(), className="page-title"),
                            html.P(descricao, className="page-description"),
                        ],
                        className="page-heading",
                    ),
                    dbc.Button(
                        "Filtros",
                        id={"type": "filter-button", "area": slug},
                        color="secondary",
                        outline=True,
                        className="filter-button",
                    ),
                ],
                className="page-head-row",
            ),
            alerta,
            html.Div(
                [
                    kpi_card("Empenhado", {"type": "kpi-empenho", "area": slug}),
                    kpi_card("Liquidado", {"type": "kpi-liquidado", "area": slug}),
                    kpi_card("Pago", {"type": "kpi-pago", "area": slug}),
                    kpi_card("RAP", {"type": "kpi-rap", "area": slug}, "Restos a pagar"),
                ],
                className="kpi-grid",
            ),
            dcc.Tabs(
                id={"type": "analysis-tabs", "area": slug},
                value="overview",
                className="analysis-tabs",
                parent_className="analysis-tabs-parent",
                children=[
                    dcc.Tab(
                        label="Visão geral",
                        value="overview",
                        className="analysis-tab",
                        selected_className="analysis-tab analysis-tab--selected",
                        children=html.Div(
                            [
                                graph_card({"type": "graph-evolution", "area": slug}),
                                graph_card({"type": "graph-region", "area": slug}),
                                graph_card({"type": "graph-program", "area": slug}),
                                graph_card({"type": "graph-subfunction", "area": slug}),
                            ],
                            className="chart-grid",
                        ),
                    ),
                    dcc.Tab(
                        label="Estatística",
                        value="stats",
                        className="analysis-tab",
                        selected_className="analysis-tab analysis-tab--selected",
                        children=html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Span("IC 95% da média diária paga", className="stat-label"),
                                                html.Strong("—", id={"type": "stat-ci", "area": slug}, className="stat-value"),
                                            ],
                                            className="stat-card",
                                        ),
                                        html.Div(
                                            [
                                                html.Span("Mediana diária", className="stat-label"),
                                                html.Strong("—", id={"type": "stat-median", "area": slug}, className="stat-value"),
                                            ],
                                            className="stat-card",
                                        ),
                                        html.Div(
                                            [
                                                html.Span("Desvio padrão diário", className="stat-label"),
                                                html.Strong("—", id={"type": "stat-std", "area": slug}, className="stat-value"),
                                            ],
                                            className="stat-card",
                                        ),
                                        html.Div(
                                            [
                                                html.Span("Coeficiente de variação", className="stat-label"),
                                                html.Strong("—", id={"type": "stat-cv", "area": slug}, className="stat-value"),
                                            ],
                                            className="stat-card",
                                        ),
                                        html.Div(
                                            [
                                                html.Span("Pearson (empenhado × pago)", className="stat-label"),
                                                html.Strong("—", id={"type": "stat-pearson", "area": slug}, className="stat-value"),
                                            ],
                                            className="stat-card",
                                        ),
                                    ],
                                    className="stat-grid",
                                ),
                                html.Div(
                                    "O intervalo de confiança é aplicado à média diária do valor pago no período filtrado; não representa incerteza sobre o total anual observado.",
                                    className="method-note",
                                ),
                                html.Div(
                                    [
                                        graph_card({"type": "graph-box", "area": slug}),
                                        graph_card({"type": "graph-hist", "area": slug}),
                                        graph_card({"type": "graph-corr", "area": slug}),
                                        graph_card({"type": "graph-pearson", "area": slug}),
                                    ],
                                    className="chart-grid",
                                ),
                            ],
                            className="stats-section",
                        ),
                    ),
                ],
            ),
            html.Div(
                [
                    html.Span("Registros no recorte: "),
                    html.Strong("—", id={"type": "record-count", "area": slug}),
                ],
                className="record-footer",
            ),
            tabela_rastreabilidade(slug),
        ],
        className="page-shell",
    )
