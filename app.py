import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Global Markets | Institutional Dashboard",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600&family=Inter:wght@300;400;500;600&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }

[data-testid="stAppViewContainer"] { background: #08080f; min-height: 100vh; }
[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }

.topbar {
    background: linear-gradient(135deg, #0c0c18 0%, #0a0a14 100%);
    border-bottom: 1px solid rgba(196,164,100,0.15);
    padding: 0 40px; height: 64px;
    display: flex; align-items: center; justify-content: space-between;
}
.topbar-left { display: flex; align-items: center; gap: 24px; }
.logo-mark { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 600; color: #c4a464; letter-spacing: 0.04em; }
.logo-sep { width: 1px; height: 28px; background: rgba(196,164,100,0.2); }
.logo-sub { font-family: 'Inter', sans-serif; font-size: 10px; font-weight: 500; letter-spacing: 0.18em; text-transform: uppercase; color: rgba(196,164,100,0.5); }
.topbar-right { display: flex; align-items: center; gap: 20px; }
.live-indicator { display: flex; align-items: center; gap: 7px; font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: rgba(196,164,100,0.6); letter-spacing: 0.08em; text-transform: uppercase; }
.live-dot { width: 6px; height: 6px; border-radius: 50%; background: #10b981; box-shadow: 0 0 8px rgba(16,185,129,0.6); animation: blink 2s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.timestamp { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: rgba(255,255,255,0.2); letter-spacing: 0.05em; }

.tape { background: #060610; border-bottom: 1px solid rgba(196,164,100,0.08); height: 36px; overflow: hidden; display: flex; align-items: center; }
.tape-inner { display: flex; animation: tape-scroll 80s linear infinite; white-space: nowrap; }
.tape:hover .tape-inner { animation-play-state: paused; }
@keyframes tape-scroll { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
.tape-item { display: inline-flex; align-items: center; gap: 8px; padding: 0 24px; border-right: 1px solid rgba(255,255,255,0.04); font-family: 'IBM Plex Mono', monospace; font-size: 11px; }
.tape-name { color: rgba(255,255,255,0.35); letter-spacing: 0.06em; }
.tape-price { color: rgba(255,255,255,0.75); font-weight: 500; }
.tape-pos { color: #10b981; }
.tape-neg { color: #f43f5e; }

.main-wrap { padding: 28px 40px 48px; background: #08080f; }

.sec-head { display: flex; align-items: center; gap: 16px; margin: 32px 0 16px; }
.sec-head-line { flex:1; height:1px; background: linear-gradient(90deg, rgba(196,164,100,0.15), transparent); }
.sec-head-text { font-family: 'Inter', sans-serif; font-size: 9px; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; color: rgba(196,164,100,0.45); white-space: nowrap; }
.sec-flag { font-size: 13px; }

.idx-card { background: #0c0c1a; padding: 18px 20px 14px; transition: background 0.2s; position: relative; overflow: hidden; border: 1px solid rgba(196,164,100,0.06); border-radius: 2px; margin-bottom: 1px; }
.idx-card::before { content:''; position:absolute; top:0; left:0; right:0; height:1px; background: linear-gradient(90deg, transparent, rgba(196,164,100,0.12), transparent); }
.idx-card:hover { background: #10102a; }
.idx-card-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.idx-name { font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.7); letter-spacing: 0.04em; }
.idx-region { font-family: 'Inter', sans-serif; font-size: 9px; color: rgba(255,255,255,0.2); letter-spacing: 0.06em; text-transform: uppercase; margin-top: 2px; }
.idx-flag { font-size: 14px; opacity: 0.8; }
.idx-price { font-family: 'IBM Plex Mono', monospace; font-size: 21px; font-weight: 400; color: rgba(255,255,255,0.9); letter-spacing: -0.01em; margin-bottom: 10px; direction: ltr; text-align: right; }
.idx-pills { display: flex; gap: 5px; flex-wrap: wrap; justify-content: flex-end; }
.pill { font-family: 'IBM Plex Mono', monospace; font-size: 10px; font-weight: 400; padding: 3px 8px; border-radius: 1px; letter-spacing: 0.03em; direction: ltr; }
.pill-label { font-size: 8px; font-family: 'Inter', sans-serif; letter-spacing: 0.08em; opacity: 0.6; margin-left: 3px; text-transform: uppercase; }
.p-pos { color: #10b981; background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.15); }
.p-neg { color: #f43f5e; background: rgba(244,63,94,0.08); border: 1px solid rgba(244,63,94,0.15); }
.p-neu { color: rgba(255,255,255,0.3); background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); }

.ret-table-wrap { border: 1px solid rgba(196,164,100,0.08); border-radius: 2px; overflow: hidden; background: #0c0c1a; }
.ret-table { width: 100%; border-collapse: collapse; font-size: 11px; }
.ret-table thead th { background: #080812; padding: 10px 14px; text-align: center; font-family: 'IBM Plex Mono', monospace; font-size: 9px; font-weight: 400; letter-spacing: 0.12em; text-transform: uppercase; color: rgba(196,164,100,0.4); border-bottom: 1px solid rgba(196,164,100,0.08); }
.ret-table thead th:first-child { text-align: right; padding-right: 20px; }
.ret-table tbody tr { border-bottom: 1px solid rgba(255,255,255,0.03); transition: background 0.15s; }
.ret-table tbody tr:hover { background: rgba(196,164,100,0.03); }
.ret-table tbody tr:last-child { border-bottom: none; }
.ret-table td { padding: 10px 14px; text-align: center; font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: rgba(255,255,255,0.5); direction: ltr; }
.ret-table td:first-child { text-align: right; font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 500; color: rgba(255,255,255,0.65); padding-right: 20px; direction: rtl; }
.rc-pos { color: #10b981; }
.rc-neg { color: #f43f5e; }
.rc-neu { color: rgba(255,255,255,0.2); }

.chart-box { background: #0c0c1a; border: 1px solid rgba(196,164,100,0.08); border-radius: 2px; padding: 20px; position: relative; }
.chart-box::before { content:''; position:absolute; top:0; left:0; right:0; height:1px; background: linear-gradient(90deg, rgba(196,164,100,0.2), transparent); }

.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid rgba(196,164,100,0.1) !important; gap: 0 !important; padding: 0 !important; }
.stTabs [data-baseweb="tab"] { font-family: 'Inter', sans-serif !important; font-size: 10px !important; font-weight: 600 !important; letter-spacing: 0.12em !important; text-transform: uppercase !important; color: rgba(255,255,255,0.2) !important; padding: 12px 20px !important; border-bottom: 2px solid transparent !important; background: transparent !important; border-radius: 0 !important; }
.stTabs [aria-selected="true"] { color: rgba(196,164,100,0.8) !important; border-bottom: 2px solid rgba(196,164,100,0.5) !important; background: transparent !important; }

label[data-testid="stWidgetLabel"] p { color: rgba(196,164,100,0.4) !important; font-size: 9px !important; letter-spacing: 0.12em !important; text-transform: uppercase !important; font-family: 'Inter', sans-serif !important; }

[data-testid="stButton"] button { background: rgba(196,164,100,0.08) !important; border: 1px solid rgba(196,164,100,0.2) !important; color: rgba(196,164,100,0.7) !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 10px !important; letter-spacing: 0.08em !important; border-radius: 1px !important; }

.disc { font-family: 'Inter', sans-serif; font-size: 9px; color: rgba(255,255,255,0.12); letter-spacing: 0.05em; line-height: 1.8; border-top: 1px solid rgba(196,164,100,0.06); padding-top: 20px; margin-top: 32px; text-align: right; direction: rtl; }
</style>
""", unsafe_allow_html=True)

INDICES = {
    "israel": {"label":"ישראל","flag":"🇮🇱","items":[
        {"ticker":"TA35.TA","name":"ת\"א 35","region":"Tel Aviv"},
        {"ticker":"TA125.TA","name":"ת\"א 125","region":"Tel Aviv"},
        {"ticker":"TANEGS.TA","name":"ת\"א נדל\"ן","region":"Tel Aviv"},
    ]},
    "usa": {"label":"ארצות הברית","flag":"🇺🇸","items":[
        {"ticker":"^GSPC","name":"S&P 500","region":"New York"},
        {"ticker":"^DJI","name":"Dow Jones","region":"New York"},
        {"ticker":"^NDX","name":"Nasdaq 100","region":"New York"},
        {"ticker":"^VIX","name":"VIX","region":"Volatility"},
        {"ticker":"TLT","name":"UST 20Y ETF","region":"Fixed Income"},
    ]},
    "europe": {"label":"אירופה","flag":"🇪🇺","items":[
        {"ticker":"^GDAXI","name":"DAX","region":"Frankfurt"},
        {"ticker":"^FTSE","name":"FTSE 100","region":"London"},
        {"ticker":"^STOXX50E","name":"Euro Stoxx 50","region":"Europe"},
    ]},
    "asia": {"label":"אסיה / פסיפיק","flag":"🌏","items":[
        {"ticker":"^HSI","name":"Hang Seng","region":"Hong Kong"},
        {"ticker":"^AXJO","name":"ASX 200","region":"Sydney"},
        {"ticker":"^N225","name":"Nikkei 225","region":"Tokyo"},
        {"ticker":"^NSEI","name":"Nifty 50","region":"Mumbai"},
    ]},
    "fi": {"label":"אג\"ח, סחורות ומט\"ח","flag":"📊","items":[
        {"ticker":"^TNX","name":"UST 10Y Yield","region":"Fixed Income"},
        {"ticker":"^TYX","name":"UST 30Y Yield","region":"Fixed Income"},
        {"ticker":"GC=F","name":"Gold","region":"Commodities"},
        {"ticker":"CL=F","name":"Crude Oil WTI","region":"Commodities"},
        {"ticker":"EURUSD=X","name":"EUR / USD","region":"FX"},
    ]},
}

ALL = [(i["ticker"],i["name"],sec) for sec,sd in INDICES.items() for i in sd["items"]]

@st.cache_data(ttl=900)
def get_quote(ticker):
    try:
        h = yf.Ticker(ticker).history(period="5d",auto_adjust=True)
        if len(h)<2: h = yf.Ticker(ticker).history(period="1mo",auto_adjust=True)
        if len(h)<2: return None
        p,q = float(h["Close"].iloc[-1]),float(h["Close"].iloc[-2])
        return {"price":p,"prev":q,"chg":(p-q)/q*100 if q else None}
    except: return None

@st.cache_data(ttl=900)
def get_hist(ticker,period="1y"):
    try:
        h = yf.Ticker(ticker).history(period=period,auto_adjust=True)
        return h["Close"].dropna()
    except: return pd.Series(dtype=float)

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

def fpr(v):
    if v is None: return "—"
    if v>10000: return f"{v:,.0f}"
    if v>1000: return f"{v:,.1f}"
    if v>10: return f"{v:,.2f}"
    return f"{v:.4f}"

def pc(v):
    if v is None or (isinstance(v,float) and pd.isna(v)): return "p-neu"
    return "p-pos" if v>=0 else "p-neg"

def rc(v):
    if v is None or (isinstance(v,float) and pd.isna(v)): return "rc-neu"
    return "rc-pos" if v>=0 else "rc-neg"

COLORS=["#c4a464","#3b82f6","#10b981","#8b5cf6","#06b6d4","#f59e0b","#f43f5e","#84cc16","#ec4899","#14b8a6"]
CHART=dict(
    paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.25)",family="IBM Plex Mono, monospace",size=10),
    margin=dict(l=8,r=8,t=40,b=8),
    xaxis=dict(gridcolor="rgba(255,255,255,0.03)",showline=False,tickfont=dict(size=9,color="rgba(255,255,255,0.2)")),
    yaxis=dict(gridcolor="rgba(255,255,255,0.03)",showline=False,tickfont=dict(size=9,color="rgba(255,255,255,0.2)")),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#0c0c1a",bordercolor="rgba(196,164,100,0.3)",font=dict(color="rgba(255,255,255,0.8)",size=11,family="IBM Plex Mono")),
    legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="rgba(255,255,255,0.4)",size=10)),
)

now = datetime.now()
st.markdown(f"""
<div class="topbar">
  <div class="topbar-left">
    <div class="logo-mark">◈ MARKETS</div>
    <div class="logo-sep"></div>
    <div class="logo-sub">Global Indices Terminal</div>
  </div>
  <div class="topbar-right">
    <div class="live-indicator"><div class="live-dot"></div> Live · 15min delay</div>
    <div class="timestamp">{now.strftime("%d %b %Y  %H:%M:%S")}</div>
  </div>
</div>
""", unsafe_allow_html=True)

with st.spinner(""):
    quotes = {t: get_quote(t) for t,_,_ in ALL}
    annual = {t: get_annual(t) for t,_,_ in ALL}

tape_items=""
for ticker,name,_ in ALL:
    q=quotes.get(ticker) or {}
    ar=annual.get(ticker) or {}
    chg=ar.get("1D") or q.get("chg")
    cls="tape-pos" if (chg or 0)>=0 else "tape-neg"
    tape_items+=f'<div class="tape-item"><span class="tape-name">{name}</span><span class="tape-price">{fpr(q.get("price"))}</span><span class="{cls}">{fp(chg)}</span></div>'

st.markdown(f'<div class="tape"><div class="tape-inner">{tape_items}{tape_items}</div></div>', unsafe_allow_html=True)
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

col_tabs,col_btn=st.columns([8,1])
with col_btn:
    if st.button("⟳ Refresh"):
        st.cache_data.clear()
        st.rerun()

tab1,tab2,tab3,tab4=st.tabs(["MARKETS","ANNUAL RETURNS","CHART","COMPARISON"])

with tab1:
    for sec_key,sec_data in INDICES.items():
        items=sec_data["items"]; flag=sec_data["flag"]; label=sec_data["label"]
        st.markdown(f'<div class="sec-head"><span class="sec-flag">{flag}</span><span class="sec-head-text">{label}</span><div class="sec-head-line"></div></div>', unsafe_allow_html=True)
        cols=st.columns(len(items))
        for col,info in zip(cols,items):
            ticker=info["ticker"]
            q=quotes.get(ticker) or {}
            ar=annual.get(ticker) or {}
            price=q.get("price")
            chg1d=ar.get("1D") or q.get("chg")
            ytd=ar.get("YTD"); mtd=ar.get("MTD")
            with col:
                st.markdown(f"""
                <div class="idx-card">
                  <div class="idx-card-top">
                    <div><div class="idx-name">{info['name']}</div><div class="idx-region">{info['region']}</div></div>
                    <div class="idx-flag">{flag}</div>
                  </div>
                  <div class="idx-price">{fpr(price)}</div>
                  <div class="idx-pills">
                    <div class="pill {pc(chg1d)}"><span class="pill-label">1D</span>{fp(chg1d)}</div>
                    <div class="pill {pc(mtd)}"><span class="pill-label">MTD</span>{fp(mtd)}</div>
                    <div class="pill {pc(ytd)}"><span class="pill-label">YTD</span>{fp(ytd)}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

with tab2:
    COLS=["2020","2021","2022","2023","2024","YTD","MTD","1D"]
    rows_html=""
    for ticker,name,_ in ALL:
        ar=annual.get(ticker) or {}
        cells=f"<td>{name}</td>"
        for c in COLS:
            v=ar.get(c); cls=rc(v); txt=fp(v)
            cells+=f'<td><span class="{cls}">{txt}</span></td>'
        rows_html+=f"<tr>{cells}</tr>"
    head_html="<th>INDEX</th>"+"".join(f"<th>{c}</th>" for c in COLS)
    st.markdown(f'<div class="ret-table-wrap"><table class="ret-table"><thead><tr>{head_html}</tr></thead><tbody>{rows_html}</tbody></table></div>', unsafe_allow_html=True)

with tab3:
    ticker_map={f"{name}  [{ticker}]":ticker for ticker,name,_ in ALL}
    name_map={ticker:name for ticker,name,_ in ALL}
    c1,c2=st.columns([3,1])
    with c1: sel_lbl=st.selectbox("INDEX",list(ticker_map.keys()),label_visibility="visible")
    with c2:
        pmap={"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","3Y":"3y","5Y":"5y"}
        sel_per=pmap[st.selectbox("PERIOD",list(pmap.keys()),index=3,label_visibility="visible")]
    sel_t=ticker_map[sel_lbl]; hist=get_hist(sel_t,sel_per)
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    if not hist.empty:
        first=hist.iloc[0]; norm=(hist-first)/first*100
        is_pos=norm.iloc[-1]>=0
        lc="#10b981" if is_pos else "#f43f5e"
        fc="rgba(16,185,129,0.05)" if is_pos else "rgba(244,63,94,0.05)"
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=hist.index,y=norm,mode="lines",name=name_map[sel_t],line=dict(color=lc,width=1.5),fill="tozeroy",fillcolor=fc,hovertemplate="%{x|%d %b %Y}  <b>%{y:+.2f}%</b><extra></extra>"))
        fig.update_layout(**CHART,yaxis=dict(**CHART["yaxis"],tickformat="+.1f",ticksuffix="%"),height=340,showlegend=False,title=dict(text=f"{name_map[sel_t]}  ·  Performance ({sel_per})",font=dict(color="rgba(196,164,100,0.5)",size=11,family="Inter"),x=0,xanchor="left"))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        ar=annual.get(sel_t) or {}; yrs=["2020","2021","2022","2023","2024","YTD","MTD"]
        vals=[ar.get(y) for y in yrs]
        bar_c=["rgba(16,185,129,0.7)" if (v or 0)>=0 else "rgba(244,63,94,0.7)" for v in vals]
        fig2=go.Figure()
        fig2.add_trace(go.Bar(x=yrs,y=vals,marker_color=bar_c,marker_line_width=0,text=[fp(v) for v in vals],textposition="outside",textfont=dict(size=9,color="rgba(255,255,255,0.35)"),hovertemplate="%{x}: <b>%{y:+.2f}%</b><extra></extra>"))
        fig2.update_layout(**CHART,yaxis=dict(**CHART["yaxis"],tickformat="+.1f",ticksuffix="%"),height=260,bargap=0.4,showlegend=False,title=dict(text="Annual Returns",font=dict(color="rgba(196,164,100,0.5)",size=11,family="Inter"),x=0,xanchor="left"))
        st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    n2t={name:ticker for ticker,name,_ in ALL}
    defs=["S&P 500","Nasdaq 100","ת\"א 35","DAX","FTSE 100"]
    defs_valid=[d for d in defs if d in n2t]
    c1,c2=st.columns([3,1])
    with c1: sel_names=st.multiselect("SELECT INDICES",list(n2t.keys()),default=defs_valid,label_visibility="visible")
    with c2:
        cpmap={"3M":"3mo","6M":"6mo","1Y":"1y","3Y":"3y","5Y":"5y"}
        cper=cpmap[st.selectbox("PERIOD",list(cpmap.keys()),index=2,key="cper",label_visibility="visible")]
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    if sel_names:
        fig3=go.Figure()
        for i,name in enumerate(sel_names):
            t=n2t[name]; h=get_hist(t,cper)
            if h.empty: continue
            norm=(h-h.iloc[0])/h.iloc[0]*100
            fig3.add_trace(go.Scatter(x=h.index,y=norm,mode="lines",name=name,line=dict(color=COLORS[i%len(COLORS)],width=1.5),hovertemplate=f"<b>{name}</b>: %{{y:+.2f}}%<extra></extra>"))
        fig3.update_layout(**CHART,yaxis=dict(**CHART["yaxis"],tickformat="+.1f",ticksuffix="%"),height=400,title=dict(text="Normalized Performance Comparison",font=dict(color="rgba(196,164,100,0.5)",size=11,family="Inter"),x=0,xanchor="left"),legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
        st.plotly_chart(fig3,use_container_width=True,config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div class='disc'>Data provided by Yahoo Finance · 15-minute delay · For informational purposes only — not investment advice · Past performance is not indicative of future results</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
