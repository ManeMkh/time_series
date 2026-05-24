"""
tabs_forecast.py
================
Layout builder for the Forecasting tab (_tab_fc).
All charts are pre-computed at startup so no Dash callbacks are needed here.
"""

import numpy as np
import plotly.graph_objects as go
from dash import dcc, html

from constants import (
    NAVY, BLUE, GREEN, GOLD, DGRAY, WHITE,
    CARD, T,
)
from ui_helpers import _card, _section_title, _badge

import state


# ── Figure helpers ────────────────────────────────────────────

def _fc_line_fig(actual_label: str = 'Actual') -> go.Figure:
    """Forecast-vs-actual line chart with VAR confidence band."""
    actual = state.TEST['dlog_CPI_index']
    var_fc = state.FC_VAR['dlog_CPI_index']
    var_lo = var_fc - 1.96 * state.RESID_STD['dlog_CPI_index']
    var_hi = var_fc + 1.96 * state.RESID_STD['dlog_CPI_index']

    fig = go.Figure()
    # 95 % CI shading
    fig.add_trace(go.Scatter(
        x=list(var_hi.index) + list(var_lo.index[::-1]),
        y=list(var_hi.values) + list(var_lo.values[::-1]),
        fill='toself', fillcolor='rgba(37,99,235,0.12)',
        line={'color': 'rgba(0,0,0,0)'}, name='VAR 95% CI', hoverinfo='skip',
    ))
    # Actual
    fig.add_trace(go.Scatter(
        x=actual.index, y=actual.values, mode='lines+markers',
        name=actual_label, line={'color': 'black', 'width': 2.5}, marker={'size': 5},
        hovertemplate=f'<b>{actual_label}</b> %{{x|%Y-%m}}: %{{y:.5f}}<extra></extra>',
    ))
    # VAR forecast
    fig.add_trace(go.Scatter(
        x=var_fc.index, y=var_fc.values, mode='lines+markers',
        name=f'VAR (RMSE={state.RMSE_VAR:.5f})',
        line={'color': BLUE, 'dash': 'dash'}, marker={'size': 4},
        hovertemplate='<b>VAR</b> %{x|%Y-%m}: %{y:.5f}<extra></extra>',
    ))
    # XGBoost
    if state.PREDS_XGB is not None:
        xidx = state.TEST.index[-len(state.PREDS_XGB):]
        fig.add_trace(go.Scatter(
            x=xidx, y=state.PREDS_XGB, mode='lines+markers',
            name=f'XGBoost (RMSE={state.RMSE_XGB:.5f})',
            line={'color': GREEN, 'dash': 'dot'}, marker={'size': 4},
            hovertemplate='<b>XGBoost</b> %{x|%Y-%m}: %{y:.5f}<extra></extra>',
        ))
    # LSTM
    if state.PREDS_LSTM is not None:
        lidx = (state.Y_LSTM.index if state.Y_LSTM is not None
                else state.TEST.index[-len(state.PREDS_LSTM):])
        fig.add_trace(go.Scatter(
            x=lidx, y=state.PREDS_LSTM, mode='lines+markers',
            name=f'LSTM (RMSE={state.RMSE_LSTM:.5f})',
            line={'color': '#7c3aed', 'dash': 'dashdot'},
            marker={'size': 4, 'symbol': 'diamond'},
            hovertemplate='<b>LSTM</b> %{x|%Y-%m}: %{y:.5f}<extra></extra>',
        ))

    fig.update_layout(
        xaxis_title='Quarter', yaxis_title='Δlog(CPI)',
        template='plotly_white', height=380,
        legend={'orientation': 'h', 'y': -0.2},
        hovermode='x unified', margin={'t': 10},
    )
    return fig


def _fc_bar_fig(y_label: str = 'RMSE (lower is better)') -> go.Figure:
    """Bar chart comparing model RMSE scores."""
    labels = ['VAR', 'XGBoost', 'LSTM']
    rmses  = [state.RMSE_VAR, state.RMSE_XGB, state.RMSE_LSTM]
    best_i = int(np.argmin(rmses))

    fig = go.Figure(go.Bar(
        x=labels, y=rmses,
        marker_color=[BLUE, GREEN, '#7c3aed'],
        marker_line_color=[GOLD if i == best_i else WHITE for i in range(3)],
        marker_line_width=[3 if i == best_i else 1 for i in range(3)],
        text=[f'{r:.5f}' for r in rmses], textposition='outside',
        hovertemplate='<b>%{x}</b> RMSE: %{y:.5f}<extra></extra>',
    ))
    fig.add_annotation(
        x=labels[best_i], y=rmses[best_i], text="🏆",
        showarrow=True, arrowhead=2, arrowcolor=GOLD, ay=-40,
    )
    fig.update_layout(yaxis_title=y_label, template='plotly_white',
                      height=300, margin={'t': 30})
    return fig


# ── Tab layout ────────────────────────────────────────────────

def _tab_fc(lang: str) -> html.Div:
    t     = T[lang]
    rmses = [state.RMSE_VAR, state.RMSE_XGB, state.RMSE_LSTM]
    best  = ['VAR', 'XGBoost', 'LSTM'][int(np.argmin(rmses))]

    model_card_style = {
        'flex': '1', 'padding': '14px',
        'borderRadius': '8px', 'marginRight': '10px',
    }

    return html.Div([
        _section_title(t['fc_h'], t['fc_sub']),
        _card(
            html.H4(t['fc_what_h'], style={'color': NAVY, 'marginTop': 0}),
            html.P(t['fc_what_p'],
                   style={'color': '#334155', 'lineHeight': '1.8', 'fontSize': '14px'}),
            html.Div([
                html.Div([
                    html.Strong("VAR", style={'color': BLUE}),
                    _badge(t['badge_econ']),
                    html.P(t['var_d'],
                           style={'fontSize': '13px', 'color': DGRAY, 'marginTop': '6px'}),
                ], style={**model_card_style,
                          'background': '#eff6ff', 'borderTop': f'3px solid {BLUE}'}),
                html.Div([
                    html.Strong("XGBoost", style={'color': GREEN}),
                    _badge(t['badge_ml'], GREEN),
                    html.P(t['xgb_d'],
                           style={'fontSize': '13px', 'color': DGRAY, 'marginTop': '6px'}),
                ], style={**model_card_style,
                          'background': '#f0fdf4', 'borderTop': f'3px solid {GREEN}'}),
                html.Div([
                    html.Strong("LSTM", style={'color': '#7c3aed'}),
                    _badge(t['badge_dl'], '#7c3aed'),
                    html.P(t['lstm_d'],
                           style={'fontSize': '13px', 'color': DGRAY, 'marginTop': '6px'}),
                ], style={**model_card_style,
                          'background': '#faf5ff', 'borderTop': '3px solid #7c3aed',
                          'marginRight': '0'}),
            ], style={'display': 'flex', 'marginTop': '16px'}),
        ),
        _card(
            _section_title(t['fc_line_h'], t['fc_line_sub']),
            dcc.Graph(figure=_fc_line_fig(t['actual'])),
        ),
        _card(
            _section_title(t['fc_bar_h'], t['fc_bar_sub']),
            html.Div([
                dcc.Graph(figure=_fc_bar_fig(t['lower_better']), style={'flex': '1'}),
                html.Div([
                    html.Div("🏆", style={'fontSize': '36px', 'marginBottom': '8px'}),
                    html.H4(f"{best} {t['wins']}",
                            style={'color': NAVY, 'marginTop': 0, 'marginBottom': '8px'}),
                    html.P(f"{t['best_rmse']}{min(rmses):.5f}",
                           style={'color': DGRAY, 'fontSize': '13px'}),
                    html.Hr(style={'borderColor': '#e2e8f0'}),
                    html.P(t['fc_verdict_p'],
                           style={'color': '#334155', 'fontSize': '13px', 'lineHeight': '1.7'}),
                ], style={**CARD, 'flex': '1', 'margin': '0 0 0 20px'}),
            ], style={'display': 'flex', 'alignItems': 'center'}),
        ),
    ])
