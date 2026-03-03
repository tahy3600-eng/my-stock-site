“””
ETF Market Watch - Optimized
“””

import streamlit as st
import yfinance as yf
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(**name**)

# ── 상수 ───────────────────────────────────────────────────────────────────────

KST = timezone(timedelta(hours=9))

COLORS = {
“red”:    “#D62828”,
“blue”:   “#003049”,
“green”:  “#2A9D8F”,
“orange”: “#F77F00”,
“dark”:   “#212529”,
“muted”:  “#6c757d”,
“light”:  “#adb5bd”,
}

ETF_SYMBOLS: dict[str, str] = {
“Nasdaq 100 (QQQ)”: “QQQ”,
“S&P 500 (VOO)”:    “VOO”,
}

MACRO_SYMBOLS: dict[str, str] = {
“USD / KRW”: “USDKRW=X”,
“VIX INDEX”: “^VIX”,
}

# ── 데이터 클래스 ───────────────────────────────────────────────────────────────

@dataclass
class TickerSnapshot:
symbol:   str
price:    float
ath:      float
ath_date: str
gap_pct:  float

# ── 데이터 수집 ────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_ath(symbol: str) -> Optional[tuple[float, str]]:
“”“전고점은 자주 변하지 않으므로 1시간 캐시.”””
try:
df = yf.Ticker(symbol).history(period=“2y”, auto_adjust=True)
if df.empty:
return None
return float(df[“High”].max()), df[“High”].idxmax().strftime(”%Y.%m.%d”)
except Exception as e:
logger.warning(“ATH fetch failed [%s]: %s”, symbol, e)
return None

@st.cache_data(ttl=30, show_spinner=False)
def _fetch_price(symbol: str) -> Optional[float]:
“”“실시간 가격은 30초 캐시 (fragment 갱신 주기와 동기화).”””
try:
df = yf.Ticker(symbol).history(period=“2d”, auto_adjust=True)
if df.empty:
return None
return float(df[“Close”].iloc[-1])
except Exception as e:
logger.warning(“Price fetch failed [%s]: %s”, symbol, e)
return None

def get_snapshot(symbol: str) -> Optional[TickerSnapshot]:
“”“ATH + 현재가 합산 스냅샷 반환. 둘 중 하나라도 실패하면 None.”””
price = _fetch_price(symbol)
ath   = _fetch_ath(symbol)
if price is None or ath is None:
return None
ath_val, ath_date = ath
return TickerSnapshot(
symbol   = symbol,
price    = price,
ath      = ath_val,
ath_date = ath_date,
gap_pct  = ((price - ath_val) / ath_val) * 100,
)

# ── UI 헬퍼 ───────────────────────────────────────────────────────────────────

def _card_html(title: str, main: str, sub: str = “”, footer: str = “”) -> str:
return (
f’<div style="background:white;padding:40px 20px;border-radius:24px;'
f'box-shadow:0 4px 20px rgba(0,0,0,0.03);border:1px solid #f1f3f5;'
f'text-align:center;margin-bottom:20px;">’
f’<div style=“color:{COLORS[“muted”]};font-size:12px;font-weight:600;’
f’letter-spacing:1.2px;margin-bottom:15px;text-transform:uppercase;”>{title}</div>’
f’{main}{sub}{footer}’
f’</div>’
)

def draw_etf_card(title: str, snap: TickerSnapshot) -> None:
color  = COLORS[“red”] if snap.gap_pct >= 0 else COLORS[“blue”]
main   = f’<div style="font-size:48px;font-weight:800;color:{color};line-height:1;">{snap.gap_pct:+.2f}%</div>’
sub    = f’<div style="font-size:20px;font-weight:600;color:#444;margin-top:8px;">${snap.price:,.2f}</div>’
footer = f’<div style=“color:{COLORS[“light”]};font-size:11px;margin-top:15px;”>ATH ${snap.ath:,.1f} ({snap.ath_date})</div>’
st.markdown(_card_html(title, main, sub, footer), unsafe_allow_html=True)

def draw_vix_card(title: str, price: float) -> None:
if price < 20:
v_color, v_state = COLORS[“green”],  “STABLE”
elif price < 30:
v_color, v_state = COLORS[“orange”], “CAUTION”
else:
v_color, v_state = COLORS[“red”],    “PANIC”
main   = f’<div style=“font-size:45px;font-weight:800;color:{COLORS[“dark”]};line-height:1;”>{price:,.2f}</div>’
footer = f’<div style="color:{v_color};font-size:13px;font-weight:700;margin-top:15px;letter-spacing:1px;">● {v_state}</div>’
st.markdown(_card_html(title, main, footer=footer), unsafe_allow_html=True)

def draw_macro_card(title: str, price: float) -> None:
main = f’<div style=“font-size:45px;font-weight:800;color:{COLORS[“dark”]};line-height:1;”>{price:,.2f}</div>’
st.markdown(_card_html(title, main), unsafe_allow_html=True)

# ── 페이지 설정 ────────────────────────────────────────────────────────────────

st.set_page_config(page_title=“ETF Market Watch”, page_icon=“📈”, layout=“wide”)
st.markdown(
‘<style>@import url(“https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap”);’
‘* { font-family: Pretendard, sans-serif; } .main { background-color: #f8f9fa; }</style>’,
unsafe_allow_html=True,
)
st.title(“📈 Market Overview”)

# ── 대시보드 ───────────────────────────────────────────────────────────────────

@st.fragment(run_every=“30s”)
def render_dashboard() -> None:
st.caption(f”⏱ Last synced: {datetime.now(tz=KST).strftime(’%Y-%m-%d %H:%M:%S’)} (KST) | Data: Yahoo Finance”)

```
# Core ETFs
st.subheader("Core ETFs (vs ATH)")
for col, (name, sym) in zip(st.columns(len(ETF_SYMBOLS)), ETF_SYMBOLS.items()):
    with col:
        snap = get_snapshot(sym)
        if snap:
            draw_etf_card(name, snap)
        else:
            st.warning(f"⚠️ {name} 데이터 로드 실패")

st.markdown("---")

# Macro Indicators
st.subheader("Macro Indicators")
for col, (name, sym) in zip(st.columns(len(MACRO_SYMBOLS)), MACRO_SYMBOLS.items()):
    with col:
        price = _fetch_price(sym)
        if price is None:
            st.error(f"❌ {name} 로드 실패")
        elif sym == "^VIX":
            draw_vix_card(name, price)
        else:
            draw_macro_card(name, price)
```

render_dashboard()
