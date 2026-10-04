import dash
from dash import dcc, html

from src.data_service import auditoria_base, dados_disponiveis, metadata, resumo_funcoes
from src.analytics import moeda


dash.register_page(__name__, path="/", name="Visão Geral")

AREAS = ["URBANISMO", "TRANSPORTE", "HABITAÇÃO", "SANEAMENTO", "GESTÃO AMBIENTAL"]
LINKS = [
    ("Urbanismo", "/urbanismo"),
    ("Transporte", "/transporte"),
    ("Habitação", "/habitacao"),
    ("Saneamento", "/saneamento"),
    ("Gestão Ambiental", "/gestao-ambiental"),
]


def _inteiro(valor: int) -> str:
    return f"{int(valor):,}".replace(",", ".")


def layout(**kwargs):
    if not dados_disponiveis():
        return html.Div(
            [
                html.H2("Dados não encontrados", className="page-title"),
                html.P(
                    "Coloque as quatro partes ZIP de 2024 e as quatro partes ZIP de 2025 em data/raw para carregar o dashboard.",
                    className="page-description",
                ),
                html.Code("data/raw/despesas_es_2024_completo_parte_01.zip ... 2025_completo_parte_04.zip"),
            ],
            className="page-shell",
        )

    meta = metadata()
    auditoria = auditoria_base()
    resumo = resumo_funcoes(AREAS)
    total_pago = resumo["ValorPago"].sum() if not resumo.empty else 0

    invalidos_monetarios = sum(auditoria["valores_invalidos_base_integral"].values())
    negativos = auditoria["valores_negativos_recorte"]
    integral_por_ano = auditoria.get("registros_base_integral_por_ano", {})
    recorte_por_ano = auditoria.get("registros_recorte_por_ano", {})
    reconstruidos_2025 = auditoria.get("rotulos_reconstruidos_2025", {})
    fallbacks_2025 = auditoria.get("rotulos_fallback_2025", {})

    return html.Div(
        [
            html.Div(
                [
                    html.P(
                        "Plataforma que transforma dados oficiais de despesas públicas do Espírito Santo de 2024 e 2025 "
                        "em indicadores, comparações e visualizações rastreáveis.",
                        className="page-description",
                    ),
                ],
                className="page-heading",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("Base integral 2024–2025", className="kpi-label"),
                            html.Div(_inteiro(meta.get("registros_base_integral", 0)), className="kpi-value"),
                        ],
                        className="kpi-card",
                    ),
                    html.Div(
                        [
                            html.Div("Registros no recorte", className="kpi-label"),
                            html.Div(_inteiro(meta.get("registros_recorte", 0)), className="kpi-value"),
                        ],
                        className="kpi-card",
                    ),
                    html.Div(
                        [
                            html.Div("Áreas monitoradas", className="kpi-label"),
                            html.Div(str(len(AREAS)), className="kpi-value"),
                        ],
                        className="kpi-card",
                    ),
                    html.Div(
                        [
                            html.Div("Pago nas áreas", className="kpi-label"),
                            html.Div(moeda(total_pago), className="kpi-value"),
                        ],
                        className="kpi-card",
                    ),
                ],
                className="kpi-grid",
            ),
            html.Div(
                [
                    dcc.Link(
                        html.Div(
                            [html.Strong(nome), html.Span("Abrir análise →")],
                            className="area-link-content",
                        ),
                        href=href,
                        className="area-link",
                    )
                    for nome, href in LINKS
                ],
                className="area-link-grid",
            ),
            html.Details(
                [
                    html.Summary("Qualidade e preparação dos dados"),
                    html.Div(
                        [
                            html.P(
                                f"Duplicidades por ID encontradas na base integral: "
                                f"{_inteiro(auditoria['duplicados_id_base_integral'])}. "
                                f"Datas inválidas: {_inteiro(auditoria['datas_invalidas_base_integral'])}. "
                                f"Valores monetários inválidos: {_inteiro(invalidos_monetarios)}.",
                                className="traceability-note",
                            ),
                            html.P(
                                "Movimentos monetários negativos são preservados como parte dos dados oficiais "
                                "e não são tratados automaticamente como erro. "
                                f"Empenho: {_inteiro(negativos['ValorEmpenho'])}; "
                                f"liquidado: {_inteiro(negativos['ValorLiquidado'])}; "
                                f"pago: {_inteiro(negativos['ValorPago'])}; "
                                f"RAP: {_inteiro(negativos['ValorRap'])}.",
                                className="traceability-note",
                            ),
                            html.P(
                                f"Base integral por ano — 2024: {_inteiro(integral_por_ano.get(2024, 0))}; "
                                f"2025: {_inteiro(integral_por_ano.get(2025, 0))}. "
                                f"Recorte da POC — 2024: {_inteiro(recorte_por_ano.get(2024, 0))}; "
                                f"2025: {_inteiro(recorte_por_ano.get(2025, 0))}.",
                                className="traceability-note",
                            ),
                            html.P(
                                "Em 2025, alguns rótulos textuais da fonte vieram vazios. A POC reconstrói "
                                "Função, Subfunção, Programa e Localizador a partir dos respectivos códigos, "
                                "usando as correspondências observadas na base oficial de 2024. "
                                f"Reconstruções: Função {_inteiro(reconstruidos_2025.get('Funcao', 0))}, "
                                f"Subfunção {_inteiro(reconstruidos_2025.get('SubFuncao', 0))}, "
                                f"Programa {_inteiro(reconstruidos_2025.get('Programa', 0))}, "
                                f"Localizador {_inteiro(reconstruidos_2025.get('Subtitulo', 0))}. "
                                f"Fallbacks sem correspondência segura: {sum(fallbacks_2025.values())}.",
                                className="traceability-note",
                            ),
                        ],
                        className="traceability-body",
                    ),
                ],
                className="traceability-panel",
            ),
        ],
        className="page-shell",
    )
