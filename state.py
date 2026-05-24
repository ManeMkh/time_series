"""
state.py
========
Global runtime state for the Armenia Macro Pulse dashboard.

All attributes are populated once at startup by app.py calling
`models.load_and_fit()`. Tab modules import this module to access
pre-computed data and model results without circular imports.

Attributes
----------
DATA        : pd.DataFrame  — raw quarterly dataset
FITTED      : VAR results object
VAR_DATA    : pd.DataFrame  — stationary VAR series
EXOG        : pd.Series     — election dummy
IRF         : IRF object
GRANGER_DF  : pd.DataFrame  — Granger causality results
TEST        : pd.DataFrame  — test-set (2022–2025)
FC_VAR      : pd.DataFrame  — VAR forecasts
RESID_STD   : pd.Series     — residual std per variable
Y_XGB       : pd.Series     — XGBoost test-set actuals
PREDS_XGB   : np.ndarray    — XGBoost predictions
RMSE_XGB    : float
Y_LSTM      : pd.Series | None
PREDS_LSTM  : np.ndarray | None
RMSE_LSTM   : float
RMSE_VAR    : float
VAR_COLS    : list[str]
NUMERIC     : list[str]     — raw variable names
ELEC_Q      : DatetimeIndex — election quarters
"""

# All attributes are set at runtime; None until populated.
DATA        = None
FITTED      = None
VAR_DATA    = None
EXOG        = None
IRF         = None
GRANGER_DF  = None
TEST        = None
FC_VAR      = None
RESID_STD   = None
Y_XGB       = None
PREDS_XGB   = None
RMSE_XGB    = None
Y_LSTM      = None
PREDS_LSTM  = None
RMSE_LSTM   = None
RMSE_VAR    = None
VAR_COLS    = None
NUMERIC     = None
ELEC_Q      = None


def populate(results: dict) -> None:
    """Copy model results dict into module-level globals."""
    g = globals()
    for key, val in results.items():
        g[key] = val
