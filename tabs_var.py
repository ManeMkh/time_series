"""
tabs_var.py
===========
Layout builder and Dash callbacks for the VAR Model tab:
  - _tab_var
  - _hypothesis_conclusion
  - upd_var  (IRF figure + Granger table callback)
"""

import numpy as np
import plotly.graph_objects as go
from dash import dcc, html, dash_table, Input, Output

from constants import (
    NAVY, BLUE, GREEN, RED, DGRAY, LGRAY, WHITE,
    VAR_LABELS, T,
)
from ui_helpers import _card, _info, _section_title, _dd

import state


# ── Hypothesis-conclusion panel ───────────────────────────────

def _hypothesis_conclusion() -> html.Div:
    gov_row = state.GRANGER_DF[state.GRANGER_DF['Variable'] == 'Δlog(Gov Spending)']
    m2_row  = state.GRANGER_DF[state.GRANGER_DF['Variable'] == 'Δlog(M2)']
    gov_sig = not gov_row.empty and gov_row.iloc[0]['p-value'] < 0.05
    m2_sig  = not m2_row.empty  and m2_row.iloc[0]['p-value']  < 0.05
    gov_p   = gov_row.iloc[0]['p-value'] if not gov_row.empty else float('nan')
    m2_p    = m2_row.iloc[0]['p-value']  if not m2_row.empty  else float('nan')

    if gov_sig or m2_sig:
        verdict     = "✅ We REJECT the null hypothesis"
        verdict_sub = "Evidence supports the Political Business Cycle in Armenia."
        verdict_col = '#166534'
        verdict_bg  = '#f0fdf4'
        verdict_bdr = '#86efac'
    else:
        verdict     = "❌ We FAIL TO REJECT the null hypothesis"
        verdict_sub = "Insufficient evidence for a Political Business Cycle in Armenia."
        verdict_col = '#991b1b'
        verdict_bg  = '#fff1f2'
        verdict_bdr = '#fca5a5'

    rows = [
        {'Hypothesis': 'H₀: Gov Spending does NOT Granger-cause CPI',
         'p-value': gov_p, 'Decision': '✅ Reject H₀' if gov_sig else '❌ Fail to reject'},
        {'Hypothesis': 'H₀: M2 does NOT Granger-cause CPI',
         'p-value': m2_p,  'Decision': '✅ Reject H₀' if m2_sig  else '❌ Fail to reject'},
    ]

    return html.Div([
        _section_title(
            "Hypothesis Test Conclusion",
            "H₀ = elections/spending/M2 do not predict CPI changes  |  α = 0.05",
        ),
        html.Div([
            html.Div(verdict,     style={'fontSize': '18px', 'fontWeight': '800', 'color': verdict_col}),
            html.Div(verdict_sub, style={'fontSize': '14px', 'color': verdict_col, 'marginTop': '4px'}),
        ], style={
            'background': verdict_bg, 'border': f'1px solid {verdict_bdr}',
            'borderRadius': '8px', 'padding': '16px 20px', 'marginBottom': '16px',
        }),
        dash_table.DataTable(
            data=rows,
            columns=[{'name': c, 'id': c} for c in ['Hypothesis', 'p-value', 'Decision']],
            style_cell={'textAlign': 'left', 'fontSize': '13px', 'padding': '10px 14px',
                        'whiteSpace': 'normal', 'fontFamily': 'Inter,Arial'},
            style_header={'backgroundColor': NAVY, 'color': WHITE, 'fontWeight': '700'},
            style_data_conditional=[
                {'if': {'filter_query': '{Decision} contains "Reject H"', 'column_id': 'Decision'},
                 'color': '#166534', 'fontWeight': '700'},
                {'if': {'filter_query': '{Decision} contains "Fail"', 'column_id': 'Decision'},
                 'color': '#991b1b', 'fontWeight': '700'},
                {'if': {'row_index': 'odd'}, 'backgroundColor': LGRAY},
            ],
            style_table={'borderRadius': '8px', 'overflow': 'hidden'},
        ),
        html.P(
            "Note: Granger causality tests whether past values of X improve CPI forecasts. "
            "α = 0.05 significance level used throughout.",
            style={'color': DGRAY, 'fontSize': '12px', 'marginTop': '10px'},
        ),
    ])


# ── Tab layout ────────────────────────────────────────────────

def _tab_var(lang: str) -> html.Div:
    t = T[lang]
    return html.Div([
        _section_title(t['var_h'], t['var_sub']),
        _card(
            html.H4(t['var_what_h'], style={'color': NAVY, 'marginTop': 0}),
            html.P(t['var_what_p'], style={'color': '#334155', 'lineHeight': '1.8', 'fontSize': '14px'}),
            html.Div([
                html.Div([
                    html.Strong(t['box1h']), html.Br(),
                    html.Span(t['box1p'], style={'fontSize': '13px', 'color': DGRAY}),
                ], style={'flex': '1', 'padding': '12px', 'background': '#f8fafc',
                          'borderRadius': '8px', 'marginRight': '10px'}),
                html.Div([
                    html.Strong(t['box2h']), html.Br(),
                    html.Span(t['box2p'], style={'fontSize': '13px', 'color': DGRAY}),
                ], style={'flex': '1', 'padding': '12px', 'background': '#f8fafc',
                          'borderRadius': '8px', 'marginRight': '10px'}),
                html.Div([
                    html.Strong(t['box3h']), html.Br(),
                    html.Span(t['box3p'], style={'fontSize': '13px', 'color': DGRAY}),
                ], style={'flex': '1', 'padding': '12px', 'background': '#f8fafc', 'borderRadius': '8px'}),
            ], style={'display': 'flex', 'marginTop': '16px'}),
        ),
        _card(
            _section_title(t['irf_h'], t['irf_sub']),
            _info(t['irf_info']),
            html.Div([
                _dd('irf-imp',
                    [{'label': VAR_LABELS[v], 'value': v} for v in state.VAR_COLS],
                    'dlog_GOV_EXP', label=t['irf_imp']),
                html.Div(style={'width': '20px'}),
                _dd('irf-resp',
                    [{'label': VAR_LABELS[v], 'value': v} for v in state.VAR_COLS],
                    'dlog_CPI_index', label=t['irf_resp']),
            ], style={'display': 'flex', 'marginBottom': '16px'}),
            dcc.Graph(id='irf-fig'),
            html.Div(id='irf-explain', style={
                'background': '#eff6ff', 'border': '1px solid #bfdbfe',
                'borderRadius': '8px', 'padding': '14px 18px',
                'marginTop': '12px', 'color': '#1e3a8a',
                'fontSize': '14px', 'lineHeight': '1.7',
            }),
        ),
        _card(
            _section_title(t['granger_h'], t['granger_sub']),
            _info(t['granger_info']),
            html.Div(id='granger-tbl'),
        ),
        _card(_hypothesis_conclusion()),
    ])


# ── Callbacks ─────────────────────────────────────────────────

def register_callbacks(app):

    @app.callback(
        Output('irf-fig',     'figure'),
        Output('irf-explain', 'children'),
        Output('granger-tbl', 'children'),
        Input('irf-imp',      'value'),
        Input('irf-resp',     'value'),
        Input('lang',         'data'),
    )
    def upd_var(impulse, response, lang):
        imp_i = state.VAR_COLS.index(impulse)
        res_i = state.VAR_COLS.index(response)
        vals  = state.IRF.irfs[:, res_i, imp_i]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(range(len(vals))), y=vals,
            marker_color=[GREEN if v >= 0 else RED for v in vals],
            hovertemplate='Q%{x}: %{y:.5f}<extra></extra>',
        ))
        fig.add_hline(y=0, line_dash='dash', line_color='gray')
        fig.update_layout(
            xaxis_title='Quarters after shock',
            yaxis_title=f'Response of {VAR_LABELS.get(response, response)}',
            template='plotly_white', height=340, margin={'t': 10},
            xaxis={
                'tickvals': list(range(len(vals))),
                'ticktext': [f'Q{i}' for i in range(len(vals))],
            },
        )

        peak_q    = int(np.argmax(np.abs(vals)))
        direction = "increases" if vals[peak_q] > 0 else "decreases"
        imp_lbl   = VAR_LABELS.get(impulse,  impulse)
        resp_lbl  = VAR_LABELS.get(response, response)
        pbc_note  = (
            " This is the key PBC signature: government spending shocks feed into inflation."
            if impulse == 'dlog_GOV_EXP' and response == 'dlog_CPI_index' and vals[peak_q] > 0
            else ""
        )
        persists = sum(1 for v in vals[peak_q:] if (v > 0) == (vals[peak_q] > 0))
        explain  = (
            f"📈 A one-standard-deviation shock to {imp_lbl} causes {resp_lbl} to "
            f"{direction} most strongly at quarter {peak_q} after the shock "
            f"(peak magnitude: {vals[peak_q]:.5f}). "
            f"The effect persists in the same direction for {persists} quarter(s).{pbc_note}"
        )

        tbl = dash_table.DataTable(
            data=state.GRANGER_DF.to_dict('records'),
            columns=[{'name': c, 'id': c} for c in state.GRANGER_DF.columns],
            style_cell={'textAlign': 'left', 'fontSize': '13px',
                        'padding': '10px 16px', 'whiteSpace': 'normal'},
            style_header={'backgroundColor': NAVY, 'color': WHITE, 'fontWeight': '700'},
            style_data_conditional=[
                {'if': {'filter_query': '{Significant (p<0.05)} = "✅ Yes"'}, 'backgroundColor': '#f0fdf4'},
                {'if': {'filter_query': '{Significant (p<0.05)} = "❌ No"'},  'backgroundColor': '#fff1f2'},
                {'if': {'column_id': 'p-value'}, 'fontWeight': '700'},
            ],
            style_table={'borderRadius': '8px', 'overflow': 'hidden'},
        )

        return fig, explain, tbl
