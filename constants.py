"""
constants.py
============
Colour palette, shared style dicts, election metadata, variable labels,
and all bilingual translation strings used throughout the dashboard.
"""

# ── Colour palette ────────────────────────────────────────────
NAVY  = '#0f172a'
GOLD  = '#f59e0b'
BLUE  = '#2563eb'
GREEN = '#059669'
RED   = '#dc2626'
LGRAY = '#f8fafc'
DGRAY = '#64748b'
WHITE = '#ffffff'

# ── Shared style dicts ────────────────────────────────────────
CARD = {
    'background': WHITE,
    'borderRadius': '12px',
    'boxShadow': '0 2px 12px rgba(0,0,0,0.08)',
    'padding': '24px',
    'marginBottom': '20px',
}
INFO = {
    'background': '#eff6ff',
    'border': '1px solid #bfdbfe',
    'borderRadius': '8px',
    'padding': '14px 18px',
    'marginBottom': '18px',
    'color': '#1e3a8a',
    'fontSize': '14px',
    'lineHeight': '1.7',
}

# ── Election metadata ─────────────────────────────────────────
ELECTIONS = {
    2008: {'label': '2008', 'color': '#7c3aed'},
    2012: {'label': '2012', 'color': '#2563eb'},
    2017: {'label': '2017', 'color': '#0891b2'},
    2018: {'label': '2018', 'color': '#ea580c'},
    2021: {'label': '2021', 'color': '#059669'},
}
ELEC_STARTS = {
    2008: '2008-04-01',
    2012: '2012-04-01',
    2017: '2017-04-01',
    2018: '2018-12-09',
    2021: '2021-06-20',
}

# ── Variable labels (stationary / differenced names) ──────────
VAR_LABELS = {
    'dlog_CPI_index': 'Δlog(CPI)',
    'dlog_M2':        'Δlog(M2)',
    'dlog_GOV_EXP':   'Δlog(Gov Spending)',
    'd_rate':         'Δ Interest Rate',
}

# ── Human-readable descriptions for raw variables ─────────────
VAR_DESC = {
    'CPI_index': (
        "Consumer Price Index (Base 2003=100)",
        "Tracks the cost of everyday goods. Rising CPI = inflation. Computed as a "
        "cumulative index from monthly growth rates, rebased so Jan 2003 = 100.",
    ),
    'M2': (
        "M2 Money Supply (million AMD)",
        "All cash plus bank deposits. Governments can expand M2 by lowering rates. "
        "Pre-election M2 spikes are a classic political business cycle signal.",
    ),
    'GOV_EXP': (
        "Government Expenditure (million AMD)",
        "Total spending from Armenia's consolidated budget. The most direct tool "
        "politicians control — spending increases before elections are a textbook PBC signal.",
    ),
    'rate': (
        "CBA Reference Interest Rate (%)",
        "The Central Bank's policy rate. Lower rates stimulate borrowing and growth "
        "but risk inflation. Watch for rate cuts before elections.",
    ),
}

# ── Bilingual translations ────────────────────────────────────
T = {
    'en': {
        'subtitle':      'Do Elections Move the Economy? A Time Series Investigation.',
        'span_elec':     '4 Elections',
        'span_models':   'VAR · XGBoost · LSTM',
        'tab_home':      '🏠  About',
        'tab_data':      '📈  Data Explorer',
        'tab_elec':      '🗳️  Election Analysis',
        'tab_var':       '🔬  VAR Model',
        'tab_fc':        '🔮  Forecasting',
        'about_h':       'What is the Political Business Cycle?',
        'about_p1':      (
            'The Political Business Cycle (PBC) theory argues that governments '
            'manipulate economic policy around elections to boost their chances of '
            'winning. Before an election, politicians may raise spending, expand '
            'money supply, or cut rates — creating a short-term economic boost. '
            'After the election, corrections follow: higher inflation, tightening, cuts.'
        ),
        'about_p2':      (
            'This project asks: does Armenia show evidence of a PBC? We use quarterly '
            'data from 2008–2025, covering four elections, and apply VAR, XGBoost, '
            'and LSTM to test whether elections predict changes in inflation, '
            'money supply, and government spending.'
        ),
        'stat_q':        'Quarters of data',      'stat_q_s': '2008 Q1 – 2025 Q4',
        'stat_e':        'Elections analysed',    'stat_e_s': '2008, 2012, 2017, 2018, 2021',
        'stat_v':        'Macro variables',       'stat_v_s': 'CPI · M2 · Gov · Rate · Election',
        'stat_m':        'Models compared',       'stat_m_s': 'VAR · XGBoost · LSTM',
        'data_h':        'The Data — What Are We Looking At?',
        'data_sub':      'All variables measured quarterly (every 3 months)',
        'col_var':       'Variable', 'col_mean': 'What it means',
        'col_freq':      'Frequency', 'col_src': 'Source',
        'annual_note':   '* Annual gov. expenditure is linearly interpolated to quarterly.',
        'clean_h':       'How Was the Data Cleaned?',
        'clean_sub':     'Raw government data is messy — here is what we did',
        'c1h': 'Excel structure fix',
        'c1p': 'Armstat exports had year values buried in a data row, not the column header. We extracted them automatically.',
        'c2h': 'Date parsing',
        'c2p': 'Central Bank files stored dates as Python datetime objects — footnote rows were filtered, dates parsed directly.',
        'c3h': 'Quarterly aggregation',
        'c3p': 'Monthly CPI and M2 were averaged to quarterly. Annual gov spending was linearly interpolated. All series merged on a common quarterly index.',
        'elec_cov':      'Elections Covered',
        'data_select':   'Select variable',
        'about_var':     'About this variable: ',
        'elec_h':        'Election-Period Analysis',
        'elec_sub':      'Compare macro behaviour 4 quarters before, during, and after each election',
        'elec_info':     (
            "Election window = election quarter + quarter before. "
            "'Before' = 4 preceding quarters. 'After' = 4 following quarters. "
            "Look for spending surges and M2 expansion before elections, "
            "and inflation corrections afterward."
        ),
        'elec_yr':       'Select election year',
        'elec_vr':       'Select variable',
        'elec_comp_h':   'All Elections Side-by-Side — CPI',
        'elec_comp_sub': 'CPI indexed to 100 at election quarter. Do all elections look similar?',
        'period_b':      '4 quarters BEFORE',
        'period_d':      'ELECTION window',
        'period_a':      '4 quarters AFTER',
        'col_period':    'Period', 'col_ch': 'Change vs previous',
        'var_h':         'VAR Model Results',
        'var_sub':       'Vector Autoregression — the core econometric model',
        'var_what_h':    'What is a VAR model?',
        'var_what_p':    (
            'A VAR model treats several time series simultaneously. Instead of '
            'modelling CPI alone, VAR models CPI, M2, Gov Spending, and Interest Rate '
            'all at once — each variable depends on past values of all the others. '
            'This lets us ask: does a shock to government spending cause inflation to rise?'
        ),
        'box1h': 'Stationarity',
        'box1p': 'VAR requires stationary series. We take Δlog of CPI, M2, Gov Spending and first-difference of the rate.',
        'box2h': 'Lag selection',
        'box2p': 'We test lags 1–6 and pick the lag count minimising AIC — balancing fit vs complexity.',
        'box3h': 'Election dummy',
        'box3p': 'Binary variable (1 = election quarter or quarter before) included as exogenous regressor.',
        'irf_h':         'Impulse Response Function (IRF)',
        'irf_sub':       'How does a one-time shock ripple through the economy over 8 quarters?',
        'irf_info':      (
            'Bars above zero = positive response. A positive CPI response to Gov Spending '
            'means spending increases cause inflation — a key PBC signature.'
        ),
        'irf_imp':       'Impulse (shock)', 'irf_resp': 'Response',
        'granger_h':     'Granger Causality',
        'granger_sub':   'Does knowing past X help predict CPI better than CPI alone?',
        'granger_info':  (
            "Granger causality ≠ physical causation. It means X contains predictive "
            "information about CPI beyond CPI's own history. p < 0.05 supports the PBC "
            "hypothesis when it is gov spending or M2 driving inflation."
        ),
        'fc_h':          'Forecasting Models Comparison',
        'fc_sub':        'Train on 2008–2021, forecast 2022–2025, compare accuracy',
        'fc_what_h':     'What are we forecasting?',
        'fc_what_p':     (
            'We forecast Δlog(CPI) — the quarterly log change in price level, '
            'interpretable as quarterly inflation. All models train on 2008–2021 '
            'and forecast 2022–2025 without seeing that data.'
        ),
        'fc_line_h':     'Forecast vs Actual',
        'fc_line_sub':   'Shaded blue = 95% CI for VAR  (±1.96 × residual std dev)',
        'fc_bar_h':      'Model Accuracy',
        'fc_bar_sub':    'RMSE = Root Mean Squared Error. Lower is better.',
        'fc_verdict_p':  (
            'VAR is preferred for policy analysis regardless of raw accuracy — '
            'it explains WHY prices move via Granger causality and IRFs. '
            'XGBoost wins on pure prediction.'
        ),
        'wins':          'wins on RMSE',
        'best_rmse':     'Best RMSE: ',
        'actual':        'Actual',
        'lower_better':  'RMSE (lower is better)',
        'badge_econ':    'Econometric',
        'badge_ml':      'Machine Learning',
        'badge_dl':      'Deep Learning',
        'var_d':  'Uses all four macro variables. Interpretable coefficients and confidence intervals.',
        'xgb_d':  'Gradient-boosted trees with 4 lags per variable. Captures non-linear patterns.',
        'lstm_d': 'Neural network over 4-quarter sequences. May underperform with ~55 training obs.',
    },
    'hy': {
        'subtitle':      'Արդյո՞ք ընտրությունները շարժում են տնտեսությունը։ Ժամային շարքերի հետազոտություն։',
        'span_elec':     '4 ընտրություն',
        'span_models':   'VAR · XGBoost · LSTM',
        'tab_home':      '🏠  Մասին',
        'tab_data':      '📈  Տվյալներ',
        'tab_elec':      '🗳️  Ընտրություններ',
        'tab_var':       '🔬  VAR Մոդել',
        'tab_fc':        '🔮  Կանխատեսում',
        'about_h':       'Ի՞նչ է Քաղաքական Բիզնես Ցիկլը',
        'about_p1':      (
            'Քաղաքական Բիզնես Ցիկլի (ՔԲՑ) տեսությունն ասում է, որ կառավարությունները '
            'ընտրություններից առաջ շահարկում են տնտեսությունը հաղթելու համար։ '
            'Ավելացնում են ծախսերը, ընդլայնում դրամական մատակարարումը կամ '
            'իջեցնում տոկոսադրույքները՝ ստեղծելով կարճաժամկետ աճ։ '
            'Ընտրություններից հետո հետևում են ուղղումներ՝ գնաճ, խստացում, կրճատումներ։'
        ),
        'about_p2':      (
            'Այս նախագիծն ուսումնասիրում է՝ արդյո՞ք Հայաստանում ՔԲՑ-ի ապացույցներ կան։ '
            'Օգտագործել ենք 2008–2025թթ. եռամսյակային տվյալներ, ընդգրկելով 4 ընտրություն, '
            'և կիրառում ենք VAR, XGBoost, LSTM մոդելներ։'
        ),
        'stat_q':        'Եռամսյակ',             'stat_q_s': '2008 Ե1 – 2025 Ե4',
        'stat_e':        'Ուսումնասիրված ընտրություն', 'stat_e_s': '2008, 2012, 2017, 2018, 2021',
        'stat_v':        'Մակրո փոփոխական',      'stat_v_s': 'ՍԳԻ · M2 · Պետ.Ծախս · Դրույք · Ընտրություն',
        'stat_m':        'Համեմատված մոդել',      'stat_m_s': 'VAR · XGBoost · LSTM',
        'data_h':        'Տվյալները — ի՞նչ ենք ուսումնասիրում',
        'data_sub':      'Բոլոր փոփոխականները չափվում են եռամսյակային (3 ամիսը մեկ)',
        'col_var':       'Փոփոխական', 'col_mean': 'Ի՞նչ է նշանակում',
        'col_freq':      'Հաճախություն', 'col_src': 'Աղբյուր',
        'annual_note':   '* Տարեկան պետական ծախսերը ինտերպոլացվեցին եռամսյակային հաճախությամբ։',
        'clean_h':       'Ինչպե՞ս մաքրվեցին տվյալները',
        'clean_sub':     'Կառավարության հումք տվյալները անկանոն են',
        'c1h': 'Excel կառուցվածքի ուղղում',
        'c1p': 'Armstat-ի ֆայլերում տարեթվերը թաղված էին տվյալների տողում։ Ավտոմատ արդյունահանեցինք։',
        'c2h': 'Ամսաթվերի ճշգրտում',
        'c2p': 'ԿԲ ֆայլերն ամսաթվերը պահում էին datetime-ի տեսքով։ Ծանոթագրությունների տողերը զտեցինք։',
        'c3h': 'Եռամսյակային ամփոփում',
        'c3p': 'Ամսեկան ՍԳԻ-ն ու M2-ը միջինացվեցին։ Տարեկան ծախսերը ինտերպոլացվեցին։ Բոլոր շարքերը ձուլվեցին։',
        'elec_cov':      'Ընդգրկված ընտրություններ',
        'data_select':   'Ընտրեք փոփոխական',
        'about_var':     'Այս փոփոխականի մասին՝ ',
        'elec_h':        'Ընտրաշրջանի Վերլուծություն',
        'elec_sub':      'Համեմատեք վարքը ընտրությունից 4 եռամսյակ առաջ, ընթացքում և հետո',
        'elec_info':     (
            'Ընտրության պատուհան = ընտրության եռամսյակ + նախորդ եռամսյակ։ '
            '«Առաջ» = 4 նախորդ եռամսյակ։ «Հետո» = 4 հաջորդ եռամսյակ։ '
            'Փնտրեք ծախսերի աճ և M2-ի ընդլայնում ընտրություններից առաջ։'
        ),
        'elec_yr':       'Ընտրեք ընտրության տարեթիվ',
        'elec_vr':       'Ընտրեք փոփոխական',
        'elec_comp_h':   'Բոլոր ընտրությունները — ՍԳԻ',
        'elec_comp_sub': 'ՍԳԻ ինդեքսացված 100-ի վրա ընտրության եռամսյակում։',
        'period_b':      '4 եռամսյակ ԱՌԱՋ',
        'period_d':      'ԸՆՏՐՈՒԹՅԱՆ պատուհան',
        'period_a':      '4 եռամսյակ ՀԵՏՈ',
        'col_period':    'Ժամանակաշրջան', 'col_ch': 'Փոփոխություն',
        'var_h':         'VAR Մոդելի Արդյունքներ',
        'var_sub':       'Վեկտոր ավտոռեգրեսիա — հիմնական էկոնոմետրիկ մոդել',
        'var_what_h':    'Ի՞նչ է VAR մոդելը',
        'var_what_p':    (
            'VAR մոդելը միաժամանակ ուսումնասիրում է մի քանի ժամային շարքեր։ '
            'Փոխարենը ՍԳԻ-ն առանձին մոդելավորելու, VAR-ն ուսումնասիրում է ՍԳԻ, '
            'M2, Պետ. ծախսեր և Տոկոսադրույք — յուրաքանչյուրը կախված բոլոր '
            'մյուսների անցյալ արժեքներից։'
        ),
        'box1h': 'Ստացիոնարություն',
        'box1p': 'VAR-ը պահանջում է ստացիոնար շարքեր։ Վերցնում ենք Δlog(ՍԳԻ, M2, Ծախս) և Δ(Դրույք)։',
        'box2h': 'Լագի ընտրություն',
        'box2p': 'Ստուգում ենք 1–6 լագերը, ընտրում ենք AIC-ն նվազագույնի հասցնողը։',
        'box3h': 'Ընտրությունների dummy',
        'box3p': 'Երկուական փոփոխական (1 = ընտրության կամ նախորդ եռամսյակ)։',
        'irf_h':         'Ազդակի Արձագանք (IRF)',
        'irf_sub':       'Ինչպե՞ս է ցնցումն ալիք առաջացնում 8 եռամսյակի ընթացքում',
        'irf_info':      (
            'Զրոյից վեր ձողիկ = դրական արձագանք։ ՍԳԻ-ի դրական արձագանքը '
            'Պետ. ծախսերի ցնցմանը = ծախսերն առաջացնում են գնաճ — ՔԲՑ-ի հիմնական ազդանշան։'
        ),
        'irf_imp':       'Ազդակ (ցնցում)', 'irf_resp': 'Արձագանք',
        'granger_h':     'Գրեյնջերի պատճառականություն',
        'granger_sub':   'Արդյո՞ք X-ի անցյալն ավելի լավ կանխատեսում է ՍԳԻ-ն, քան ՍԳԻ-ի սեփական անցյալը',
        'granger_info':  (
            'Գրեյնջերի պատճառականությունը ֆիզիկական պատճառ չի նշանակում։ '
            'Նշանակում է X-ն ՍԳԻ-ի կանխատեսիչ տեղեկատվություն է պարունակում։ '
            'p < 0.05 աջակցում է ՔԲՑ-ի վարկածին, եթե պատճառը Պետ. ծախսն է կամ M2-ը։'
        ),
        'fc_h':          'Կանխատեսման Մոդելների Համեմատություն',
        'fc_sub':        'Ուսուցում 2008–2021, կանխատեսում 2022–2025',
        'fc_what_h':     'Ի՞նչ ենք կանխատեսում',
        'fc_what_p':     (
            'Կանխատեսում ենք Δlog(ՍԳԻ) — եռամսյակային գնաճի տեմպը։ '
            'Բոլոր մոդելները վարժեցվում են 2008–2021 թ. վրա, '
            'կանխատեսում են 2022–2025 թ.՝ առանց այդ տվյալները տեսնելու։'
        ),
        'fc_line_h':     'Կանխատեսում ընդդեմ փաստացիի',
        'fc_line_sub':   'Կապույտ ստվեր = VAR 95% վստահության միջակայք',
        'fc_bar_h':      'Մոդելների ճշգրտություն',
        'fc_bar_sub':    'RMSE = արմատային միջին քառ. սխալ։ Ցածր = ավելի լավ։',
        'fc_verdict_p':  (
            'VAR-ն ընտրելի է քաղաքականության վերլուծության համար — '
            'բացատրում է ԻՆՉՈՒ են գները փոխվում՝ Գրեյնջերի և IRF-ի միջոցով։'
        ),
        'wins':          'հաղթում է RMSE-ով',
        'best_rmse':     'Լավագույն RMSE՝ ',
        'actual':        'Փաստացի',
        'lower_better':  'RMSE (ցածր = ավելի լավ)',
        'badge_econ':    'Էկոնոմետրիկ',
        'badge_ml':      'Մ. Ուսուցում',
        'badge_dl':      'Խ. Ուսուցում',
        'var_d':  'Օգտ. չորս մակրո փոփոխականի կապերը։ Մեկնաբանելի գործակիցներ ու վստ. միջակայքներ։',
        'xgb_d':  'Գրադիենտ-ուժ. ծառ՝ 4 լաgrade փոփ.-ից։ Ոչ-գծային ձևեր։',
        'lstm_d': 'Նեյրոնային ցանց՝ 4-եռամսյ. հաջ.վ.։ Կարող է ավելի թույլ կատ. ~55 դիտ.–ով։',
    },
}
