import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# -------------------------------------------------
# 페이지 설정
# -------------------------------------------------

st.set_page_config(
    page_title="Semiconductor Market Watch",
    page_icon="📈",
    layout="wide"
)

# -------------------------------------------------
# CSS 스타일
# -------------------------------------------------

st.markdown("""
<style>

html, body, [class*="css"]  {
    background-color: #f8f9fa;
}

.card {
    background: white;
    padding: 24px;
    border-radius: 22px;
    border: 1px solid #e9ecef;
    box-shadow: 0 4px 16px rgba(0,0,0,0.04);
    text-align: center;
    margin-bottom: 20px;
}

.card-title {
    color: #6c757d;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1px;
    margin-bottom: 16px;
}

.big-number {
    font-size: 48px;
    font-weight: 800;
    line-height: 1;
}

.sub-number {
    font-size: 20px;
    font-weight: 600;
    color: #444;
    margin-top: 10px;
}

.footer-text {
    color: #adb5bd;
    font-size: 11px;
    margin-top: 14px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 캐시
# -------------------------------------------------

@st.cache_resource
def get_ticker(sym):
    return yf.Ticker(sym)


@st.cache_data(ttl=300)
def get_high_info(sym):

    try:
        ticker = get_ticker(sym)

        # 종가 기준 ATH
        df = ticker.history(period="10y")

        if df.empty:
            return None

        high = df["Close"].max()
        idx = df["Close"].idxmax()

        return {
            "val": float(high),
            "date": idx.strftime("%Y.%m.%d")
        }

    except Exception:
        return None


@st.cache_data(ttl=60)
def get_prices(symbols):

    result = {}

    for sym in symbols:

        try:
            ticker = get_ticker(sym)

            price = None

            fi = getattr(ticker, "fast_info", None)

            if fi:
                price = (
                    fi.get("lastPrice")
                    or fi.get("regularMarketPrice")
                )

            # fallback
            if not price:

                df = ticker.history(period="5d")

                if not df.empty:
                    price = df["Close"].iloc[-1]

            result[sym] = float(price) if price else 0.0

        except Exception:
            result[sym] = 0.0

    return result


def now_kst():
    return datetime.utcnow() + timedelta(hours=9)


# -------------------------------------------------
# ETF 카드
# -------------------------------------------------

def draw_etf_card(title, pct, price, ath):

    color = "#D62828" if pct >= 0 else "#003049"

    html = f"""
    <div class="card">

        <div class="card-title">
            {title}
        </div>

        <div class="big-number" style="color:{color};">
            {pct:+.2f}%
        </div>

        <div class="sub-number">
            ${price:,.2f}
        </div>

        <div class="footer-text">
            ATH {ath}
        </div>

    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


# -------------------------------------------------
# 매크로 카드
# -------------------------------------------------

def draw_macro_card(title, value, is_vix=False):

    color = "#212529"

    if is_vix:

        if value >= 25:
            color = "#D62828"

        elif value <= 15:
            color = "#2A9D8F"

    html = f"""
    <div class="card">

        <div class="card-title">
            {title}
        </div>

        <div class="big-number" style="color:{color};">
            {value:,.2f}
        </div>

    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


# -------------------------------------------------
# 메인 타이틀
# -------------------------------------------------

st.title("📈 Semiconductor Market Watch")

st.caption(
    f"Last synced: {now_kst().strftime('%Y-%m-%d %H:%M:%S')} (KST)"
)

# -------------------------------------------------
# ETF 목록
# -------------------------------------------------

etfs = {
    "SOXX (1x)": "SOXX",
    "USD (2x)": "USD"
}

# -------------------------------------------------
# 매크로 지표
# -------------------------------------------------

macro = {
    "USD / KRW": "USDKRW=X",
    "VIX INDEX": "^VIX"
}

symbols = list(etfs.values()) + list(macro.values())

prices = get_prices(symbols)

# -------------------------------------------------
# ETF 섹션
# -------------------------------------------------

st.subheader("Semiconductor ETFs (vs ATH)")

cols = st.columns(len(etfs))

for i, (name, sym) in enumerate(etfs.items()):

    ref = get_high_info(sym)
    curr = prices[sym]

    with cols[i]:

        if ref and curr > 0:

            gap = (
                (curr - ref["val"])
                / ref["val"]
                * 100
            )

            draw_etf_card(
                title=name,
                pct=gap,
                price=curr,
                ath=f"${ref['val']:,.1f} ({ref['date']})"
            )

        else:
            st.error(f"{name} 데이터 오류")

# -------------------------------------------------
# 구분선
# -------------------------------------------------

st.markdown("---")

# -------------------------------------------------
# Macro 섹션
# -------------------------------------------------

st.subheader("Macro")

col1, col2 = st.columns(2)

# 환율
with col1:

    usdkrw = prices["USDKRW=X"]

    if usdkrw:
        draw_macro_card(
            title="USD / KRW",
            value=usdkrw
        )
    else:
        st.error("환율 데이터 오류")

# VIX
with col2:

    vix = prices["^VIX"]

    if vix:
        draw_macro_card(
            title="VIX INDEX",
            value=vix,
            is_vix=True
        )
    else:
        st.error("VIX 데이터 오류")
