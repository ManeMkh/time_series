"""
ui_helpers.py
=============
Reusable Dash / HTML helper functions used across all tab layouts:
  _card, _info, _section_title, _dd, _badge, _bands
"""

import pandas as pd
from dash import dcc, html

from constants import CARD, INFO, NAVY, BLUE, DGRAY, WHITE, RED, GOLD


def _card(*children, extra: dict = None) -> html.Div:
    """Wrap children in a raised white card."""
    return html.Div(children, style={**CARD, **(extra or {})})


def _info(text) -> html.Div:
    """Blue info banner with an ℹ️ icon."""
    return html.Div([html.Span("ℹ️  "), text], style=INFO)


def _section_title(text: str, sub: str = None) -> html.Div:
    """Bold navy section header with an optional grey subtitle."""
    return html.Div([
        html.H3(text, style={'color': NAVY, 'marginBottom': '4px', 'fontWeight': '700'}),
        html.P(sub, style={'color': DGRAY, 'fontSize': '13px', 'marginTop': '0'}) if sub else None,
    ], style={'marginBottom': '12px'})


def _dd(id_: str, options: list, value, label: str = None) -> html.Div:
    """Labelled Dropdown with a fixed width of 240 px."""
    return html.Div([
        html.Label(
            label,
            style={'fontSize': '12px', 'color': DGRAY, 'fontWeight': '600', 'marginBottom': '4px'},
        ) if label else None,
        dcc.Dropdown(id=id_, options=options, value=value, clearable=False,
                     style={'fontSize': '13px'}),
    ], style={'width': '240px'})


def _badge(text: str, color: str = BLUE) -> html.Span:
    """Small pill-shaped badge."""
    return html.Span(text, style={
        'background': color, 'color': WHITE, 'borderRadius': '99px',
        'padding': '2px 10px', 'fontSize': '11px', 'fontWeight': '700',
        'marginLeft': '8px', 'verticalAlign': 'middle',
    })


def _bands(fig, elec_q) -> None:
    """
    Add faint red vertical bands to *fig* at every election quarter.

    Parameters
    ----------
    fig    : plotly Figure
    elec_q : DatetimeIndex of election quarters (from global state)
    """
    for eq in elec_q:
        fig.add_vrect(
            x0=eq,
            x1=eq + pd.DateOffset(months=3),
            fillcolor=RED,
            opacity=0.07,
            line_width=0,
        )
