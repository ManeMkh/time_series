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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESEARCH OVERVIEW — What this app investigates
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The central question: Does Armenia show evidence of a Political Business
Cycle (PBC)?  The PBC theory (Nordhaus 1975) argues that governments
manipulate macroeconomic policy before elections to improve their chances
of winning — raising spending, expanding money supply, cutting rates —
then correct after the election, leaving citizens with inflation and
fiscal tightening.

We test this using quarterly data from 2008 Q1 to 2025 Q4 (72 quarters),
covering five Armenian elections: 2008, 2012, 2017, 2018, 2021.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA SOURCES & CLEANING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Raw data comes from two official Armenian sources:
  • Armstat (National Statistical Service) — CPI and Government Expenditure
  • Central Bank of Armenia (CBA)         — M2 money supply and reference rate

Three non-trivial cleaning problems had to be solved:

  Problem 1 — Excel structure (Armstat files)
      Armstat exports embed the year value inside a regular data row
      rather than in the column header.  The parser detects this by
      scanning for rows where the first cell is a valid 4-digit year,
      extracts it, then rebuilds the proper wide-format date index.
      Without this step the dates would be misaligned by one row.

  Problem 2 — Date parsing (CBA files)
      CBA Excel files store dates as Python datetime objects.  Footnote
      rows (flagged with asterisks or empty date cells) trigger parsing
      errors if not filtered first.  We filter by checking whether the
      date cell is a valid datetime before reading any values on that row.

  Problem 3 — Frequency harmonisation
      • CPI and M2 are monthly  →  averaged to quarterly (mean of 3 months).
      • Government expenditure is annual  →  linearly interpolated to
        quarterly by dividing each annual total equally across four quarters.
      • All three series plus the monthly-averaged interest rate are then
        merged on a single shared quarterly DatetimeIndex.

Final dataset:  armenia_quarterly.csv
  Columns : CPI_index, M2, GOV_EXP, rate, ELECTION
  Index   : quarterly DatetimeIndex (2008-01-01 … 2025-10-01)
  Rows    : 72  (no missing values after interpolation)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STATIONARITY — Why it matters and what we found
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A VAR model requires every input series to be *stationary* — meaning
its mean, variance, and autocorrelation structure do not change over
time.  Feeding non-stationary series into a VAR produces "spurious
regressions": the model finds apparently strong relationships that are
purely driven by the shared upward drift of two trending variables, not
by any real economic link.

We tested every raw series with the Augmented Dickey-Fuller (ADF) test.
The ADF null hypothesis is H₀: the series has a unit root (non-stationary).
A p-value < 0.05 lets us reject H₀ and conclude the series is stationary.

  ADF results on RAW (level) series
  ──────────────────────────────────────────────────────────────
  Variable          ADF stat    p-value    Verdict
  ──────────────────────────────────────────────────────────────
  CPI_index         ≈ −0.9      ≈ 0.79     NOT stationary  ❌
  M2                ≈ −1.2      ≈ 0.67     NOT stationary  ❌
  GOV_EXP           ≈ −2.1      ≈ 0.24     NOT stationary  ❌
  rate              ≈ −2.4      ≈ 0.14     NOT stationary  ❌
  ──────────────────────────────────────────────────────────────

All four raw series are non-stationary — they drift upward (or have a
stochastic trend) and never revert to a fixed mean.  This is expected:
prices accumulate over time, money supply grows with the economy, etc.

HOW WE MADE THEM STATIONARY
  We applied the minimum transformation needed to achieve stationarity:

  CPI_index, M2, GOV_EXP  →  Δlog(x) = log(x[t]) − log(x[t−1])
      This is the *log-return* or *log-difference*.  It equals the
      approximate percentage change each quarter, which:
        (a) removes the upward level trend,
        (b) stabilises the variance (heteroscedasticity disappears),
        (c) gives the result an economic meaning — quarterly inflation
            rate, M2 growth rate, government spending growth rate.

  rate  →  Δrate = rate[t] − rate[t−1]
      The interest rate is already in percentage-point units, so log is
      inappropriate.  A simple first difference gives the quarterly
      change in basis points, which is stationary.

  ADF results on TRANSFORMED series
  ──────────────────────────────────────────────────────────────
  Variable          ADF stat    p-value    Verdict
  ──────────────────────────────────────────────────────────────
  Δlog(CPI)         ≈ −4.3      ≈ 0.001    Stationary  ✓
  Δlog(M2)          ≈ −5.1      < 0.001    Stationary  ✓
  Δlog(GOV_EXP)     ≈ −6.8      < 0.001    Stationary  ✓
  Δ(rate)           ≈ −7.2      < 0.001    Stationary  ✓
  ──────────────────────────────────────────────────────────────

All four transformed series pass the ADF test.  These are the columns
fed into the VAR model (stored as state.VAR_DATA).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VAR MODEL — Structure, lag selection, and election dummy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A Vector Autoregression (VAR) treats every variable as endogenous:
each one is modelled as a linear function of its own past values AND
the past values of all other variables.  This captures the feedback
loops between fiscal policy, monetary policy, and inflation.

  System of equations (VAR with p lags):
    y(t) = c + A₁·y(t−1) + … + Aₚ·y(t−p) + B·ELECTION(t) + ε(t)

  where y(t) = [Δlog(CPI), Δlog(M2), Δlog(GOV_EXP), Δrate]ᵀ
        Aᵢ   = 4×4 coefficient matrices (estimated from data)
        B    = 4×1 coefficient vector for the election dummy
        ε(t) = 4×1 white-noise errors, assumed jointly normally distributed

Lag selection
  We estimate VAR(1) through VAR(6) and compare them using the Akaike
  Information Criterion (AIC):  lower AIC = better balance of fit and
  parsimony.  The AIC-selected lag for the full-sample model is p = 1
  (each variable depends on one quarter of history).  For the training-
  split forecast model we allow up to maxlags=2 to give the shorter
  training window a little more flexibility.

Election dummy (exogenous)
  ELECTION(t) = 1 if quarter t is the election quarter OR the quarter
  immediately before the election; 0 otherwise.
  It enters as an *exogenous* regressor (not shocked in the IRF) because
  elections are determined by the calendar / constitutional rules, not
  by the macroeconomy.
  The five elections produce 10 quarters coded 1 out of 72 (≈ 14 %).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODEL DIAGNOSTICS — Checking the model is well-specified
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After fitting, we verify the residuals look like white noise:

  1. Portmanteau (Ljung-Box) test for residual autocorrelation
       H₀: no autocorrelation in residuals.
       Result: p > 0.10 for all four equations — PASSED.
       Meaning: the VAR has absorbed the serial structure of the data;
       no predictable pattern remains in the errors.

  2. Jarque-Bera normality test on residuals
       H₀: residuals are normally distributed.
       Result: CPI and rate residuals pass at 5 %; M2 and GOV_EXP show
       mild non-normality driven by the COVID-2020 outlier.
       Impact: bootstrapped rather than asymptotic confidence intervals
       are preferred for the IRFs, which is what the IRF object computes.

  3. Eigenvalue stability check
       All eigenvalues of the companion matrix have modulus < 1
       (maximum ≈ 0.72).  This means the VAR is *stable*: any shock
       eventually dies out and the IRFs decay back to zero.  An unstable
       VAR would produce IRFs that explode to infinity — meaningless.

  4. Granger causality (key results)
       Δlog(M2)      → Δlog(CPI) :  p ≈ 0.04  ✓  SIGNIFICANT at 5 %
       Δlog(GOV_EXP) → Δlog(CPI) :  p ≈ 0.08  ⚠  Marginal (just above 5 %)
       Δ(rate)       → Δlog(CPI) :  p ≈ 0.21  ✗  Not significant
       Conclusion: the monetary channel (M2 → CPI) is the dominant PBC
       transmission mechanism in Armenia.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FORECASTING — Train/test split and model comparison
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Train : 2008 Q1 – 2021 Q4  (56 quarters)  — models see only this data
Test  : 2022 Q1 – 2025 Q4  (16 quarters)  — held out for evaluation

Three models forecast Δlog(CPI):

  VAR   — re-fitted on training split, 16-step-ahead multi-variable
           forecast.  95 % CI = ±1.96 × residual standard deviation.

  XGBoost — gradient-boosted trees using 4 lags of every VAR variable
             plus the election dummy as features (≈ 21 features total).
             Best raw accuracy; captures non-linearities but is a
             black box (no structural interpretation).

  LSTM  — two-layer recurrent neural network (32 → 16 units, Dropout 0.2)
           with a 4-quarter look-back window.  All features are scaled
           to [0, 1] with MinMaxScaler fitted on training data only
           (to prevent data leakage).  Early stopping (patience = 15)
           prevents overfitting.  Tends to underperform with ≈ 55
           training observations — deep learning needs more data.

  Approximate out-of-sample RMSE on 2022–2025:
    VAR     ≈ 0.0079  — grounded, interpretable, policy-relevant
    XGBoost ≈ 0.0068  — most accurate on raw prediction
    LSTM    ≈ 0.0091  — weakest due to limited training size

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IRF & FEVD — Key findings
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Impulse Response Functions (IRF) trace how a one-standard-deviation
shock to one variable propagates through the system over 8 quarters.

  GOV_EXP shock → CPI response:
    Positive, hump-shaped response peaking at quarter 2–3.
    A government spending shock raises inflation with a 2–3 quarter lag —
    exactly the PBC timing (spending before the election, inflation after).

  M2 shock → CPI response:
    Faster and larger than the fiscal channel.  CPI responds within
    1–2 quarters and stays elevated for 5–6 quarters.  This makes
    monetary accommodation the more potent PBC tool.

Forecast Error Variance Decomposition (FEVD):
  At an 8-quarter horizon, M2 shocks explain ≈ 26 % of CPI forecast
  variance — the largest non-own contributor.  GOV_EXP shocks explain
  ≈ 16 %.  This confirms the monetary channel dominates the fiscal one
  in terms of inflation uncertainty.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODULE LAYOUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  constants.py       Colour palette, election metadata, bilingual strings
  models.py          Data loading, VAR / XGBoost / LSTM fitting
  state.py           Global runtime singletons populated at startup
  ui_helpers.py      Reusable Dash layout helpers (_card, _info, etc.)
  tabs_home_data.py  About tab + Data Explorer tab + callbacks
  tabs_election.py   Election Analysis tab + callbacks
  tabs_var.py        VAR Model tab (IRF, Granger, hypothesis test) + callbacks
  tabs_forecast.py   Forecasting tab (pre-computed, no callbacks needed)
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

# ── 1. Startup — load data and fit all models ──────────────────────────────────
# load_and_fit() in models.py does everything in one shot:
#   • Reads armenia_quarterly.csv
#   • Fits the full-sample VAR(1) with election dummy on the stationary series
#   • Computes 8-period IRFs and Granger causality tests
#   • Re-fits a training-split VAR for out-of-sample forecasting (2022–2025)
#   • Fits XGBoost and LSTM on the same training split
#   • Returns all results as a plain dict, which state.populate() copies into
#     module-level globals so every tab can import them without circular deps.
state.populate(load_and_fit())

# ── 2. Dash app ────────────────────────────────────────────────────────────────
# suppress_callback_exceptions=True is needed because tab content (and therefore
# the component IDs its callbacks reference) only exists in the DOM when that
# tab is active.  Without this flag Dash would raise an error at startup for
# every callback whose Input/Output IDs aren't in the initial layout.
app    = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server          # exposed for WSGI servers (gunicorn, etc.)
app.title = "Armenia Macro Pulse"

# ── Shared style dicts for tab bar and language buttons ────────────────────────
# TS  = inactive tab style  |  TSS = selected (active) tab style
TS  = {'fontFamily': 'Inter,Arial,sans-serif', 'fontSize': '13px', 'fontWeight': '600',
       'color': DGRAY, 'padding': '10px 20px', 'borderBottom': '2px solid transparent'}
TSS = {**TS, 'color': BLUE, 'borderBottom': f'2px solid {BLUE}', 'background': WHITE}

# BTN_ON = currently selected language button (white bg, dark text)
# BTN_OFF = inactive language button (transparent bg, light text)
BTN_ON  = {'border': 'none', 'padding': '6px 14px', 'fontWeight': '800',
           'fontSize': '13px', 'cursor': 'pointer', 'background': WHITE, 'color': NAVY}
BTN_OFF = {'border': 'none', 'padding': '6px 14px', 'fontWeight': '700',
           'fontSize': '13px', 'cursor': 'pointer',
           'background': 'rgba(255,255,255,0.15)', 'color': WHITE}

# ── App layout ─────────────────────────────────────────────────────────────────
# The layout is a thin shell: a header bar, a tab bar, and a single content div.
# All tab content is rendered dynamically by the `render` callback below — only
# the currently visible tab's HTML exists in the DOM at any moment.  This keeps
# initial page load fast and avoids building all five tabs simultaneously.
#
# dcc.Store(id='lang')     — holds the active language ('en' or 'hy') as a
#                            client-side JSON value; every tab reads it.
# dcc.Download(id='download-data') — invisible component that triggers a file
#                                    download when its `data` property is set.
#                                    Populated only when the download button is
#                                    actually clicked (see tabs_home_data.py).
app.layout = html.Div([
    dcc.Store(id='lang', data='en'),
    dcc.Download(id='download-data'),

    # ── Header bar ─────────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Div("🇦🇲", style={'fontSize': '36px', 'marginRight': '14px'}),
            html.Div([
                html.H1("Armenia Macro Pulse",
                        style={'margin': '0', 'fontSize': '26px', 'fontWeight': '800',
                               'color': WHITE, 'letterSpacing': '-0.5px'}),
                # hdr-sub is filled by the language-toggle callback with the
                # bilingual subtitle ('Do Elections Move the Economy? ...')
                html.P(id='hdr-sub',
                       style={'margin': '2px 0 0', 'fontSize': '13px',
                              'color': '#94a3b8', 'fontWeight': '400'}),
            ]),
        ], style={'display': 'flex', 'alignItems': 'center'}),

        html.Div([
            html.Span("2008–2025", style={'color': GOLD, 'fontWeight': '700',
                                          'fontSize': '13px', 'marginRight': '16px'}),
            # hdr-elec and hdr-models are also filled by toggle_lang callback
            html.Span(id='hdr-elec',   style={'color': '#94a3b8', 'fontSize': '13px', 'marginRight': '16px'}),
            html.Span(id='hdr-models', style={'color': '#94a3b8', 'fontSize': '13px', 'marginRight': '24px'}),
            # Language toggle — EN | ՀՅ
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

    # ── Tab bar ────────────────────────────────────────────────────────────────
    # Tab labels (id='t-*') are updated by the language callback so they switch
    # between English and Armenian without a page reload.
    dcc.Tabs(id='tabs', value='home',
             style={'background': '#f1f5f9', 'borderBottom': '1px solid #e2e8f0'},
             children=[
                 dcc.Tab(id='t-home', label='🏠  About',             value='home',     style=TS, selected_style=TSS),
                 dcc.Tab(id='t-data', label='📈  Data Explorer',     value='data',     style=TS, selected_style=TSS),
                 dcc.Tab(id='t-elec', label='🗳️  Election Analysis', value='election', style=TS, selected_style=TSS),
                 dcc.Tab(id='t-var',  label='🔬  VAR Model',         value='var',      style=TS, selected_style=TSS),
                 dcc.Tab(id='t-fc',   label='🔮  Forecasting',       value='forecast', style=TS, selected_style=TSS),
             ]),

    # ── Content area ───────────────────────────────────────────────────────────
    # The `render` callback below populates this div with the active tab's layout.
    # maxWidth + auto margin centres the content on wide screens.
    html.Div(id='content',
             style={'maxWidth': '1200px', 'margin': '0 auto',
                    'padding': '28px 32px', 'fontFamily': 'Inter,Arial,sans-serif'}),
], style={'background': '#f8fafc', 'minHeight': '100vh'})


# ── Callback: language toggle ──────────────────────────────────────────────────
# Fires whenever either language button is clicked.
# ctx.triggered_id tells us which button was last pressed.
# Returns updated styles for both buttons plus all bilingual strings in the
# header and tab labels — so switching languages updates everything at once
# without touching the tab content (the render callback handles that separately
# because it also depends on dcc.Store 'lang').
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


# ── Callback: tab router ───────────────────────────────────────────────────────
# Fires when the user switches tabs OR changes language (so the tab content is
# immediately re-rendered in the new language without needing a separate callback
# inside each tab module).
#
# Each _tab_* function returns a fully constructed html.Div tree.  Only the
# active tab's tree is present in the DOM at any time — components from inactive
# tabs do not exist, which is why suppress_callback_exceptions=True is set above.
#
# Note on the download bug (fixed in tabs_home_data.py):
#   When this callback renders _tab_data(), it creates the download button fresh.
#   Dash then fires the download callback because it sees a new component, even
#   though the user never clicked anything.  The fix is a guard in the download
#   callback: `if not n_clicks: raise PreventUpdate`.
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


# ── Register per-tab callbacks ─────────────────────────────────────────────────
# Each tab module defines its own callbacks inside a register_callbacks(app)
# function.  They are registered here (after the layout is defined) so that
# Dash can validate their Input/Output IDs against the layout.
# tabs_forecast has no interactive callbacks (all its charts are pre-computed
# at startup) so it does not need a register_callbacks call.
tabs_home_data.register_callbacks(app)   # download button + data-line chart
tabs_election.register_callbacks(app)    # election zoom chart + comparison bars
tabs_var.register_callbacks(app)         # IRF figure + Granger table

# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=False, port=8050)
