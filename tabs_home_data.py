"""
tabs_home_data.py
=================
Layout builders and Dash callbacks for:
  - Home / About tab   (_tab_home)
  - Data Explorer tab  (_tab_data, upd_data, download_csv)
"""

import plotly.graph_objects as go
from dash import dcc, html, dash_table, Input, Output

from constants import (
    NAVY, BLUE, GREEN, GOLD, DGRAY, LGRAY, WHITE, RED,
    ELECTIONS, VAR_DESC, T,
)
from ui_helpers import _card, _info, _section_title, _dd, _bands

# State is injected at runtime by app.py
import state


# ══════════════════════════════════════════════════════════════
# HOME TAB
# ══════════════════════════════════════════════════════════════

def _tab_home(lang: str) -> html.Div:
    t = T[lang]

    def stat(val, label, sub):
        return html.Div([
            html.Div(val,   style={'fontSize': '36px', 'fontWeight': '800', 'color': BLUE}),
            html.Div(label, style={'fontSize': '14px', 'fontWeight': '700', 'color': NAVY, 'marginTop': '2px'}),
            html.Div(sub,   style={'fontSize': '11px', 'color': DGRAY, 'marginTop': '2px'}),
        ], style={**{'background': WHITE, 'borderRadius': '12px',
                     'boxShadow': '0 2px 12px rgba(0,0,0,0.08)',
                     'padding': '24px', 'marginBottom': '20px'},
                  'textAlign': 'center', 'flex': '1', 'margin': '8px'})

    var_rows = [
        ("CPI Index",        "Tracks everyday goods cost. Rising CPI = inflation. Base Jan 2003=100.", "Monthly→Quarterly", "Armstat"),
        ("M2 Money Supply",  "All cash + bank deposits. Expanding M2 before elections = classic PBC signal.", "Monthly→Quarterly", "CBA"),
        ("Gov. Expenditure", "Total government spending. Politicians often raise this before elections.", "Annual→Quarterly*", "Armstat"),
        ("Interest Rate",    "CBA policy rate. Lower rate = cheaper loans = more spending = inflation risk.", "Monthly→Quarterly", "CBA"),
        ("Election Dummy",   "1 in election quarter AND quarter before; 0 otherwise. Our key variable.", "Constructed", "Official records"),
    ]

    return html.Div([
        _card(
            html.H2(t['about_h'], style={'color': NAVY, 'marginTop': '0', 'fontWeight': '800'}),
            html.P(t['about_p1'], style={'color': '#334155', 'lineHeight': '1.8', 'fontSize': '15px'}),
            html.P(t['about_p2'], style={'color': '#334155', 'lineHeight': '1.8', 'fontSize': '15px'}),
        ),
        html.Div([
            stat("72", t['stat_q'], t['stat_q_s']),
            stat("5",  t['stat_e'], t['stat_e_s']),
            stat("5",  t['stat_v'], t['stat_v_s']),
            stat("3",  t['stat_m'], t['stat_m_s']),
        ], style={'display': 'flex', 'gap': '8px', 'marginBottom': '8px'}),
        _card(
            _section_title(t['data_h'], t['data_sub']),
            dash_table.DataTable(
                data=[{t['col_var']: r[0], t['col_mean']: r[1],
                       t['col_freq']: r[2], t['col_src']: r[3]} for r in var_rows],
                columns=[{'name': c, 'id': c}
                         for c in [t['col_var'], t['col_mean'], t['col_freq'], t['col_src']]],
                style_cell={'textAlign': 'left', 'fontSize': '13px', 'padding': '10px 14px',
                            'whiteSpace': 'normal', 'fontFamily': 'Inter,Arial'},
                style_header={'backgroundColor': NAVY, 'color': WHITE, 'fontWeight': '700'},
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': LGRAY},
                    {'if': {'column_id': t['col_var']}, 'fontWeight': '700', 'color': BLUE},
                ],
                style_table={'borderRadius': '8px', 'overflow': 'hidden'},
            ),
            html.P(t['annual_note'], style={'color': DGRAY, 'fontSize': '12px', 'marginTop': '10px'}),
        ),
        _card(
            _section_title(t['clean_h'], t['clean_sub']),
            html.Div([
                html.Div([
                    html.Div(n, style={
                        'background': c, 'color': WHITE, 'borderRadius': '50%',
                        'width': '28px', 'height': '28px', 'display': 'flex',
                        'alignItems': 'center', 'justifyContent': 'center',
                        'fontWeight': '700', 'fontSize': '13px',
                        'marginRight': '12px', 'flexShrink': '0',
                    }),
                    html.Div([
                        html.Strong(h),
                        html.P(p, style={'margin': '2px 0 0', 'color': DGRAY, 'fontSize': '13px'}),
                    ]),
                ], style={'display': 'flex', 'alignItems': 'flex-start', 'marginBottom': '16px'})
                for n, c, h, p in [
                    ('1', BLUE,  t['c1h'], t['c1p']),
                    ('2', GREEN, t['c2h'], t['c2p']),
                    ('3', GOLD,  t['c3h'], t['c3p']),
                ]
            ]),
        ),
        _card(
            _section_title(t['elec_cov']),
            html.Div([
                html.Div([
                    html.Div(str(yr), style={'fontSize': '28px', 'fontWeight': '800', 'color': info['color']}),
                    html.Div("Parliamentary", style={'fontSize': '12px', 'color': '#94a3b8', 'marginTop': '4px'}),
                ], style={
                    'textAlign': 'center', 'flex': '1',
                    'borderLeft': f'3px solid {info["color"]}',
                    'paddingLeft': '12px', 'margin': '4px',
                })
                for yr, info in ELECTIONS.items()
            ], style={'display': 'flex', 'gap': '12px'}),
        ),
    ])


# ══════════════════════════════════════════════════════════════
# DATA EXPLORER TAB
# ══════════════════════════════════════════════════════════════

def _all_vars_fig() -> go.Figure:
    """Overview chart with all four raw variables and election bands."""
    fig = go.Figure()
    for var, color in zip(state.NUMERIC, [BLUE, GREEN, GOLD, '#7c3aed']):
        s = state.DATA[var].dropna()
        fig.add_trace(go.Scatter(
            x=s.index, y=s.values,
            name=VAR_DESC[var][0],
            line={'color': color, 'width': 2},
            hovertemplate=f'<b>{var}</b><br>%{{x|%Y-%m}}: %{{y:,.1f}}<extra></extra>',
        ))
    for eq in state.ELEC_Q:
        import pandas as pd
        fig.add_vrect(x0=eq, x1=eq + pd.DateOffset(months=3),
                      fillcolor=RED, opacity=0.07, line_width=0)
    fig.update_layout(
        height=400, template='plotly_white', hovermode='x unified',
        legend={'orientation': 'h', 'y': -0.18}, margin={'t': 10},
        xaxis={
            'rangeslider': {'visible': True},
            'rangeselector': {'buttons': [
                {'count': 2, 'label': '2Y', 'step': 'year', 'stepmode': 'backward'},
                {'count': 5, 'label': '5Y', 'step': 'year', 'stepmode': 'backward'},
                {'step': 'all', 'label': 'All'},
            ]},
        },
    )
    return fig


def _tab_data(lang: str) -> html.Div:
    t = T[lang]
    return html.Div([
        _section_title("Data Explorer", "Select a variable to explore its history"),
        html.Div([
            dcc.Download(id='download-data'),
            html.Button(
                "⬇️  Download Cleaned Data (CSV)", id='btn-download',
                style={
                    'background': BLUE, 'color': WHITE, 'border': 'none',
                    'borderRadius': '8px', 'padding': '10px 20px',
                    'fontSize': '14px', 'fontWeight': '600', 'cursor': 'pointer',
                    'marginBottom': '20px',
                },
            ),
            html.Span(
                " armenia_quarterly.csv — 72 quarters, 5 variables, ready for analysis",
                style={'color': DGRAY, 'fontSize': '13px', 'marginLeft': '12px'},
            ),
        ]),
        _card(
            _dd('data-var',
                [{'label': f'{v} — {VAR_DESC[v][0]}', 'value': v} for v in state.NUMERIC],
                'CPI_index', label=t['data_select']),
            html.Div(id='var-desc', style={
                'background': '#eff6ff', 'border': '1px solid #bfdbfe',
                'borderRadius': '8px', 'padding': '14px 18px',
                'marginBottom': '18px', 'color': '#1e3a8a',
                'fontSize': '14px', 'lineHeight': '1.7',
            }),
            dcc.Graph(id='data-line', config={'displayModeBar': True}),
            html.Div(id='data-stats'),
        ),
        _card(
            _section_title(
                "All Variables — Overview",
                "Shaded red = election quarters. Range slider below to zoom.",
            ),
            dcc.Graph(id='data-all', figure=_all_vars_fig()),
        ),
    ])


# ── Callbacks ─────────────────────────────────────────────────

def register_callbacks(app):
    @app.callback(
        Output('download-data', 'data'),
        Input('btn-download', 'n_clicks'),
        prevent_initial_call=True,
    )
    def download_csv(_n):
        return dcc.send_data_frame(state.DATA.to_csv, 'armenia_quarterly.csv')

    @app.callback(
        Output('data-line',  'figure'),
        Output('var-desc',   'children'),
        Output('data-stats', 'children'),
        Input('data-var',    'value'),
        Input('lang',        'data'),
    )
    def upd_data(var, lang):
        t           = T[lang or 'en']
        s           = state.DATA[var].dropna()
        title, desc = VAR_DESC[var]

        fig = go.Figure()
        _bands(fig, state.ELEC_Q)
        fig.add_trace(go.Scatter(
            x=s.index, y=s.values, mode='lines', name=title,
            line={'color': BLUE, 'width': 2.5},
            fill='tozeroy', fillcolor='rgba(37,99,235,0.06)',
            hovertemplate=f'<b>%{{x|%Y-%m}}</b><br>{title}: %{{y:,.2f}}<extra></extra>',
        ))
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode='lines', name='Election quarter',
            line={'color': 'rgba(220,38,38,0.45)', 'width': 10},
        ))
        fig.update_layout(
            title={'text': title, 'font': {'size': 16, 'color': NAVY}},
            template='plotly_white', height=360,
            legend={'orientation': 'h', 'y': -0.15}, margin={'t': 50, 'b': 60},
            xaxis={'rangeselector': {'buttons': [
                {'count': 2, 'label': '2Y', 'step': 'year', 'stepmode': 'backward'},
                {'count': 5, 'label': '5Y', 'step': 'year', 'stepmode': 'backward'},
                {'step': 'all', 'label': 'All'},
            ]}},
        )

        stats = s.describe().round(3).reset_index()
        stats.columns = ['Statistic', 'Value']
        tbl = dash_table.DataTable(
            data=stats.to_dict('records'),
            columns=[{'name': c, 'id': c} for c in stats.columns],
            style_cell={'textAlign': 'left', 'fontSize': '13px', 'padding': '8px 14px'},
            style_header={'backgroundColor': NAVY, 'color': WHITE, 'fontWeight': '700'},
            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': LGRAY}],
            style_table={'width': '380px', 'borderRadius': '8px', 'overflow': 'hidden'},
        )

        return fig, [html.Strong(t['about_var']), desc], tbl
