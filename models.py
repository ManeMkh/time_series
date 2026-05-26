"""
models.py
=========
Data loading and all statistical / ML model fitting:
  - VAR (Vector Autoregression) with Granger causality
  - XGBoost
  - LSTM (optional, requires PyTorch)

Call `load_and_fit()` once at startup; it returns a ModelResults dataclass
that the rest of the app can import from `state.py`.
"""

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import grangercausalitytests
import os
import random

from constants import VAR_LABELS

# ── Optional PyTorch / LSTM ────────────────────────────────────
try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset
    _LSTM_AVAILABLE = True
except ImportError:
    _LSTM_AVAILABLE = False


# ── PyTorch LSTM model definition ─────────────────────────────

if _LSTM_AVAILABLE:
    class LSTMModel(nn.Module):
        def __init__(self, n_features: int, hidden1: int = 32, hidden2: int = 16,
                     dropout: float = 0.2):
            super().__init__()
            self.lstm1   = nn.LSTM(n_features, hidden1, batch_first=True)
            self.drop1   = nn.Dropout(dropout)
            self.lstm2   = nn.LSTM(hidden1, hidden2, batch_first=True)
            self.drop2   = nn.Dropout(dropout)
            self.fc      = nn.Linear(hidden2, 1)

        def forward(self, x):
            out, _ = self.lstm1(x)           # (batch, seq, hidden1)
            out     = self.drop1(out)
            out, _ = self.lstm2(out)          # (batch, seq, hidden2)
            out     = self.drop2(out[:, -1])  # take last time-step
            return self.fc(out)               # (batch, 1)


# ── Data loading ──────────────────────────────────────────────

def load_data(path: str = 'armenia_quarterly.csv') -> pd.DataFrame:
    """Read the cleaned quarterly dataset from CSV."""
    return pd.read_csv(path, index_col=0, parse_dates=True)


# ── VAR model ─────────────────────────────────────────────────

def fit_var(data: pd.DataFrame):
    """
    Fit a VAR model on the four stationary macro variables.

    Returns
    -------
    fitted     : fitted VAR results object
    var_data   : DataFrame of stationary series used in the VAR
    exog       : election dummy series aligned to var_data
    irf        : IRF object (8-period impulse response functions)
    granger_df : DataFrame with Granger causality test results
    """
    dm = data.copy()
    for v in ['CPI_index', 'M2', 'GOV_EXP']:
        dm[f'log_{v}']  = np.log(dm[v])
        dm[f'dlog_{v}'] = dm[f'log_{v}'].diff()
    dm['d_rate'] = dm['rate'].diff()

    var_cols = ['dlog_CPI_index', 'dlog_M2', 'dlog_GOV_EXP', 'd_rate']
    var_data = dm[var_cols].dropna()
    exog     = dm['ELECTION'].reindex(var_data.index).fillna(0)

    fitted = VAR(var_data, exog=exog).fit(maxlags=4, ic='aic', trend='c')
    irf    = fitted.irf(periods=8)

    # Granger causality: does each macro variable predict CPI?
    rows = []
    for cause in ['dlog_M2', 'dlog_GOV_EXP', 'd_rate']:
        td  = var_data[['dlog_CPI_index', cause]].dropna()
        res = grangercausalitytests(td, maxlag=4, verbose=False)
        p   = res[1][0]['ssr_ftest'][1]
        rows.append({
            'Variable':              VAR_LABELS.get(cause, cause),
            'p-value':               round(p, 4),
            'Significant (p<0.05)':  '✅ Yes' if p < 0.05 else '❌ No',
            'Interpretation':        'Predicts CPI' if p < 0.05 else 'No predictive power',
        })

    return fitted, var_data, exog, irf, pd.DataFrame(rows)


# ── VAR forecast ─────────────────────────────────────────────

def var_forecast(var_data: pd.DataFrame, exog: pd.Series):
    """
    Re-fit VAR on the training split and produce out-of-sample forecasts.

    Returns
    -------
    test      : test-set DataFrame
    fc_df     : forecast DataFrame (same columns as var_data)
    resid_std : Series of per-column residual standard deviations
    """
    split    = '2022-01-01'
    train    = var_data[var_data.index < split]
    test     = var_data[var_data.index >= split]
    exog_tr  = exog[exog.index < split]
    exog_te  = exog[exog.index >= split]

    fitted_tr = VAR(train, exog=exog_tr).fit(maxlags=2, trend='c')
    lag       = fitted_tr.k_ar
    fc_vals   = fitted_tr.forecast(
        y=train.values[-lag:],
        steps=len(test),
        exog_future=exog_te.values.reshape(-1, 1),
    )
    fc_df = pd.DataFrame(fc_vals, index=test.index, columns=var_data.columns)
    return test, fc_df, fitted_tr.resid.std()


# ── XGBoost forecast ─────────────────────────────────────────

def xgb_forecast(var_data: pd.DataFrame, exog: pd.Series):
    """
    Gradient-boosted tree forecast for Δlog(CPI).
    Uses 4 lags of all VAR variables plus the election dummy as features.

    Returns
    -------
    yte   : actual test-set target Series
    preds : numpy array of predictions
    rmse  : float
    """
    split, target = '2022-01-01', 'dlog_CPI_index'
    df = var_data.copy()
    df['ELECTION'] = exog.reindex(df.index).fillna(0)

    for lag in range(1, 5):
        for col in var_data.columns:
            df[f'{col}_lag{lag}'] = df[col].shift(lag)

    df   = df.dropna()
    feat = [c for c in df.columns if c != target]
    Xtr, ytr = df[df.index < split][feat],  df[df.index < split][target]
    Xte, yte = df[df.index >= split][feat], df[df.index >= split][target]

    model = xgb.XGBRegressor(
        n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42
    )
    model.fit(Xtr, ytr)
    preds = model.predict(Xte)
    return yte, preds, float(np.sqrt(mean_squared_error(yte, preds)))


# ── LSTM forecast ─────────────────────────────────────────────

def lstm_forecast(var_data: pd.DataFrame, exog: pd.Series):
    """
    Two-layer LSTM forecast for Δlog(CPI) with a 4-quarter look-back window.
    Falls back gracefully to (None, None, nan) when PyTorch is not installed.

    Returns
    -------
    yte_s : actual test-set target Series (with DatetimeIndex)
    preds : numpy array of predictions
    rmse  : float
    """
    if not _LSTM_AVAILABLE:
        return None, None, float('nan')

    # ── Reproducibility seeds ─────────────────────────────────
    os.environ['PYTHONHASHSEED'] = '42'
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)

    split  = '2022-01-01'
    target = 'dlog_CPI_index'
    SEQ    = 4                        # look-back window (quarters)
    N_FEAT = var_data.shape[1] + 1   # +1 for election dummy

    df = var_data.copy()
    df['ELECTION'] = exog.reindex(df.index).fillna(0)
    df = df.dropna()

    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()

    # Fit scalers on training data only (avoid data leakage)
    df_train = df[df.index < split]
    scaler_X.fit(df_train.values)
    scaler_y.fit(df_train[[target]].values)

    X_all = scaler_X.transform(df.values)
    y_all = scaler_y.transform(df[[target]].values)

    # Build sequences
    Xs, ys = [], []
    for i in range(SEQ, len(X_all)):
        Xs.append(X_all[i - SEQ:i])
        ys.append(y_all[i])
    Xs = np.array(Xs, dtype=np.float32)
    ys = np.array(ys, dtype=np.float32)

    seq_idx    = df.index[SEQ:]
    train_mask = seq_idx < split
    test_mask  = seq_idx >= split

    X_tr, y_tr = Xs[train_mask], ys[train_mask]
    X_te       = Xs[test_mask]

    if len(X_tr) < 8 or len(X_te) == 0:
        return None, None, float('nan')

    # ── Build DataLoader ──────────────────────────────────────
    X_tr_t = torch.from_numpy(X_tr)
    y_tr_t = torch.from_numpy(y_tr)

    # Hold out last 15 % of training data for validation (early stopping)
    val_size  = max(1, int(len(X_tr_t) * 0.15))
    X_val_t, y_val_t = X_tr_t[-val_size:], y_tr_t[-val_size:]
    X_tr_t,  y_tr_t  = X_tr_t[:-val_size],  y_tr_t[:-val_size]

    train_loader = DataLoader(
        TensorDataset(X_tr_t, y_tr_t),
        batch_size=8, shuffle=False,
    )

    # ── Instantiate model, loss, optimiser ───────────────────
    device = torch.device('cpu')          # Render is CPU-only
    model  = LSTMModel(N_FEAT).to(device)
    criterion = nn.MSELoss()
    optimiser = torch.optim.Adam(model.parameters())

    # ── Training loop with early stopping ────────────────────
    patience, best_val, wait = 15, float('inf'), 0
    best_state = None

    for epoch in range(200):
        model.train()
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            optimiser.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            optimiser.step()

        # Validation loss
        model.eval()
        with torch.no_grad():
            val_loss = criterion(
                model(X_val_t.to(device)),
                y_val_t.to(device),
            ).item()

        if val_loss < best_val:
            best_val   = val_loss
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
            wait       = 0
        else:
            wait += 1
            if wait >= patience:
                break

    # Restore best weights
    if best_state is not None:
        model.load_state_dict(best_state)

    # ── Inference ─────────────────────────────────────────────
    model.eval()
    with torch.no_grad():
        preds_scaled = model(
            torch.from_numpy(X_te).to(device)
        ).cpu().numpy()

    preds = scaler_y.inverse_transform(preds_scaled).flatten()

    yte   = df.loc[seq_idx[test_mask], target].values
    mask  = ~(np.isnan(preds) | np.isnan(yte))
    if mask.sum() == 0:
        return None, None, float('nan')

    rmse  = float(np.sqrt(mean_squared_error(yte[mask], preds[mask])))
    yte_s = df.loc[seq_idx[test_mask], target]
    return yte_s, preds, rmse


# ── RMSE helper ───────────────────────────────────────────────

def rmse(a, b) -> float:
    """Compute RMSE ignoring NaNs."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    m = ~(np.isnan(a) | np.isnan(b))
    return float(np.sqrt(np.mean((a[m] - b[m]) ** 2)))


# ── One-shot startup loader ───────────────────────────────────

def load_and_fit(csv_path: str = 'armenia_quarterly.csv') -> dict:
    """
    Load data and fit all models. Returns a dict of pre-computed globals
    for the Dash app to consume.
    """
    print("Loading data and fitting VAR (~15 s)…")
    data                                      = load_data(csv_path)
    fitted, var_data, exog, irf, granger_df   = fit_var(data)
    test, fc_var, resid_std                   = var_forecast(var_data, exog)
    y_xgb, preds_xgb, rmse_xgb               = xgb_forecast(var_data, exog)
    y_lstm, preds_lstm, rmse_lstm             = lstm_forecast(var_data, exog)

    rmse_var  = rmse(test['dlog_CPI_index'].values, fc_var['dlog_CPI_index'].values)
    rmse_xgb_ = rmse(test['dlog_CPI_index'].values, preds_xgb)

    print("Ready — open http://127.0.0.1:8050\n")

    return dict(
        DATA       = data,
        FITTED     = fitted,
        VAR_DATA   = var_data,
        EXOG       = exog,
        IRF        = irf,
        GRANGER_DF = granger_df,
        TEST       = test,
        FC_VAR     = fc_var,
        RESID_STD  = resid_std,
        Y_XGB      = y_xgb,
        PREDS_XGB  = preds_xgb,
        RMSE_XGB   = rmse_xgb_,
        Y_LSTM     = y_lstm,
        PREDS_LSTM = preds_lstm,
        RMSE_LSTM  = rmse_lstm,
        RMSE_VAR   = rmse_var,
        VAR_COLS   = var_data.columns.tolist(),
        NUMERIC    = ['CPI_index', 'M2', 'GOV_EXP', 'rate'],
        ELEC_Q     = data[data['ELECTION'] == 1].index,
    )
