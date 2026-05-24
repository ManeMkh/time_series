"""
app.py
======
Armenia Macro Pulse — main entry point.

Run:  python app.py
Open: http://127.0.0.1:8050

Startup sequence
----------------
1. Load data and fit all models  →  populate state module
2. Build Dash app and register all callbacks
3. Start the development server
"""

import dash
from dash import dcc, html, Input, Output, ctx

import state
from models import load_and_fit
from constants import NAVY, BLUE, GOLD, DGRAY, WHITE, T
from tabs_home_data import _tab_home, _tab_data
from tabs_election import _tab_elec
from tabs_var import _tab_var
from tabs_forecast import _tab_fc
import tabs_home_data
import tabs_election
import tabs_var

# ── 1. Startup — load data and fit models ─────────────────────
state.populate(load_and_fit())

# ── 2. Dash app ───────────────────────────────────────────────
app    = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.title = "Armenia Macro Pulse"

# Tab & button styles
TS  = {'fontFamily': 'Inter,Arial,sans-serif', 'fontSize': '13px', 'fontWeight': '600',
       'color': DGRAY, 'padding': '10px 20px', 'borderBottom': '2px solid transparent'}
TSS = {**TS, 'color': BLUE, 'borderBottom': f'2px solid {BLUE}', 'background': WHITE}

BTN_ON  = {'border': 'none', 'padding': '6px 14px', 'fontWeight': '800',
           'fontSize': '13px', 'cursor': 'pointer', 'background': WHITE, 'color': NAVY}
BTN_OFF = {'border': 'none', 'padding': '6px 14px', 'fontWeight': '700',
           'fontSize': '13px', 'cursor': 'pointer',
           'background': 'rgba(255,255,255,0.15)', 'color': WHITE}

# ── Layout ────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Store(id='lang', data='en'),
    dcc.Download(id='download-data'),

    # Header
    html.Div([
        html.Div([
            html.Div("🇦🇲", style={'fontSize': '36px', 'marginRight': '14px'}),
            html.Div([
                html.H1("Armenia Macro Pulse",
                        style={'margin': '0', 'fontSize': '26px', 'fontWeight': '800',
                               'color': WHITE, 'letterSpacing': '-0.5px'}),
                html.P(id='hdr-sub',
                       style={'margin': '2px 0 0', 'fontSize': '13px',
                              'color': '#94a3b8', 'fontWeight': '400'}),
            ]),
        ], style={'display': 'flex', 'alignItems': 'center'}),

        html.Div([
            html.Span("2008–2025", style={'color': GOLD, 'fontWeight': '700',
                                          'fontSize': '13px', 'marginRight': '16px'}),
            html.Span(id='hdr-elec',   style={'color': '#94a3b8', 'fontSize': '13px', 'marginRight': '16px'}),
            html.Span(id='hdr-models', style={'color': '#94a3b8', 'fontSize': '13px', 'marginRight': '24px'}),
            html.Div([
                html.Button('EN', id='btn-en', n_clicks=0,
                            style={**BTN_ON,  'borderRadius': '6px 0 0 6px'}),
                html.Button('ՀՅ', id='btn-hy', n_clicks=0,
                            style={**BTN_OFF, 'borderRadius': '0 6px 6px 0'}),
            ], style={'display': 'flex'}),
        ], style={'display': 'flex', 'alignItems': 'center'}),
    ], style={
        'background': f'linear-gradient(135deg,{NAVY} 0%,#1e3a5f 100%)',
        'padding': '18px 32px', 'display': 'flex',
        'justifyContent': 'space-between', 'alignItems': 'center',
    }),

    # Tabs
    dcc.Tabs(id='tabs', value='home',
             style={'background': '#f1f5f9', 'borderBottom': '1px solid #e2e8f0'},
             children=[
                 dcc.Tab(id='t-home', label='🏠  About',             value='home',     style=TS, selected_style=TSS),
                 dcc.Tab(id='t-data', label='📈  Data Explorer',     value='data',     style=TS, selected_style=TSS),
                 dcc.Tab(id='t-elec', label='🗳️  Election Analysis', value='election', style=TS, selected_style=TSS),
                 dcc.Tab(id='t-var',  label='🔬  VAR Model',         value='var',      style=TS, selected_style=TSS),
                 dcc.Tab(id='t-fc',   label='🔮  Forecasting',       value='forecast', style=TS, selected_style=TSS),
             ]),

    html.Div(id='content',
             style={'maxWidth': '1200px', 'margin': '0 auto',
                    'padding': '28px 32px', 'fontFamily': 'Inter,Arial,sans-serif'}),
], style={'background': '#f8fafc', 'minHeight': '100vh'})


# ── Callbacks — language toggle ───────────────────────────────
@app.callback(
    Output('lang',       'data'),
    Output('btn-en',     'style'),
    Output('btn-hy',     'style'),
    Output('hdr-sub',    'children'),
    Output('hdr-elec',   'children'),
    Output('hdr-models', 'children'),
    Output('t-home',     'label'),
    Output('t-data',     'label'),
    Output('t-elec',     'label'),
    Output('t-var',      'label'),
    Output('t-fc',       'label'),
    Input('btn-en',      'n_clicks'),
    Input('btn-hy',      'n_clicks'),
)
def toggle_lang(n_en, n_hy):
    lang   = 'hy' if ctx.triggered_id == 'btn-hy' else 'en'
    t      = T[lang]
    on_en  = {**BTN_ON,  'borderRadius': '6px 0 0 6px'}
    off_en = {**BTN_OFF, 'borderRadius': '6px 0 0 6px'}
    on_hy  = {**BTN_ON,  'borderRadius': '0 6px 6px 0'}
    off_hy = {**BTN_OFF, 'borderRadius': '0 6px 6px 0'}
    return (
        lang,
        on_en  if lang == 'en' else off_en,
        on_hy  if lang == 'hy' else off_hy,
        t['subtitle'], t['span_elec'], t['span_models'],
        t['tab_home'], t['tab_data'], t['tab_elec'], t['tab_var'], t['tab_fc'],
    )


# ── Callbacks — tab router ────────────────────────────────────
@app.callback(
    Output('content', 'children'),
    Input('tabs',     'value'),
    Input('lang',     'data'),
)
def render(tab, lang):
    lang = lang or 'en'
    if tab == 'home':     return _tab_home(lang)
    if tab == 'data':     return _tab_data(lang)
    if tab == 'election': return _tab_elec(lang)
    if tab == 'var':      return _tab_var(lang)
    if tab == 'forecast': return _tab_fc(lang)
    return html.Div()


# ── Register per-tab callbacks ────────────────────────────────
tabs_home_data.register_callbacks(app)
tabs_election.register_callbacks(app)
tabs_var.register_callbacks(app)

# ── Run ───────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=False, port=8050)
