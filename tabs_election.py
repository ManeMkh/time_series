"""
tabs_election.py
================
Layout builder and Dash callbacks for the Election Analysis tab:
  - _tab_elec
  - _elec_compare_fig
  - upd_elec_bars
  - upd_elec
"""

import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, dash_table, Input, Output

from constants import (
    NAVY, BLUE, GREEN, GOLD, DGRAY, LGRAY, WHITE,
    ELECTIONS, ELEC_STARTS, VAR_DESC, T,
)
from ui_helpers import _card, _info, _section_title, _dd

import state


# ── Comparison figure (all elections, CPI indexed to 100) ─────

def _elec_compare_fig() -> go.Figure:
    fig = go.Figure()
    for yr, info in ELECTIONS.items():
        elec_d = pd.Timestamp(ELEC_STARTS[yr])
        s      = state.DATA['CPI_index'].dropna()
        idx    = int(s.index.get_indexer([elec_d], method='nearest')[0])
        if idx < 0:
            continue
        seg  = s.iloc[max(0, idx - 4): min(len(s), idx + 6)]
        base = seg.iloc[min(4, len(seg) - 1)]
        if not base or pd.isna(base):
            continue
        x = list(range(-min(4, idx), len(seg) - min(4, idx)))
        y = (seg.values / base * 100).tolist()
        fig.add_trace(go.Scatter(
            x=x, y=y, mode='lines+markers', name=str(yr),
            line={'color': info['color'], 'width': 2.5}, marker={'size': 6},
            hovertemplate=f'<b>{yr}</b> Q%{{x:+d}}: %{{y:.1f}}<extra></extra>',
        ))
    fig.add_vline(x=0, line_dash='dash', line_color='#dc2626', line_width=1.5,
                  annotation_text='Election', annotation_position='top right')
    fig.add_hline(y=100, line_dash='dot', line_color='gray', line_width=1)
    fig.update_layout(
        xaxis_title='Quarters relative to election (0 = election)',
        yaxis_title='CPI indexed to 100',
        template='plotly_white', height=380,
        hovermode='x unified', legend={'title': 'Year'},
    )
    return fig


# ── Tab layout ────────────────────────────────────────────────

def _tab_elec(lang: str) -> html.Div:
    t = T[lang]
    return html.Div([
        _section_title(t['elec_h'], t['elec_sub']),
        _info(t['elec_info']),
        _card(
            html.Div([
                _dd('elec-yr',
                    [{'label': str(yr), 'value': yr} for yr in ELECTIONS],
                    2008, label=t['elec_yr']),
                html.Div(style={'width': '24px'}),
                _dd('elec-var',
                    [{'label': VAR_DESC[v][0], 'value': v} for v in state.NUMERIC],
                    'CPI_index', label=t['elec_vr']),
            ], style={'display': 'flex', 'alignItems': 'flex-end', 'marginBottom': '20px'}),
            dcc.Graph(id='elec-zoom'),
            html.Div(id='elec-tbl'),
        ),
        _card(
            _section_title(t['elec_comp_h'], t['elec_comp_sub']),
            dcc.Graph(id='elec-comp', figure=_elec_compare_fig()),
        ),
        _card(
            _section_title(
                "Election Comparison — Before / During / After",
                "Grouped bars show the average of the selected variable across all elections. "
                "Spot which elections had the biggest pre-election surges.",
            ),
            dcc.Graph(id='elec-bars'),
        ),
    ])


# ── Callbacks ─────────────────────────────────────────────────

def register_callbacks(app):

    @app.callback(
        Output('elec-bars', 'figure'),
        Input('elec-var',   'value'),
    )
    def upd_elec_bars(var):
        periods  = ['Before', 'During', 'After']
        colors_p = [BLUE, GOLD, GREEN]
        bar_data = {p: [] for p in periods}
        yr_labels = []

        for yr in ELECTIONS:
            elec_d = pd.Timestamp(ELEC_STARTS[yr])
            s      = state.DATA[var].dropna()
            idx    = int(s.index.get_indexer([elec_d], method='nearest')[0])
            if idx < 0:
                continue
            seg = s.iloc[max(0, idx - 4): min(len(s), idx + 5)]
            bm  = seg.index < elec_d - pd.DateOffset(months=3)
            dm  = (seg.index >= elec_d - pd.DateOffset(months=3)) & (seg.index <= elec_d)
            am  = seg.index > elec_d
            bar_data['Before'].append(round(seg[bm].mean(), 2))
            bar_data['During'].append(round(seg[dm].mean(), 2))
            bar_data['After'].append(round(seg[am].mean(), 2))
            yr_labels.append(str(yr))

        fig = go.Figure()
        for period, color in zip(periods, colors_p):
            fig.add_trace(go.Bar(
                name=period, x=yr_labels, y=bar_data[period],
                marker_color=color,
                hovertemplate=f'<b>{period}</b> %{{x}}: %{{y:,.2f}}<extra></extra>',
            ))
        fig.update_layout(
            barmode='group', template='plotly_white', height=340,
            xaxis_title='Election year', yaxis_title=VAR_DESC[var][0],
            legend={'title': 'Period'}, margin={'t': 10},
        )
        return fig

    @app.callback(
        Output('elec-zoom', 'figure'),
        Output('elec-tbl',  'children'),
        Input('elec-yr',    'value'),
        Input('elec-var',   'value'),
        Input('lang',       'data'),
    )
    def upd_elec(yr, var, lang):
        t      = T[lang or 'en']
        yr     = int(yr)
        color  = ELECTIONS[yr]['color']
        elec_d = pd.Timestamp(ELEC_STARTS[yr])
        s      = state.DATA[var].dropna()

        idx = int(s.index.get_indexer([elec_d], method='nearest')[0])
        if idx < 0:
            idx = 0
        seg = s.iloc[max(0, idx - 6): min(len(s), idx + 7)]

        fig = go.Figure()
        fig.add_vrect(
            x0=elec_d - pd.DateOffset(months=3),
            x1=elec_d + pd.DateOffset(months=3),
            fillcolor=color, opacity=0.12, line_width=0,
            annotation_text='Election window', annotation_position='top left',
        )
        fig.add_trace(go.Scatter(
            x=seg.index, y=seg.values, mode='lines+markers',
            line={'color': color, 'width': 2.5}, marker={'size': 7, 'color': color},
            name=VAR_DESC[var][0],
            hovertemplate='<b>%{x|%Y-%m}</b>: %{y:,.2f}<extra></extra>',
        ))
        fig.update_layout(
            title=f'{VAR_DESC[var][0]} — {yr} election',
            template='plotly_white', height=340, margin={'t': 50},
        )

        bm = seg.index < elec_d - pd.DateOffset(months=3)
        dm = (seg.index >= elec_d - pd.DateOffset(months=3)) & (seg.index <= elec_d)
        am = seg.index > elec_d
        bv, dv, av = seg[bm].mean(), seg[dm].mean(), seg[am].mean()

        rows = [
            {t['col_period']: t['period_b'], 'Mean': round(bv, 2), t['col_ch']: '—'},
            {t['col_period']: t['period_d'], 'Mean': round(dv, 2),
             t['col_ch']: f'{((dv / bv - 1) * 100):+.1f}%' if bv else '—'},
            {t['col_period']: t['period_a'], 'Mean': round(av, 2),
             t['col_ch']: f'{((av / dv - 1) * 100):+.1f}%' if dv else '—'},
        ]
        tbl = dash_table.DataTable(
            data=rows,
            columns=[{'name': c, 'id': c} for c in [t['col_period'], 'Mean', t['col_ch']]],
            style_cell={'textAlign': 'left', 'fontSize': '13px', 'padding': '10px 14px'},
            style_header={'backgroundColor': color, 'color': WHITE, 'fontWeight': '700'},
            style_data_conditional=[{
                'if': {'row_index': 1},
                'backgroundColor': '#fef3c7', 'fontWeight': '600',
            }],
            style_table={
                'width': '560px', 'borderRadius': '8px',
                'overflow': 'hidden', 'marginTop': '16px',
            },
        )

        # Smart PBC interpretation
        bd_chg = ((dv / bv - 1) * 100) if bv and not pd.isna(bv) and not pd.isna(dv) else 0
        da_chg = ((av / dv - 1) * 100) if dv and not pd.isna(dv) and not pd.isna(av) else 0
        var_name = VAR_DESC[var][0]

        if abs(bd_chg) < 0.5:
            trend = f"virtually no change ({bd_chg:+.1f}%) in {var_name} during the election window"
            pbc   = "This provides weak evidence for the PBC hypothesis for this election."
        elif bd_chg > 0:
            trend = f"a {bd_chg:+.1f}% increase in {var_name} during the election window"
            pbc   = ("This is consistent with the Political Business Cycle hypothesis — "
                     "politicians appear to have expanded this variable before the vote.")
        else:
            trend = f"a {bd_chg:+.1f}% decrease in {var_name} during the election window"
            pbc   = "This runs counter to the typical PBC pattern for this variable."

        after_note = (
            f" After the election, {var_name} {'rose' if da_chg > 0 else 'fell'} "
            f"by {abs(da_chg):.1f}% — "
            f"{'a typical post-election correction.' if (bd_chg > 0 and da_chg < 0) else 'no strong reversal observed.'}"
        )

        interp = html.Div([
            html.Strong(f"📊 What does this tell us about {yr}?  "),
            html.Span(f"There was {trend}. {pbc}{after_note}"),
        ], style={
            'background': '#eff6ff', 'border': '1px solid #bfdbfe',
            'borderRadius': '8px', 'padding': '14px 18px',
            'marginBottom': '18px', 'color': '#1e3a8a',
            'fontSize': '14px', 'lineHeight': '1.7', 'marginTop': '14px',
        })

        return fig, html.Div([tbl, interp])
