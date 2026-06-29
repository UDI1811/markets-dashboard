import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Markets Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #0d1220 0%, #0a0e1a 100%);
}
[data-testid="stHeader"] { background: transparent; }

div[data-testid="metric-container"] {
    background: #131929;
    border: 1px solid rgba(148,163,184,0.1);
    border-radius: 10px;
    padding: 14px;
}
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 11px !important; }
[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 18px !important; }
[data-testid="stMetricDelta"] { font-family: 'IBM Plex Mono', monospace !important; font-size: 12px !important; }

.stTabs [data-baseweb="tab-list"] { gap: 4px; background: #131929; border-radius: 8px; padding: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 6px; color: #94a3b8; font-size: 12px; font-weight: 500; padding: 6px 14px; }
.stTabs [aria-selected="true"] { background: rgba(59,130,246,0.15) !important; color: #3b82f6 !important; }

h1, h2, h3 { color: #f1f5f9 !important; }
p, label { color: #94a3b8 !important; }

.section-title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #475569;
    border-bottom: 1px solid rgba(148,163,184,0.08);
    padding-bottom: 8px;
    margin: 20px 0 12px 0;
    direction: rtl;
    text-align: right;
}

.badge-row {
    display: flex;
    gap: 5px;
    margin-top: -6px;
    margin-bottom: 8px;
    flex-wrap: wrap;
    justify-content: flex-end;
}
.badge {
    font-size: 10px;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 4px;
    font-family: monospace;
}
.pos { color: #10b981; background: rgba(16,185,129,0.12); }
.neg { color: #ef4444; background: rgba(239,68,68,0.12); }
.neu { color: #94a3b8; background: rgba(148,163,184,0.08); }

.ret-pos { color: #10b981; font-weight: 600; }
.ret-neg { color: #ef4444; font-weight: 600; }
.ret-neu { color: #475569; }

.disclaimer {
    font-size: 10px;
    color: #334155;
    border-top: 1px solid rgba(148,163,184,0.06);
    padding-top: 12px;
    margin-top: 24px;
    text-align: right;
    direction: rtl;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# INDICES
# ══════════════════════════════════════════════
INDICES = {
    "🇮🇱 ישראל": [
        {"ticker": "TA35.TA",   "name": "תל אביב 35",     "region": "בורסה תל אביב"},
        {"ticker": "TA125.TA",  "name": "תל אביב 125",    "region": "בורסה תל אביב"},
        {"ticker": "TANEGS.TA", "name": "תל אביב נדל\"ן",  "region": "בורסה תל אביב"},
    ],
    "🇺🇸 ארה\"ב": [
        {"ticker": "^GSPC", "name": "S&P 500",       "region": "ניו יורק"},
        {"ticker": "^DJI",  "name": "דאו ג'ונס 30",  "region": "ניו יורק"},
        {"ticker": "^NDX",  "name": "נאסד\"ק 100",    "region": "ניו יורק"},
        {"ticker": "^VIX",  "name": "VIX",            "region": "תנודתיות"},
        {"ticker": "TLT",   "name": "אג\"ח US 20Y",   "region": "אג\"ח"},
    ],
    "🇪🇺 אירופה": [
        {"ticker": "^GDAXI",    "name": "דאקס",         "region": "פרנקפורט"},
        {"ticker": "^FTSE",     "name": "פוטסי 100",    "region": "לונדון"},
        {"ticker": "^STOXX50E", "name": "יורוסטוקס 50", "region": "אירופה"},
    ],
    "🌏 אסיה/פסיפיק": [
        {"ticker": "^HSI",  "name": "האנג סאנג", "region": "הונג קונג"},
        {"ticker": "^AXJO", "name": "ASX 200",    "region": "אוסטרליה"},
        {"ticker": "^N225", "name": "ניקיי 225",  "region": "טוקיו"},
        {"ticker": "^NSEI", "name": "ניפטי 50",   "region": "מומביי"},
    ],
    "📊 אג\"ח וסחורות": [
        {"ticker": "^TNX",     "name": "תשואת US 10Y", "region": "אג\"ח"},
        {"ticker": "^TYX",     "name": "תשואת US 30Y", "region": "אג\"ח"},
        {"ticker": "GC=F",     "name": "זהב",          "region": "סחורות"},
        {"ticker": "CL=F",     "name": "נפט WTI",      "region": "סחורות"},
        {"ticker": "EURUSD=X", "name": "EUR/USD",       "region": "מט\"ח"},
    ],
}

ALL_TICKERS = [(info["ticker"], info["name"], section)
               for section, items in INDICES.items()
               for info in items]

# ══════════════════════════════════════════════
# DATA FETCHING
# ══════════════════════════════════════════════
@st.cache_data(ttl=900)
def get_quote(ticker):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="5d", auto_adjust=True)
        if len(hist) < 2:
            hist = t.history(period="1mo", auto_adjust=True)
        if len(hist) < 2:
            return None
        price = float(hist["Close"].iloc[-1])
        prev  = float(hist["Close"].iloc[-2])
        return {
            "price":   price,
            "prev":    prev,
            "day_chg": (price - prev) / prev * 100 if prev else None,
        }
    except Exception:
        return None

@st.cache_data(ttl=900)
def get_history(ticker, period="1y"):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period, auto_adjust=True)
        return hist["Close"].dropna()
    except Exception:
        return pd.Series(dtype=float)

@st.cache_data(ttl=900)
def get_annual_returns(ticker):
    """Calculate annual returns using daily history resampled to yearly."""
    try:
        t = yf.Ticker(ticker)
        # Pull max history available
        hist = t.history(period="max", auto_adjust=True)["Close"].dropna()
        if hist.empty:
            return {}
        hist.index = hist.index.tz_localize(None) if hist.index.tz else hist.index
        hist.index = pd.to_datetime(hist.index)

        returns = {}
        now = datetime.now()

        # Annual returns 2019-2024 (need year-end prices)
        for year in [2020, 2021, 2022, 2023, 2024]:
            # Get last trading day of year and year before
            yr   = hist[hist.index.year == year]
            prev = hist[hist.index.year == year - 1]
            if len(yr) > 0 and len(prev) > 0:
                end_price   = yr.iloc[-1]
                start_price = prev.iloc[-1]
                if start_price > 0:
                    returns[str(year)] = (end_price - start_price) / start_price * 100

        # YTD: from last day of previous year to today
        cur_yr  = hist[hist.index.year == now.year]
        prev_yr = hist[hist.index.year == now.year - 1]
        if len(cur_yr) > 0 and len(prev_yr) > 0 and prev_yr.iloc[-1] > 0:
            returns["YTD"] = (cur_yr.iloc[-1] - prev_yr.iloc[-1]) / prev_yr.iloc[-1] * 100

        # MTD: from last day of previous month to today
        cur_mo  = hist[(hist.index.year == now.year) & (hist.index.month == now.month)]
        prev_mo_end = hist[(hist.index.year == now.year) & (hist.index.month == now.month - 1)] if now.month > 1 else hist[hist.index.year == now.year - 1]
        if len(cur_mo) > 0 and len(prev_mo_end) > 0 and prev_mo_end.iloc[-1] > 0:
            returns["MTD"] = (cur_mo.iloc[-1] - prev_mo_end.iloc[-1]) / prev_mo_end.iloc[-1] * 100

        # Daily (already in quotes, but add here too)
        if len(hist) >= 2:
            returns["יומי"] = (hist.iloc[-1] - hist.iloc[-2]) / hist.iloc[-2] * 100

        return returns
    except Exception as e:
        return {}

# ══════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════
def fmt_pct(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return f"+{v:.2f}%" if v >= 0 else f"{v:.2f}%"

def fmt_price(v):
    if v is None: return "—"
    if v > 1000:  return f"{v:,.1f}"
    if v > 10:    return f"{v:,.2f}"
    return f"{v:.4f}"

def badge_cls(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return "neu"
    return "pos" if v >= 0 else "neg"

def color_val(v):
    if v is None or (isinstance(v, float) and pd.isna(v)): return "ret-neu"
    return "ret-pos" if v >= 0 else "ret-neg"

COLORS = ["#3b82f6","#10b981","#f59e0b","#8b5cf6","#06b6d4","#ef4444","#84cc16","#f97316","#ec4899","#14b8a6"]

PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", family="Inter, sans-serif", size=11),
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(gridcolor="rgba(148,163,184,0.06)", showline=False, tickfont=dict(size=10, color="#475569")),
    yaxis=dict(gridcolor="rgba(148,163,184,0.06)", showline=False, tickfont=dict(size=10, color="#475569")),
    hovermode="x unified",
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", size=11)),
)

# ══════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════
c1, c2, c3 = st.columns([4, 3, 1])
with c1:
    st.markdown("## 📊 Markets Terminal")
    st.caption("דשבורד מדדים גלובלי — נתונים בעיכוב עד 15 דקות | מקור: Yahoo Finance")
with c2:
    st.markdown(f"<br><span style='color:#475569;font-size:11px;font-family:monospace'>⏱ עדכון אחרון: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</span>", unsafe_allow_html=True)
with c3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 רענן"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# ══════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════
with st.spinner("טוען נתונים מ-Yahoo Finance..."):
    quotes = {}
    annual = {}
    for ticker, name, _ in ALL_TICKERS:
        quotes[ticker] = get_quote(ticker)
        annual[ticker] = get_annual_returns(ticker)

# ══════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs(["📈 מדדים חיים", "📅 תשואות שנתיות", "📊 גרפים", "🔀 השוואה"])

# ──────────────────────────────────────────────
# TAB 1 — LIVE
# ──────────────────────────────────────────────
with tab1:
    for section, items in INDICES.items():
        st.markdown(f"<div class='section-title'>{section}</div>", unsafe_allow_html=True)
        cols = st.columns(len(items))
        for col, info in zip(cols, items):
            ticker  = info["ticker"]
            q  = quotes.get(ticker) or {}
            ar = annual.get(ticker) or {}
            price   = q.get("price")
            day_chg = ar.get("יומי") or q.get("day_chg")
            ytd     = ar.get("YTD")
            mtd     = ar.get("MTD")
            with col:
                st.metric(
                    label=f"{info['name']}",
                    value=fmt_price(price),
                    delta=fmt_pct(day_chg) if day_chg is not None else None
                )
                st.markdown(f"""
                <div class='badge-row'>
                  <span class='badge neu'>יומי</span>
                  <span class='badge {badge_cls(day_chg)}'>{fmt_pct(day_chg)}</span>
                  <span class='badge neu'>MTD</span>
                  <span class='badge {badge_cls(mtd)}'>{fmt_pct(mtd)}</span>
                  <span class='badge neu'>YTD</span>
                  <span class='badge {badge_cls(ytd)}'>{fmt_pct(ytd)}</span>
                </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# TAB 2 — ANNUAL RETURNS TABLE
# ──────────────────────────────────────────────
with tab2:
    st.markdown("### תשואות שנתיות 2020–YTD")
    YEARS = ["2020", "2021", "2022", "2023", "2024", "YTD", "MTD", "יומי"]
    rows = []
    for ticker, name, section in ALL_TICKERS:
        ar = annual.get(ticker) or {}
        row = {"מדד": name, "קטגוריה": section.split(" ", 1)[-1]}
        for y in YEARS:
            v = ar.get(y)
            row[y] = round(v, 2) if v is not None else None
        rows.append(row)

    df = pd.DataFrame(rows)

    def style_pct(val):
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return "color: #334155"
        return "color: #10b981; font-weight:600" if val >= 0 else "color: #ef4444; font-weight:600"

    styled = (
        df.style
        .applymap(style_pct, subset=YEARS)
        .format({y: (lambda v: fmt_pct(v) if v is not None and not (isinstance(v, float) and pd.isna(v)) else "—") for y in YEARS})
        .set_properties(**{"text-align": "center", "font-family": "IBM Plex Mono, monospace", "font-size": "12px"})
        .set_properties(subset=["מדד", "קטגוריה"], **{"text-align": "right", "font-family": "Inter, sans-serif"})
        .set_table_styles([
            {"selector": "thead th", "props": [("background", "#0d1220"), ("color", "#475569"), ("font-size", "10px"), ("text-align", "center")]},
            {"selector": "tbody tr:hover", "props": [("background", "#1a2235")]},
            {"selector": "tbody td", "props": [("border-color", "rgba(148,163,184,0.06)")]},
        ])
    )
    st.dataframe(styled, use_container_width=True, height=620)

# ──────────────────────────────────────────────
# TAB 3 — CHARTS
# ──────────────────────────────────────────────
with tab3:
    ticker_opts = {f"{name}  ({ticker})": ticker for ticker, name, _ in ALL_TICKERS}
    c1, c2 = st.columns([2, 1])
    with c1:
        sel_label = st.selectbox("בחר מדד לתצוגה", list(ticker_opts.keys()))
    with c2:
        period_opts = {"חודש אחד": "1mo", "3 חודשים": "3mo", "6 חודשים": "6mo", "שנה": "1y", "3 שנים": "3y", "5 שנים": "5y"}
        sel_period_label = st.selectbox("תקופה", list(period_opts.keys()), index=3)

    sel_ticker = ticker_opts[sel_label]
    sel_period = period_opts[sel_period_label]
    hist = get_history(sel_ticker, sel_period)

    if not hist.empty:
        first = hist.iloc[0]
        norm  = (hist - first) / first * 100
        is_pos = norm.iloc[-1] >= 0
        line_color = "#10b981" if is_pos else "#ef4444"
        fill_color = "rgba(16,185,129,0.07)" if is_pos else "rgba(239,68,68,0.07)"

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist.index, y=norm,
            mode="lines", name=sel_label,
            line=dict(color=line_color, width=2),
            fill="tozeroy", fillcolor=fill_color,
            hovertemplate="%{x|%d/%m/%Y}  %{y:+.2f}%<extra></extra>"
        ))
        fig.update_layout(
            **PLOTLY_BASE,
            title=dict(text=f"ביצועים — {sel_label}", font=dict(color="#f1f5f9", size=13)),
            yaxis=dict(**PLOTLY_BASE["yaxis"], tickformat="+.1f", ticksuffix="%"),
            height=360
        )
        st.plotly_chart(fig, use_container_width=True)

        # Annual bar chart
        ar = annual.get(sel_ticker) or {}
        yr_labels = ["2020","2021","2022","2023","2024","YTD","MTD"]
        yr_vals   = [ar.get(y) for y in yr_labels]
        bar_colors = ["#10b981" if (v or 0) >= 0 else "#ef4444" for v in yr_vals]

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=yr_labels, y=yr_vals,
            marker_color=bar_colors, marker_line_width=0,
            text=[fmt_pct(v) for v in yr_vals],
            textposition="outside",
            textfont=dict(size=10, color="#94a3b8"),
            hovertemplate="%{x}: %{y:+.2f}%<extra></extra>"
        ))
        fig2.update_layout(
            **PLOTLY_BASE,
            title=dict(text="תשואות שנתיות", font=dict(color="#f1f5f9", size=13)),
            yaxis=dict(**PLOTLY_BASE["yaxis"], tickformat="+.1f", ticksuffix="%"),
            height=300, bargap=0.35
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("לא ניתן לטעון נתונים עבור מדד זה כרגע")

# ──────────────────────────────────────────────
# TAB 4 — COMPARISON
# ──────────────────────────────────────────────
with tab4:
    st.markdown("### השוואת מדדים — ביצועים מנורמלים")
    name_to_ticker = {name: ticker for ticker, name, _ in ALL_TICKERS}
    defaults = ["S&P 500", "נאסד\"ק 100", "תל אביב 35", "דאקס"]
    valid_defaults = [n for n in defaults if n in name_to_ticker]

    c1, c2 = st.columns([3, 1])
    with c1:
        sel_names = st.multiselect("בחר מדדים", list(name_to_ticker.keys()), default=valid_defaults)
    with c2:
        comp_opts = {"3 חודשים": "3mo", "6 חודשים": "6mo", "שנה": "1y", "3 שנים": "3y", "5 שנים": "5y"}
        comp_period = comp_opts[st.selectbox("תקופה ", list(comp_opts.keys()), index=2)]

    if sel_names:
        fig3 = go.Figure()
        summary = []
        for i, name in enumerate(sel_names):
            ticker = name_to_ticker[name]
            h = get_history(ticker, comp_period)
            if h.empty: continue
            norm = (h - h.iloc[0]) / h.iloc[0] * 100
            fig3.add_trace(go.Scatter(
                x=h.index, y=norm,
                mode="lines", name=name,
                line=dict(color=COLORS[i % len(COLORS)], width=2),
                hovertemplate=f"{name}: %{{y:+.2f}}%<extra></extra>"
            ))
            ar = annual.get(ticker) or {}
            q  = quotes.get(ticker) or {}
            summary.append({
                "מדד": name,
                "תשואה בתקופה": round((h.iloc[-1]-h.iloc[0])/h.iloc[0]*100, 2),
                "יומי": round(ar.get("יומי") or q.get("day_chg") or 0, 2),
                "MTD":  round(ar.get("MTD") or 0, 2),
                "YTD":  round(ar.get("YTD") or 0, 2),
            })

        fig3.update_layout(
            **PLOTLY_BASE,
            title=dict(text="השוואת ביצועים — מנורמל מתחילת תקופה", font=dict(color="#f1f5f9", size=13)),
            yaxis=dict(**PLOTLY_BASE["yaxis"], tickformat="+.1f", ticksuffix="%"),
            height=420,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig3, use_container_width=True)

        if summary:
            st.markdown("#### סיכום")
            df_s = pd.DataFrame(summary)
            num_cols = ["תשואה בתקופה","יומי","MTD","YTD"]
            styled_s = (
                df_s.style
                .applymap(style_pct, subset=num_cols)
                .format({c: fmt_pct for c in num_cols})
                .set_properties(**{"text-align":"center","font-family":"IBM Plex Mono, monospace","font-size":"12px"})
                .set_properties(subset=["מדד"], **{"text-align":"right","font-family":"Inter, sans-serif"})
            )
            st.dataframe(styled_s, use_container_width=True)

# ══════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════
st.markdown("""
<div class='disclaimer'>
* הנתונים מוצגים לצורכי מידע בלבד ואינם מהווים המלצת השקעה.
נתוני המדדים מתעדכנים בעיכוב של עד 15 דקות. מקור: Yahoo Finance.
תשואות עבר אינן ערובה לתשואות עתידיות.
</div>
""", unsafe_allow_html=True)
