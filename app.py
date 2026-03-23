import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# -------------------------------
# 1. 페이지 설정
# -------------------------------
st.set_page_config(page_title="ETF Market Watch", page_icon="📈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
* { font-family: 'Pretendard', sans-serif; }
.main { background-color: #f8f9fa; }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 2. 캐시 구조 (수정 핵심)
# -------------------------------

@st.cache_resource
def get_ticker(sym):
    return yf.Ticker(sym)


@st.cache_data(ttl=300)
def get_high_info(sym):
    try:
        t = get_ticker(sym)
        df = t.history(period="2y")

        if df.empty:
            return None

        high = df["High"].max()
        idx = df["High"].idxmax()

        return {
            "val": float(high),
            "date": idx.strftime('%Y.%m.%d')
        }
    except:
        return None


@st.cache_data(ttl=60)
def get_prices(symbols):
    result = {}

    for sym in symbols:
        try:
            t = get_ticker(sym)
            price = None

            fi = getattr(t, "fast_info", None)
            if fi:
                price = fi.get("lastPrice")

            if not price:
                df = t.history(period="5d")
                if not df.empty:
                    price = df["Close"].iloc[-1]

            result[sym] = float(price) if price else 0.0

        except:
            result[sym] = 0.0

    return result


def now_kst():
    return datetime.utcnow() + timedelta(hours=9)


# -------------------------------
# 3. UI (변경 없음)
# -------------------------------

def draw_card(title, price, pct=None, sub="", is_vix=False, is_etf=False):
    C_RED, C_BLUE, C_GREEN, C_ORANGE = "#D62828", "#003049", "#2A9D8F", "#F77F00"

    main_display = ""
    sub_display = ""
    footer_html = ""

    if is_etf:
        status_color = C_RED if pct >= 0 else C_BLUE

        main_display = f'<div style="font-size:48px; font-weight:800; color:{status_color}; line-height:1;">{pct:+.2f}%</div>'
        sub_display = f'<div style="font-size:20px; font-weight:600; color:#444; margin-top:8px;">${price:,.2f}</div>'

        if sub:
            footer_html = f'<div style="color:#adb5bd; font-size:11px; margin-top:15px;">ATH {sub}</div>'

    elif is_vix:
        v_color, v_state = (C_GREEN, "STABLE") if price < 20 else (C_ORANGE, "CAUTION") if price < 30 else (C_RED, "PANIC")

        main_display = f'<div style="font-size:45px; font-weight:800; color:#212529;">{price:,.2f}</div>'
        footer_html = f'<div style="color:{v_color}; font-size:13px; font-weight:700; margin-top:15px;">● {v_state}</div>'

    else:
        main_display = f'<div style="font-size:45px; font-weight:800; color:#212529;">{price:,.2f}</div>'

    html = f"""
    <div style="background:white; padding:40px 20px; border-radius:24px;
    box-shadow:0 4px 20px rgba(0,0,0,0.03); border:1px solid #f1f3f5;
    text-align:center; margin-bottom:20px;">
        <div style="color:#6c757d; font-size:12px; font-weight:600;
        letter-spacing:1.2px; margin-bottom:15px;">{title}</div>
        {main_display}
        {sub_display}
        {footer_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# -------------------------------
# 4. 메인
# -------------------------------

st.title("Market Overview")

@st.fragment(run_every="30s")
def dashboard():

    st.caption(f"⏱ Last synced: {now_kst().strftime('%Y-%m-%d %H:%M:%S')} (KST) | Data: Yahoo Finance")

    etfs = {
        "Nasdaq 100 (QQQ)": "QQQ",
        "S&P 500 (VOO)": "VOO"
    }

    macro = {
        "USD / KRW": "USDKRW=X",
        "VIX INDEX": "^VIX"
    }

    symbols = list(etfs.values()) + list(macro.values())

    prices = get_prices(symbols)

    # ETF
    st.subheader("Core ETFs (vs ATH)")
    cols = st.columns(len(etfs))

    for i, (name, sym) in enumerate(etfs.items()):
        ref = get_high_info(sym)
        curr = prices[sym]

        with cols[i]:
            if ref and curr > 0:
                gap = (curr - ref["val"]) / ref["val"] * 100
                draw_card(name, curr, gap, sub=f"${ref['val']:,.1f} ({ref['date']})", is_etf=True)
            else:
                st.warning(f"{name} 데이터 지연")

    st.markdown("---")

    # Macro
    col1, col2 = st.columns(2)

    with col1:
        p = prices["USDKRW=X"]
        draw_card("USD / KRW", p) if p else st.error("환율 오류")

    with col2:
        p = prices["^VIX"]
        draw_card("VIX INDEX", p, is_vix=True) if p else st.error("VIX 오류")


dashboard()
