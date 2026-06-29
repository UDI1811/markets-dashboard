import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import time

# ══════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="Markets Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════
# CSS STYLING
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    direction: rtl;
}

.main { background-color: #0a0e1a; }

[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #0d1220 0%, #0a0e1a 100%);
}

[data-testid="stHeader"] { background: transparent; }

.metric-card {
    background: #131929;
    border: 1px solid rgba(148,163,184,0.08);
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 4px;
    transition: background 0.2s;
    text-align: right;
}

.metric-card:hover { background: #1a2235; }

.card-name {
    font-size: 14px;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 2px;
}

.card-region {
    font-size: 11px;
    color: #475569;
    margin-bottom: 10px;
}

.card-price {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 22px;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 8px;
    direction: ltr;
    text-align: right;
}

.badges {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    justify-content: flex-end;
}

.badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    padding: 3px 8px;
    border-radius: 4px;
    direction: ltr;
}

.badge-label {
    font-size: 9px;
    font-family: 'Inter', sans-serif;
    margin-left: 3px;
    opacity: 0.7;
}

.pos { color: #10b981; background: rgba(16,185,129,0.12); }
.neg { color: #ef4444; background: rgba(239,68,68,0.12); }
.neu { color: #94a3b8; background: rgba(148,163,184,0.08); }

.section-header {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #475569;
    padding: 20px 0 10px 0;
    border-bottom: 1px solid rgba(148,163,184,0.08);
    margin-bottom: 12px;
    direction: rtl;
}

.top-bar {
    background: linear-gradient(180deg, #0d1220 0%, #0a0e1a 100%);
    border-bottom: 1px solid rgba(148,163,184,0.08);
    padding: 12px 0;
    margin-bottom: 20px;
    direction: rtl;
}

.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.25);
    border-radius: 20px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
    color: #10b981;
}

div[data-testid="metric-container"] {
    background: #131929;
    border: 1px solid rgba(148,163,184,0.08);
    border-radius: 10px;
    padding: 12px;
}

[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 11px !important; }
[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-family: 'IBM Plex Mono', monospace !important; }
[data-testid="stMetricDelta"] { font-family: 'IBM Plex Mono', monospace !important; }

.stTabs [data-baseweb="tab-list"] { gap: 4px; background: #131929; border-radius: 8px; padding: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 6px; color: #94a3b8; font-size: 12px; font-weight: 500; padding: 6px 14px; }
.stTabs [aria-selected="true"] { background: rgba(59,130,246,0.15) !important; color: #3b82f6 !important; }

[data-testid="stSelectbox"] label { color: #94a3b8; font-size: 12px; }
[data-testid="stMultiSelect"] label { color: #94a3b8; font-size: 12px; }

h1, h2, h3 { color: #f1f5f9 !important; direction: rtl; }

.disclaimer {
    font-size: 10px;
    color: #475569;
    border-top: 1px solid rgba(148,163,184,0.08);
    padding-top: 12px;
    margin-top: 20px;
    direction: rtl;
}

.stPlotlyChart { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# INDEX DEFINITIONS
# ══════════════════════════════════════════════
INDICES = {
    "🇮🇱 ישראל": [
        {"ticker": "TA35.TA",   "name": "תל אביב 35",    "region": "בורסה תל אביב"},
        {"ticker": "TA125.TA",  "name": "תל אביב 125",   "region": "בורסה תל אביב"},
        {"ticker": "TANEGS.TA", "name": "תל אביב נדל\"ן", "region": "בורסה תל אביב"},
    ],
    "🇺🇸 ארה\"ב": [
        {"ticker": "^GSPC", "name": "S&P 500",        "region": "ניו יורק"},
        {"ticker": "^DJI",  "name": "דאו ג'ונס 30",   "region": "ניו יורק"},
        {"ticker": "^NDX",  "name": "נאסד\"ק 100",     "region": "ניו יורק"},
        {"ticker": "^VIX",  "name": "VIX",             "region": "תנודתיות"},
        {"ticker": "TLT",   "name": "אג\"ח US 20Y",    "region": "אג\"ח"},
    ],
    "🇪🇺 אירופה": [
        {"ticker": "^GDAXI",    "name": "דאקס",          "region": "פרנקפורט"},
        {"ticker": "^FTSE",     "name": "פוטסי 100",     "region": "לונדון"},
        {"ticker": "^STOXX50E", "name": "יורוסטוקס 50",  "region": "אירופה"},
    ],
    "🌏 אסיה/פסיפיק": [
        {"ticker": "^HSI",  "name": "האנג סאנג",  "region": "הונג קונג"},
        {"ticker": "^AXJO", "name": "ASX 200",     "region": "אוסטרליה"},
        {"ticker": "^N225", "name": "ניקיי 225",   "region": "טוקיו"},
        {"ticker": "^NSEI", "name": "ניפטי 50",    "region": "מומביי"},
    ],
    "📊 אג\"ח וסחורות": [
        {"ticker": "^TNX",    "name": "תשואת US 10Y", "region": "אג\"ח"},
        {"ticker": "^TYX",    "name": "תשואת US 30Y", "region": "אג\"ח"},
        {"ticker": "GC=F",    "name": "זהב",          "region": "סחורות"},
        {"ticker": "CL=F",    "name": "נפט WTI",      "region": "סחורות"},
        {"ticker": "EURUSD=X","name": "EUR/USD",       "region": "מט\"ח"},
    ],
}

ALL_TICKERS = [(info["ticker"], info["name"], section)
               for section, items in INDICES.items()
               for info in items]

# ══════════════════════════════════════════════
# DATA FETCHING (cached 15 min)
# ══════════════════════════════════════════════
@st.cache_data(ttl=900)  # 15 minutes
def get_quote(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        hist = t.history(period="5d")
        if len(hist) < 2:
            return None
        price = float(hist["Close"].iloc[-1])
        prev  = float(hist["Close"].iloc[-2])
        open_ = float(hist["Open"].iloc[-1]) if not hist["Open"].empty else None
        high  = float(hist["High"].iloc[-1]) if not hist["High"].empty else None
        low   = float(hist["Low"].iloc[-1])  if not hist["Low"].empty  else None
        vol   = float(hist["Volume"].iloc[-1]) if not hist["Volume"].empty else None
        return {
            "price": price,
            "prev":  prev,
            "open":  open_,
            "high":  high,
            "low":   low,
            "volume": vol,
            "day_chg": (price - prev) / prev * 100 if prev else None,
        }
    except Exception:
        return None

@st.cache_data(ttl=900)
def get_history(ticker, period="1y"):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period)
        return hist["Close"].dropna()
    except Exception:
        return pd.Series(dtype=float)

@st.cache_data(ttl=900)
def get_annual_returns(ticker):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="10y")["Close"].dropna()
        hist.index = pd.to_datetime(hist.index)
        returns = {}
        for year in [2020, 2021, 2022, 2023, 2024]:
            yr_data = hist[hist.index.year == year]
            prev_yr = hist[hist.index.year == year - 1]
            if len(yr_data) > 0 and len(prev_yr) > 0:
                returns[str(year)] = (yr_data.iloc[-1] - prev_yr.iloc[-1]) / prev_yr.iloc[-1] * 100
        # YTD
        now = datetime.now()
        cur_yr = hist[hist.index.year == now.year]
        prev_yr = hist[hist.index.year == now.year - 1]
        if len(cur_yr) > 0 and len(prev_yr) > 0:
            returns["YTD"] = (cur_yr.iloc[-1] - prev_yr.iloc[-1]) / prev_yr.iloc[-1] * 100
        # MTD
        cur_mo = hist[(hist.index.year == now.year) & (hist.index.month == now.month)]
        if len(cur_mo) >= 2:
            returns["MTD"] = (cur_mo.iloc[-1] - cur_mo.iloc[0]) / cur_mo.iloc[0] * 100
        return returns
    except Exception:
        return {}

# ══════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════
def fmt_pct(v):
    if v is None: return "—"
    return f"+{v:.2f}%" if v >= 0 else f"{v:.2f}%"

def fmt_price(v):
    if v is None: return "—"
    if v > 1000: return f"{v:,.1f}"
    if v > 10:   return f"{v:,.2f}"
    return f"{v:.4f}"

def badge_cls(v):
    if v is None: return "neu"
    return "pos" if v >= 0 else "neg"

def arrow(v):
    if v is None: return ""
    return "▲" if v >= 0 else "▼"

CHART_COLORS = [
    "#3b82f6","#10b981","#f59e0b","#8b5cf6","#06b6d4",
    "#ef4444","#84cc16","#f97316","#ec4899","#14b8a6"
]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", family="Inter, sans-serif", size=11),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(
        gridcolor="rgba(148,163,184,0.06)",
        showline=False,
        tickfont=dict(size=10, color="#475569")
    ),
    yaxis=dict(
        gridcolor="rgba(148,163,184,0.06)",
        showline=False,
        tickfont=dict(size=10, color="#475569", family="IBM Plex Mono")
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", size=11)
    ),
    hovermode="x unified",
)

# ══════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════
now_str = datetime.now().strftime("%H:%M:%S")
col_logo, col_time, col_badge = st.columns([3, 2, 1])
with col_logo:
    st.markdown("# 📊 Markets Terminal")
    st.caption("דשבורד מדדים גלובלי — עיכוב עד 15 דקות")
with col_time:
    st.markdown(f"<br><span style='color:#475569;font-size:12px;font-family:monospace'>עדכון אחרון: {now_str}</span>", unsafe_allow_html=True)
with col_badge:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 רענן נתונים"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# ══════════════════════════════════════════════
# LOAD ALL QUOTES
# ══════════════════════════════════════════════
with st.spinner("טוען נתונים חיים..."):
    quotes = {}
    annual = {}
    for ticker, name, _ in ALL_TICKERS:
        quotes[ticker] = get_quote(ticker)
        annual[ticker] = get_annual_returns(ticker)

# ══════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs(["📈 מדדים חיים", "📅 תשואות שנתיות", "📊 גרפים", "🔀 השוואה"])

# ══════════════════════════════════════════════
# TAB 1 — LIVE INDICES
# ══════════════════════════════════════════════
with tab1:
    for section, items in INDICES.items():
        st.markdown(f"<div class='section-header'>{section}</div>", unsafe_allow_html=True)
        cols = st.columns(len(items))
        for col, info in zip(cols, items):
            ticker = info["ticker"]
            name   = info["name"]
            q = quotes.get(ticker) or {}
            price   = q.get("price")
            day_chg = q.get("day_chg")
            ar      = annual.get(ticker, {})
            ytd     = ar.get("YTD")
            mtd     = ar.get("MTD")
            with col:
                delta_str = fmt_pct(day_chg) if day_chg is not None else None
                st.metric(
                    label=f"{name} ({info['region']})",
                    value=fmt_price(price),
                    delta=delta_str
                )
                badges_html = f"""
                <div class='badges' style='margin-top:-8px'>
                  <span class='badge {badge_cls(mtd)}'><span class='badge-label'>MTD</span>{arrow(mtd)} {fmt_pct(mtd)}</span>
                  <span class='badge {badge_cls(ytd)}'><span class='badge-label'>YTD</span>{arrow(ytd)} {fmt_pct(ytd)}</span>
                </div>"""
                st.markdown(badges_html, unsafe_allow_html=True)
                st.markdown("")

# ══════════════════════════════════════════════
# TAB 2 — ANNUAL RETURNS TABLE
# ══════════════════════════════════════════════
with tab2:
    st.markdown("### תשואות שנתיות 2020 – YTD")
    years_cols = ["2020", "2021", "2022", "2023", "2024", "YTD", "MTD"]
    rows = []
    for ticker, name, section in ALL_TICKERS:
        ar = annual.get(ticker, {})
        row = {"מדד": name, "קטגוריה": section.split(" ", 1)[-1]}
        for y in years_cols:
            v = ar.get(y)
            row[y] = round(v, 2) if v is not None else None
        rows.append(row)

    df = pd.DataFrame(rows)

    def color_cell(val):
        if pd.isna(val) or val is None: return "color: #475569"
        return "color: #10b981; font-weight:500" if val >= 0 else "color: #ef4444; font-weight:500"

    styled = (
        df.style
        .applymap(color_cell, subset=years_cols)
        .format({y: lambda v: fmt_pct(v) if v is not None else "—" for y in years_cols})
        .set_properties(**{"text-align": "center", "font-family": "IBM Plex Mono"})
        .set_properties(subset=["מדד", "קטגוריה"], **{"text-align": "right"})
    )
    st.dataframe(styled, use_container_width=True, height=600)

# ══════════════════════════════════════════════
# TAB 3 — CHARTS
# ══════════════════════════════════════════════
with tab3:
    ticker_options = {f"{name} ({ticker})": ticker for ticker, name, _ in ALL_TICKERS}
    col_sel, col_per = st.columns([2, 1])
    with col_sel:
        sel_label = st.selectbox("בחר מדד", list(ticker_options.keys()), index=0)
    with col_per:
        period_map = {"חודש": "1mo", "3 חודשים": "3mo", "6 חודשים": "6mo", "שנה": "1y", "5 שנים": "5y"}
        sel_period_label = st.selectbox("תקופה", list(period_map.keys()), index=3)

    sel_ticker = ticker_options[sel_label]
    sel_period = period_map[sel_period_label]
    hist = get_history(sel_ticker, sel_period)

    if not hist.empty:
        # Normalize to % from start
        first = hist.iloc[0]
        normalized = ((hist - first) / first * 100)
        color_line = "#10b981" if normalized.iloc[-1] >= 0 else "#ef4444"

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=normalized,
            mode="lines",
            name=sel_label,
            line=dict(color=color_line, width=2),
            fill="tozeroy",
            fillcolor=f"rgba({'16,185,129' if normalized.iloc[-1] >= 0 else '239,68,68'},0.08)",
            hovertemplate="%{x|%d/%m/%Y}<br>%{y:+.2f}%<extra></extra>"
        ))
        fig.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(text=f"{sel_label} — ביצועים (%)", font=dict(color="#f1f5f9", size=13)),
            yaxis=dict(**PLOTLY_LAYOUT["yaxis"], tickformat="+.1f", ticksuffix="%"),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

        # Bar chart annual returns
        ar = annual.get(sel_ticker, {})
        years_bar = ["2020", "2021", "2022", "2023", "2024", "YTD", "MTD"]
        vals = [ar.get(y) for y in years_bar]
        colors_bar = ["#10b981" if (v or 0) >= 0 else "#ef4444" for v in vals]

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=years_bar,
            y=vals,
            marker_color=colors_bar,
            marker_line_width=0,
            text=[fmt_pct(v) for v in vals],
            textposition="outside",
            textfont=dict(size=10, color="#94a3b8"),
            hovertemplate="%{x}: %{y:+.2f}%<extra></extra>"
        ))
        fig2.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(text="תשואות שנתיות", font=dict(color="#f1f5f9", size=13)),
            yaxis=dict(**PLOTLY_LAYOUT["yaxis"], tickformat="+.1f", ticksuffix="%"),
            height=300,
            bargap=0.3
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("לא ניתן לטעון נתונים היסטוריים למדד זה")

# ══════════════════════════════════════════════
# TAB 4 — COMPARISON
# ══════════════════════════════════════════════
with tab4:
    st.markdown("### השוואת מדדים — ביצועים מנורמלים")
    name_to_ticker = {name: ticker for ticker, name, _ in ALL_TICKERS}
    default_names = ["S&P 500", "נאסד\"ק 100", "תל אביב 35", "דאקס"]
    default_valid = [n for n in default_names if n in name_to_ticker]

    col_comp, col_percomp = st.columns([3, 1])
    with col_comp:
        selected_names = st.multiselect(
            "בחר מדדים להשוואה",
            list(name_to_ticker.keys()),
            default=default_valid
        )
    with col_percomp:
        period_map2 = {"3 חודשים": "3mo", "6 חודשים": "6mo", "שנה": "1y", "3 שנים": "3y", "5 שנים": "5y"}
        comp_period_label = st.selectbox("תקופה ", list(period_map2.keys()), index=2)

    comp_period = period_map2[comp_period_label]

    if selected_names:
        fig3 = go.Figure()
        for i, name in enumerate(selected_names):
            ticker = name_to_ticker[name]
            hist = get_history(ticker, comp_period)
            if hist.empty: continue
            first = hist.iloc[0]
            normalized = ((hist - first) / first * 100)
            fig3.add_trace(go.Scatter(
                x=hist.index,
                y=normalized,
                mode="lines",
                name=name,
                line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=2),
                hovertemplate=f"{name}: %{{y:+.2f}}%<extra></extra>"
            ))

        fig3.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(text="השוואת ביצועים — מנורמל ל-100 מתחילת תקופה", font=dict(color="#f1f5f9", size=13)),
            yaxis=dict(**PLOTLY_LAYOUT["yaxis"], tickformat="+.1f", ticksuffix="%"),
            height=450,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig3, use_container_width=True)

        # Summary table
        st.markdown("#### סיכום תשואות")
        summary_rows = []
        for name in selected_names:
            ticker = name_to_ticker[name]
            hist = get_history(ticker, comp_period)
            ar = annual.get(ticker, {})
            if hist.empty: continue
            total_ret = (hist.iloc[-1] - hist.iloc[0]) / hist.iloc[0] * 100
            q = quotes.get(ticker) or {}
            summary_rows.append({
                "מדד": name,
                "תשואה בתקופה": round(total_ret, 2),
                "יומי": round(q.get("day_chg") or 0, 2),
                "MTD": round(ar.get("MTD") or 0, 2),
                "YTD": round(ar.get("YTD") or 0, 2),
            })

        df_sum = pd.DataFrame(summary_rows)
        styled_sum = (
            df_sum.style
            .applymap(color_cell, subset=["תשואה בתקופה", "יומי", "MTD", "YTD"])
            .format({c: lambda v: fmt_pct(v) for c in ["תשואה בתקופה", "יומי", "MTD", "YTD"]})
            .set_properties(**{"text-align": "center"})
            .set_properties(subset=["מדד"], **{"text-align": "right"})
        )
        st.dataframe(styled_sum, use_container_width=True)

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
