import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Markets Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@300;400;500&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
[data-testid="stAppViewContainer"]{background:#0f1117;}
[data-testid="stHeader"]{display:none!important;}
[data-testid="stToolbar"]{display:none!important;}
.block-container{padding:0!important;max-width:100%!important;}

.hdr{background:linear-gradient(90deg,#0a0a14,#111128);border-bottom:1px solid rgba(255,255,255,0.06);padding:16px 32px;display:flex;align-items:center;justify-content:space-between;}
.hdr-title{font-family:'Inter',sans-serif;font-size:18px;font-weight:700;color:#fff;letter-spacing:0.02em;}
.hdr-sub{font-family:'Inter',sans-serif;font-size:11px;color:rgba(255,255,255,0.3);margin-top:3px;letter-spacing:0.04em;}
.hdr-right{display:flex;align-items:center;gap:16px;}
.live-pill{display:flex;align-items:center;gap:6px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.2);border-radius:20px;padding:5px 12px;font-family:'IBM Plex Mono',monospace;font-size:10px;color:#10b981;letter-spacing:0.06em;}
.live-dot{width:6px;height:6px;border-radius:50%;background:#10b981;animation:pulse 2s infinite;}
@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 6px rgba(16,185,129,0.6);}50%{opacity:0.4;box-shadow:none;}}
.ts{font-family:'IBM Plex Mono',monospace;font-size:11px;color:rgba(255,255,255,0.2);}

.tape-wrap{background:#080810;border-bottom:1px solid rgba(255,255,255,0.04);height:34px;overflow:hidden;display:flex;align-items:center;}
.tape-inner{display:flex;animation:scroll 70s linear infinite;white-space:nowrap;}
.tape-wrap:hover .tape-inner{animation-play-state:paused;}
@keyframes scroll{0%{transform:translateX(0);}100%{transform:translateX(-50%)}}
.ti{display:inline-flex;align-items:center;gap:7px;padding:0 20px;border-right:1px solid rgba(255,255,255,0.04);font-family:'IBM Plex Mono',monospace;font-size:11px;}
.tn{color:rgba(255,255,255,0.3);letter-spacing:0.04em;}
.tp{color:rgba(255,255,255,0.7);font-weight:500;}
.tpos{color:#10b981;font-size:10px;}
.tneg{color:#f43f5e;font-size:10px;}

.wrap{padding:20px 28px 40px;}

.kpi-row{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:1px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.05);border-radius:4px;overflow:hidden;margin-bottom:20px;}
.kpi{background:#13131f;padding:14px 16px;}
.kpi-lbl{font-family:'Inter',sans-serif;font-size:9px;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.25);margin-bottom:6px;}
.kpi-val{font-family:'IBM Plex Mono',monospace;font-size:20px;font-weight:400;color:rgba(255,255,255,0.9);margin-bottom:5px;direction:ltr;text-align:left;}
.kpi-chg{display:inline-flex;align-items:center;gap:3px;font-family:'IBM Plex Mono',monospace;font-size:11px;padding:2px 7px;border-radius:2px;}
.kpi-chg.pos{color:#10b981;background:rgba(16,185,129,0.1);}
.kpi-chg.neg{color:#f43f5e;background:rgba(244,63,94,0.1);}
.kpi-chg.neu{color:rgba(255,255,255,0.3);background:rgba(255,255,255,0.05);}
.kpi-sub{font-family:'Inter',sans-serif;font-size:9px;color:rgba(255,255,255,0.2);margin-top:4px;}

.panel{background:#13131f;border:1px solid rgba(255,255,255,0.05);border-radius:4px;padding:18px;position:relative;overflow:hidden;}
.panel::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#3b82f6,transparent);}
.panel-title{font-family:'Inter',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.35);margin-bottom:14px;}

.sec-bar{display:flex;align-items:center;gap:12px;margin:20px 0 12px;}
.sec-line{flex:1;height:1px;background:rgba(255,255,255,0.05);}
.sec-lbl{font-family:'Inter',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:rgba(255,255,255,0.2);white-space:nowrap;}

.tbl{width:100%;border-collapse:collapse;font-size:11px;}
.tbl thead th{background:#0c0c18;padding:8px 12px;text-align:center;font-family:'IBM Plex Mono',monospace;font-size:9px;font-weight:400;letter-spacing:0.1em;text-transform:uppercase;color:rgba(255,255,255,0.2);border-bottom:1px solid rgba(255,255,255,0.05);}
.tbl thead th:first-child{text-align:left;padding-left:16px;}
.tbl tbody tr{border-bottom:1px solid rgba(255,255,255,0.03);transition:background 0.15s;}
.tbl tbody tr:hover{background:rgba(255,255,255,0.02);}
.tbl tbody tr:last-child{border-bottom:none;}
.tbl td{padding:9px 12px;text-align:center;font-family:'IBM Plex Mono',monospace;font-size:11px;color:rgba(255,255,255,0.55);direction:ltr;}
.tbl td:first-child{text-align:left;padding-left:16px;font-family:'Inter',sans-serif;font-weight:500;color:rgba(255,255,255,0.75);}
.vpos{color:#10b981;font-weight:500;}
.vneg{color:#f43f5e;font-weight:500;}
.vneu{color:rgba(255,255,255,0.2);}

.badge{display:inline-block;padding:2px 7px;border-radius:2px;font-size:10px;font-family:'IBM Plex Mono',monospace;}
.bpos{color:#10b981;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.15);}
.bneg{color:#f43f5e;background:rgba(244,63,94,0.1);border:1px solid rgba(244,63,94,0.15);}
.bneu{color:rgba(255,255,255,0.3);background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);}

.stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid rgba(255,255,255,0.06)!important;gap:0!important;padding:0 28px!important;}
.stTabs [data-baseweb="tab"]{font-family:'Inter',sans-serif!important;font-size:11px!important;font-weight:600!important;letter-spacing:0.1em!important;text-transform:uppercase!important;color:rgba(255,255,255,0.2)!important;padding:12px 18px!important;border-bottom:2px solid transparent!important;background:transparent!important;border-radius:0!important;}
.stTabs [aria-selected="true"]{color:#3b82f6!important;border-bottom:2px solid #3b82f6!important;}

[data-testid="stSelectbox"]>div>div,[data-testid="stMultiSelect"]>div>div{background:#13131f!important;border:1px solid rgba(255,255,255,0.08)!important;color:rgba(255,255,255,0.7)!important;font-size:12px!important;}
label[data-testid="stWidgetLabel"] p{color:rgba(255,255,255,0.3)!important;font-size:9px!important;letter-spacing:0.1em!important;text-transform:uppercase!important;}
[data-testid="stButton"] button{background:rgba(59,130,246,0.1)!important;border:1px solid rgba(59,130,246,0.2)!important;color:rgba(59,130,246,0.8)!important;font-family:'IBM Plex Mono',monospace!important;font-size:10px!important;border-radius:2px!important;letter-spacing:0.06em!important;}

.disc{font-size:9px;color:rgba(255,255,255,0.1);border-top:1px solid rgba(255,255,255,0.04);padding-top:16px;margin-top:28px;text-align:right;direction:rtl;font-family:'Inter',sans-serif;letter-spacing:0.04em;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════
INDICES = {
    "🇮🇱 ישראל": [
        {"t":"TA35.TA",   "n":"ת\"א 35",        "r":"Tel Aviv"},
        {"t":"TA125.TA",  "n":"ת\"א 125",       "r":"Tel Aviv"},
        {"t":"TANEGS.TA", "n":"ת\"א נדל\"ן",    "r":"Tel Aviv"},
    ],
    "🇺🇸 USA": [
        {"t":"^GSPC","n":"S&P 500",     "r":"New York"},
        {"t":"^DJI", "n":"Dow Jones",   "r":"New York"},
        {"t":"^NDX", "n":"Nasdaq 100",  "r":"New York"},
        {"t":"^VIX", "n":"VIX",         "r":"Volatility"},
        {"t":"TLT",  "n":"UST 20Y ETF","r":"Fixed Income"},
    ],
    "🇪🇺 Europe": [
        {"t":"^GDAXI",   "n":"DAX",          "r":"Frankfurt"},
        {"t":"^FTSE",    "n":"FTSE 100",      "r":"London"},
        {"t":"^STOXX50E","n":"Euro Stoxx 50", "r":"Europe"},
    ],
    "🌏 Asia": [
        {"t":"^HSI", "n":"Hang Seng",  "r":"Hong Kong"},
        {"t":"^AXJO","n":"ASX 200",    "r":"Sydney"},
        {"t":"^N225","n":"Nikkei 225", "r":"Tokyo"},
        {"t":"^NSEI","n":"Nifty 50",   "r":"Mumbai"},
    ],
    "📊 FI & Commodities": [
        {"t":"^TNX",    "n":"UST 10Y Yield","r":"Rates"},
        {"t":"^TYX",    "n":"UST 30Y Yield","r":"Rates"},
        {"t":"GC=F",    "n":"Gold",         "r":"Commodities"},
        {"t":"CL=F",    "n":"Crude Oil",    "r":"Commodities"},
        {"t":"EURUSD=X","n":"EUR/USD",      "r":"FX"},
    ],
}
ALL = [(i["t"],i["n"],sec) for sec,items in INDICES.items() for i in items]
COLORS = ["#3b82f6","#10b981","#f59e0b","#8b5cf6","#06b6d4","#f43f5e","#84cc16","#f97316","#ec4899","#c4a464"]

# ══════════════════════════════════════════════
# FETCH
# ══════════════════════════════════════════════
@st.cache_data(ttl=900)
def get_quote(ticker):
    try:
        h = yf.Ticker(ticker).history(period="5d", auto_adjust=True)
        if len(h)<2: h = yf.Ticker(ticker).history(period="1mo", auto_adjust=True)
        if len(h)<2: return None
        p,q = float(h["Close"].iloc[-1]), float(h["Close"].iloc[-2])
        vol = float(h["Volume"].iloc[-1]) if "Volume" in h else None
        hi  = float(h["High"].iloc[-1])
        lo  = float(h["Low"].iloc[-1])
        return {"price":p,"prev":q,"chg":(p-q)/q*100,"high":hi,"low":lo,"vol":vol}
    except: return None

@st.cache_data(ttl=900)
def get_hist(ticker, period="1y"):
    try:
        h = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        return h[["Close","Volume","High","Low"]].dropna()
    except: return pd.DataFrame()

@st.cache_data(ttl=900)
def get_annual(ticker):
    try:
        h = yf.Ticker(ticker).history(period="max",auto_adjust=True)["Close"].dropna()
        if h.empty: return {}
        h.index = pd.to_datetime(h.index.tz_localize(None) if h.index.tz else h.index)
        now,ret = datetime.now(),{}
        for y in [2020,2021,2022,2023,2024]:
            yr=h[h.index.year==y]; pr=h[h.index.year==y-1]
            if len(yr)>0 and len(pr)>0 and pr.iloc[-1]>0:
                ret[str(y)]=(yr.iloc[-1]-pr.iloc[-1])/pr.iloc[-1]*100
        cy=h[h.index.year==now.year]; py=h[h.index.year==now.year-1]
        if len(cy)>0 and len(py)>0 and py.iloc[-1]>0:
            ret["YTD"]=(cy.iloc[-1]-py.iloc[-1])/py.iloc[-1]*100
        cm=h[(h.index.year==now.year)&(h.index.month==now.month)]
        pm=h[(h.index.year==now.year)&(h.index.month==now.month-1)] if now.month>1 else h[h.index.year==now.year-1]
        if len(cm)>0 and len(pm)>0 and pm.iloc[-1]>0:
            ret["MTD"]=(cm.iloc[-1]-pm.iloc[-1])/pm.iloc[-1]*100
        if len(h)>=2: ret["1D"]=(h.iloc[-1]-h.iloc[-2])/h.iloc[-2]*100
        return ret
    except: return {}

def fp(v):
    if v is None or (isinstance(v,float) and pd.isna(v)): return "—"
    return ("+{:.2f}%" if v>=0 else "{:.2f}%").format(v)

def fv(v):
    if v is None: return "—"
    if v>10000: return f"{v:,.0f}"
    if v>1000:  return f"{v:,.1f}"
    if v>10:    return f"{v:,.2f}"
    return f"{v:.4f}"

def fvol(v):
    if v is None or v==0: return "—"
    if v>=1e9: return f"{v/1e9:.2f}B"
    if v>=1e6: return f"{v/1e6:.1f}M"
    if v>=1e3: return f"{v/1e3:.0f}K"
    return str(int(v))

def vc(v):
    if v is None or (isinstance(v,float) and pd.isna(v)): return "vneu"
    return "vpos" if v>=0 else "vneg"

def bc(v):
    if v is None or (isinstance(v,float) and pd.isna(v)): return "bneu"
    return "bpos" if v>=0 else "bneg"

CHART_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.3)", family="IBM Plex Mono, monospace", size=10),
    margin=dict(l=8,r=8,t=36,b=8),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False, tickfont=dict(size=9,color="rgba(255,255,255,0.2)"), zeroline=False),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False, tickfont=dict(size=9,color="rgba(255,255,255,0.2)"), zeroline=False),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#1a1a2e", bordercolor="rgba(59,130,246,0.4)", font=dict(color="rgba(255,255,255,0.85)",size=11,family="IBM Plex Mono")),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="rgba(255,255,255,0.4)",size=10)),
)

# ══════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════
now = datetime.now()
st.markdown(f"""
<div class="hdr">
  <div>
    <div class="hdr-title">📊 Global Markets Dashboard</div>
    <div class="hdr-sub">INSTITUTIONAL GRADE · REAL-TIME DATA · 15-MIN DELAY</div>
  </div>
  <div class="hdr-right">
    <div class="live-pill"><div class="live-dot"></div>LIVE</div>
    <div class="ts">{now.strftime("%d %b %Y · %H:%M:%S")}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# LOAD
# ══════════════════════════════════════════════
with st.spinner("Loading market data..."):
    quotes = {t: get_quote(t) for t,_,_ in ALL}
    annual = {t: get_annual(t) for t,_,_ in ALL}

# ══════════════════════════════════════════════
# TICKER TAPE
# ══════════════════════════════════════════════
tape=""
for t,n,_ in ALL:
    q=quotes.get(t) or {}; ar=annual.get(t) or {}
    chg=ar.get("1D") or q.get("chg",0) or 0
    cls="tpos" if chg>=0 else "tneg"
    tape+=f'<div class="ti"><span class="tn">{n}</span><span class="tp">{fv(q.get("price"))}</span><span class="{cls}">{fp(chg)}</span></div>'
st.markdown(f'<div class="tape-wrap"><div class="tape-inner">{tape}{tape}</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════
st.markdown("")
c_tab, c_btn = st.columns([9,1])
with c_btn:
    if st.button("⟳ Refresh"):
        st.cache_data.clear(); st.rerun()

tab1,tab2,tab3,tab4,tab5 = st.tabs(["📈 MARKETS","📋 RETURNS TABLE","📉 PRICE CHART","🔀 COMPARISON","🏆 BEST & WORST"])

# ══════════════════════════════════════════════
# TAB 1 — MARKETS OVERVIEW (KPI cards + mini table per region)
# ══════════════════════════════════════════════
with tab1:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)

    for sec, items in INDICES.items():
        st.markdown(f'<div class="sec-bar"><div class="sec-lbl">{sec}</div><div class="sec-line"></div></div>', unsafe_allow_html=True)

        # KPI cards
        cols = st.columns(len(items))
        for col, info in zip(cols, items):
            t = info["t"]; q = quotes.get(t) or {}; ar = annual.get(t) or {}
            price = q.get("price"); chg = ar.get("1D") or q.get("chg")
            ytd = ar.get("YTD"); mtd = ar.get("MTD")
            chg_cls = ("pos" if (chg or 0)>=0 else "neg") if chg is not None else "neu"
            with col:
                st.markdown(f"""
                <div class="kpi">
                  <div class="kpi-lbl">{info['n']}</div>
                  <div class="kpi-val">{fv(price)}</div>
                  <div><span class="kpi-chg {chg_cls}">{"▲" if (chg or 0)>=0 else "▼"} {fp(chg)}</span></div>
                  <div class="kpi-sub" style="margin-top:6px;display:flex;gap:5px;flex-wrap:wrap;">
                    <span class="badge {bc(mtd)}">MTD {fp(mtd)}</span>
                    <span class="badge {bc(ytd)}">YTD {fp(ytd)}</span>
                  </div>
                </div>""", unsafe_allow_html=True)

        # Detailed mini-table
        st.markdown(f"""
        <table class="tbl" style="margin-bottom:4px;">
          <thead><tr>
            <th>Index</th><th>Price</th><th>Prev Close</th><th>Change</th><th>High</th><th>Low</th><th>Volume</th><th>MTD</th><th>YTD</th>
          </tr></thead>
          <tbody>""", unsafe_allow_html=True)

        rows=""
        for info in items:
            t=info["t"]; q=quotes.get(t) or {}; ar=annual.get(t) or {}
            chg=ar.get("1D") or q.get("chg")
            rows+=f"""<tr>
              <td><b>{info['n']}</b><br><span style='font-size:9px;color:rgba(255,255,255,0.2);font-family:Inter'>{info['r']}</span></td>
              <td style='color:rgba(255,255,255,0.85);font-weight:500'>{fv(q.get('price'))}</td>
              <td>{fv(q.get('prev'))}</td>
              <td><span class='{"vpos" if (chg or 0)>=0 else "vneg"}'>{fp(chg)}</span></td>
              <td>{fv(q.get('high'))}</td>
              <td>{fv(q.get('low'))}</td>
              <td>{fvol(q.get('vol'))}</td>
              <td><span class='{vc(ar.get("MTD"))}'>{fp(ar.get("MTD"))}</span></td>
              <td><span class='{vc(ar.get("YTD"))}'>{fp(ar.get("YTD"))}</span></td>
            </tr>"""
        st.markdown(rows+"</tbody></table>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2 — ANNUAL RETURNS TABLE
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    YCOLS = ["2020","2021","2022","2023","2024","YTD","MTD","1D"]
    head = "<th>Index</th><th>Region</th>"+"".join(f"<th>{c}</th>" for c in YCOLS)
    rows=""
    for t,n,sec in ALL:
        ar=annual.get(t) or {}
        cells="".join(f'<td><span class="{vc(ar.get(c))}">{fp(ar.get(c))}</span></td>' for c in YCOLS)
        rows+=f"<tr><td><b>{n}</b></td><td style='font-size:10px;color:rgba(255,255,255,0.2)'>{sec}</td>{cells}</tr>"
    st.markdown(f"""
    <div class="panel" style="overflow-x:auto;">
      <div class="panel-title">Annual Performance Overview — 2020 to Present</div>
      <table class="tbl"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 3 — PRICE CHART WITH MA + VOLUME
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    tmap = {f"{n}  [{t}]":t for t,n,_ in ALL}
    nmap = {t:n for t,n,_ in ALL}
    c1,c2,c3 = st.columns([3,1,1])
    with c1: sel = st.selectbox("Select Index", list(tmap.keys()))
    with c2:
        pmap={"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","2Y":"2y","5Y":"5y"}
        per=pmap[st.selectbox("Period",list(pmap.keys()),index=3)]
    with c3:
        ma_options = {"20 & 50 Day MA": [20,50], "50 & 200 Day MA": [50,200], "No MA": []}
        ma_sel = st.selectbox("Moving Average", list(ma_options.keys()))

    sel_t = tmap[sel]; sel_n = nmap[sel_t]
    h = get_hist(sel_t, per)

    if not h.empty:
        close = h["Close"]
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.72,0.28], vertical_spacing=0.02)

        # Price line
        is_pos = close.iloc[-1] >= close.iloc[0]
        lc = "#10b981" if is_pos else "#f43f5e"
        fig.add_trace(go.Scatter(
            x=close.index, y=close, name="Price", mode="lines",
            line=dict(color=lc, width=1.8),
            fill="tozeroy", fillcolor=f"rgba({'16,185,129' if is_pos else '244,63,94'},0.04)",
            hovertemplate="%{x|%d %b %Y}  <b>%{y:,.2f}</b><extra>Price</extra>"
        ), row=1, col=1)

        # Moving Averages
        ma_periods = ma_options[ma_sel]
        ma_colors = ["#f59e0b","#8b5cf6"]
        for i, ma in enumerate(ma_periods):
            if len(close) > ma:
                ma_vals = close.rolling(ma).mean()
                fig.add_trace(go.Scatter(
                    x=ma_vals.index, y=ma_vals, name=f"{ma}D MA",
                    mode="lines", line=dict(color=ma_colors[i], width=1.2, dash="dot"),
                    hovertemplate=f"%{{y:,.2f}}<extra>{ma}D MA</extra>"
                ), row=1, col=1)

        # Volume bars
        if "Volume" in h.columns and h["Volume"].sum() > 0:
            vol_colors = ["rgba(16,185,129,0.5)" if c>=o else "rgba(244,63,94,0.5)"
                          for c,o in zip(h["Close"], h["Close"].shift(1).fillna(h["Close"]))]
            fig.add_trace(go.Bar(
                x=h.index, y=h["Volume"], name="Volume",
                marker_color=vol_colors, marker_line_width=0,
                hovertemplate="%{x|%d %b %Y}  <b>%{y:,.0f}</b><extra>Volume</extra>"
            ), row=2, col=1)

        fig.update_layout(
            **CHART_BASE,
            height=500, showlegend=True,
            title=dict(text=f"{sel_n}  ·  Price & Volume", font=dict(color="rgba(255,255,255,0.5)",size=12,family="Inter"), x=0.01),
            yaxis=dict(**CHART_BASE["yaxis"], title=dict(text="Price", font=dict(size=9,color="rgba(255,255,255,0.2)"))),
            yaxis2=dict(**CHART_BASE["yaxis"], title=dict(text="Volume", font=dict(size=9,color="rgba(255,255,255,0.2)"))),
            margin=dict(l=12,r=12,t=44,b=8),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        # Stats row
        q = quotes.get(sel_t) or {}; ar = annual.get(sel_t) or {}
        chg = ar.get("1D") or q.get("chg")
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        stats = [
            ("Current Price", fv(q.get("price")), None),
            ("Previous Close", fv(q.get("prev")), None),
            ("Day Change", fp(chg), chg),
            ("52W High", fv(close.rolling(252).max().iloc[-1] if len(close)>=252 else close.max()), None),
            ("52W Low",  fv(close.rolling(252).min().iloc[-1] if len(close)>=252 else close.min()), None),
            ("YTD Return", fp(ar.get("YTD")), ar.get("YTD")),
        ]
        for col, (lbl,val,chgv) in zip([col1,col2,col3,col4,col5,col6], stats):
            chg_cls = ("pos" if (chgv or 0)>=0 else "neg") if chgv is not None else "neu"
            with col:
                st.markdown(f"""
                <div class="kpi">
                  <div class="kpi-lbl">{lbl}</div>
                  <div class="kpi-val" style="font-size:16px">{val}</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.warning("Data unavailable for this instrument.")
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 4 — COMPARISON
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    n2t = {n:t for t,n,_ in ALL}
    defs = ["S&P 500","Nasdaq 100","ת\"א 35","DAX","FTSE 100","Hang Seng"]
    dv = [d for d in defs if d in n2t]
    c1,c2 = st.columns([3,1])
    with c1: sel_names = st.multiselect("Select Indices to Compare", list(n2t.keys()), default=dv)
    with c2:
        cpmap={"3M":"3mo","6M":"6mo","1Y":"1y","3Y":"3y","5Y":"5y"}
        cper=cpmap[st.selectbox("Period",list(cpmap.keys()),index=2,key="cp")]

    if sel_names:
        fig3 = go.Figure()
        for i,name in enumerate(sel_names):
            t=n2t[name]; h=get_hist(t,cper)
            if h.empty or "Close" not in h: continue
            close=h["Close"]; norm=(close-close.iloc[0])/close.iloc[0]*100
            fig3.add_trace(go.Scatter(
                x=close.index, y=norm, mode="lines", name=name,
                line=dict(color=COLORS[i%len(COLORS)], width=1.8),
                hovertemplate=f"<b>{name}</b>: %{{y:+.2f}}%<extra></extra>"
            ))
        fig3.update_layout(
            **CHART_BASE, height=420,
            title=dict(text="Normalized Performance Comparison (base=0%)", font=dict(color="rgba(255,255,255,0.4)",size=12,family="Inter"), x=0.01),
            yaxis=dict(**CHART_BASE["yaxis"], tickformat="+.1f", ticksuffix="%"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})

        # Summary table
        head2="<th>Index</th><th>Period Return</th><th>1D</th><th>MTD</th><th>YTD</th><th>2024</th><th>2023</th><th>2022</th>"
        rows2=""
        for name in sel_names:
            t=n2t[name]; h=get_hist(t,cper); ar=annual.get(t) or {}; q=quotes.get(t) or {}
            if h.empty or "Close" not in h: continue
            close=h["Close"]; tot=(close.iloc[-1]-close.iloc[0])/close.iloc[0]*100
            chg=ar.get("1D") or q.get("chg")
            rows2+=f"""<tr>
              <td><b>{name}</b></td>
              <td><span class='{vc(tot)}'>{fp(tot)}</span></td>
              <td><span class='{vc(chg)}'>{fp(chg)}</span></td>
              <td><span class='{vc(ar.get("MTD"))}'>{fp(ar.get("MTD"))}</span></td>
              <td><span class='{vc(ar.get("YTD"))}'>{fp(ar.get("YTD"))}</span></td>
              <td><span class='{vc(ar.get("2024"))}'>{fp(ar.get("2024"))}</span></td>
              <td><span class='{vc(ar.get("2023"))}'>{fp(ar.get("2023"))}</span></td>
              <td><span class='{vc(ar.get("2022"))}'>{fp(ar.get("2022"))}</span></td>
            </tr>"""
        st.markdown(f'<div class="panel" style="overflow-x:auto;margin-top:16px"><table class="tbl"><thead><tr>{head2}</tr></thead><tbody>{rows2}</tbody></table></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 5 — BEST & WORST
# ══════════════════════════════════════════════
with tab5:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    periods_bw = {"1 Day":"1D","MTD":"MTD","YTD":"YTD","2024":"2024","2023":"2023"}
    sel_bw = st.selectbox("Rank by Period", list(periods_bw.keys()))
    key_bw = periods_bw[sel_bw]

    ranked = []
    for t,n,sec in ALL:
        ar=annual.get(t) or {}; q=quotes.get(t) or {}
        v = ar.get(key_bw) or (q.get("chg") if key_bw=="1D" else None)
        ranked.append({"ticker":t,"name":n,"region":sec,"val":v,"price":q.get("price"),"ytd":ar.get("YTD"),"mtd":ar.get("MTD")})

    ranked_valid = [r for r in ranked if r["val"] is not None]
    ranked_sorted = sorted(ranked_valid, key=lambda x: x["val"], reverse=True)

    best5  = ranked_sorted[:5]
    worst5 = ranked_sorted[-5:][::-1]

    c1,c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="panel"><div class="panel-title" style="color:#10b981">🏆 Top 5 — {sel_bw}</div>', unsafe_allow_html=True)
        rows=""
        for i,r in enumerate(best5):
            rows+=f"""<tr>
              <td><span style='color:rgba(255,255,255,0.3);font-size:10px'>#{i+1}</span>  <b>{r['name']}</b></td>
              <td>{fv(r['price'])}</td>
              <td><span class='vpos'>{fp(r['val'])}</span></td>
              <td><span class='{vc(r["ytd"])}'>{fp(r['ytd'])}</span></td>
            </tr>"""
        st.markdown(f'<table class="tbl"><thead><tr><th>Index</th><th>Price</th><th>{sel_bw}</th><th>YTD</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)

        # Bar chart best
        fig_b = go.Figure(go.Bar(
            x=[r["name"] for r in best5],
            y=[r["val"] for r in best5],
            marker_color=["rgba(16,185,129,0.7)"]*5,
            marker_line_width=0,
            text=[fp(r["val"]) for r in best5],
            textposition="outside", textfont=dict(size=9,color="rgba(255,255,255,0.4)"),
        ))
        fig_b.update_layout(**CHART_BASE, height=220, showlegend=False,
            yaxis=dict(**CHART_BASE["yaxis"],tickformat="+.1f",ticksuffix="%"), bargap=0.4)
        st.plotly_chart(fig_b, use_container_width=True, config={"displayModeBar":False})

    with c2:
        st.markdown(f'<div class="panel"><div class="panel-title" style="color:#f43f5e">📉 Bottom 5 — {sel_bw}</div>', unsafe_allow_html=True)
        rows=""
        for i,r in enumerate(worst5):
            rows+=f"""<tr>
              <td><span style='color:rgba(255,255,255,0.3);font-size:10px'>#{i+1}</span>  <b>{r['name']}</b></td>
              <td>{fv(r['price'])}</td>
              <td><span class='vneg'>{fp(r['val'])}</span></td>
              <td><span class='{vc(r["ytd"])}'>{fp(r['ytd'])}</span></td>
            </tr>"""
        st.markdown(f'<table class="tbl"><thead><tr><th>Index</th><th>Price</th><th>{sel_bw}</th><th>YTD</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)

        fig_w = go.Figure(go.Bar(
            x=[r["name"] for r in worst5],
            y=[r["val"] for r in worst5],
            marker_color=["rgba(244,63,94,0.7)"]*5,
            marker_line_width=0,
            text=[fp(r["val"]) for r in worst5],
            textposition="outside", textfont=dict(size=9,color="rgba(255,255,255,0.4)"),
        ))
        fig_w.update_layout(**CHART_BASE, height=220, showlegend=False,
            yaxis=dict(**CHART_BASE["yaxis"],tickformat="+.1f",ticksuffix="%"), bargap=0.4)
        st.plotly_chart(fig_w, use_container_width=True, config={"displayModeBar":False})

    # Full ranking table
    st.markdown('<div class="sec-bar"><div class="sec-lbl">Full Ranking</div><div class="sec-line"></div></div>', unsafe_allow_html=True)
    head_r="<th>Rank</th><th>Index</th><th>Price</th><th>"+sel_bw+"</th><th>1D</th><th>MTD</th><th>YTD</th>"
    rows_r=""
    for i,r in enumerate(ranked_sorted):
        ar=annual.get(r["ticker"]) or {}; q=quotes.get(r["ticker"]) or {}
        chg=ar.get("1D") or q.get("chg")
        rows_r+=f"""<tr>
          <td style='color:rgba(255,255,255,0.2)'>{i+1}</td>
          <td><b>{r['name']}</b><br><span style='font-size:9px;color:rgba(255,255,255,0.2)'>{r['region']}</span></td>
          <td style='color:rgba(255,255,255,0.8)'>{fv(r['price'])}</td>
          <td><span class='{vc(r["val"])}'><b>{fp(r["val"])}</b></span></td>
          <td><span class='{vc(chg)}'>{fp(chg)}</span></td>
          <td><span class='{vc(r["mtd"])}'>{fp(r["mtd"])}</span></td>
          <td><span class='{vc(r["ytd"])}'>{fp(r["ytd"])}</span></td>
        </tr>"""
    st.markdown(f'<div class="panel" style="overflow-x:auto"><table class="tbl"><thead><tr>{head_r}</tr></thead><tbody>{rows_r}</tbody></table></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='padding:0 28px'><div class='disc'>Data: Yahoo Finance · Delay: up to 15 minutes · Not investment advice · Past performance does not guarantee future results</div></div>", unsafe_allow_html=True)
