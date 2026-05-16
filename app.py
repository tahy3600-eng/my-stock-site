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
# 데이터 함수
# -------------------------------------------------

@st.cache_data(ttl=300)
def get_high_info(sym):
    try:
        ticker = yf.Ticker(sym)
        df = ticker.history(period="10y")

        if df.empty:
            return None

        high = df["Close"].max()
        idx = df["Close"].idxmax()

        return {
            "val": float(high),
            "date": idx.strftime("%Y.%m.%d")
        }

    except Exception as e:
        st.warning(f"{sym} ATH 조회 오류: {e}")
        return None


@st.cache_data(ttl=60)
def get_prices(symbols):
    result = {}

    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            price = None

            fi = getattr(ticker, "fast_info", None)

            if fi:
                price = (
                    getattr(fi, "last_price", None)
                    or getattr(fi, "regular_market_price", None)
                )

            if not price:
                df = ticker.history(period="5d")
                if not df.empty:
                    price = df["Close"].iloc[-1]

            result[sym] = float(price) if price else 0.0

        except Exception as e:
            st.warning(f"{sym} 가격 조회 오류: {e}")
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
    <div style="
        background:white;
        padding:24px;
        border-radius:20px;
        border:1px solid #e9ecef;
        box-shadow:0 4px 16px rgba(0,0,0,0.04);
        text-align:center;
        margin-bottom:20px;
    ">
        <div style="
            color:#6c757d;
            font-size:26px;
            font-weight:600;
            letter-spacing:1px;
            margin-bottom:16px;
        ">
            {title}
        </div>

        <div style="
            font-size:48px;
            font-weight:800;
            color:{color};
            line-height:1;
        ">
            {pct:+.2f}%
        </div>

        <div style="
            font-size:20px;
            font-weight:600;
            color:#444;
            margin-top:10px;
        ">
            ${price:,.2f}
        </div>

        <div style="
            color:#adb5bd;
            font-size:11px;
            margin-top:14px;
        ">
            ATH {ath}
        </div>
    </div>
    """

    st.html(html)


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
    <div style="
        background:white;
        padding:24px;
        border-radius:20px;
        border:1px solid #e9ecef;
        box-shadow:0 4px 16px rgba(0,0,0,0.04);
        text-align:center;
        margin-bottom:20px;
    ">
        <div style="
            color:#6c757d;
            font-size:13px;
            font-weight:600;
            letter-spacing:1px;
            margin-bottom:16px;
        ">
            {title}
        </div>

        <div style="
            font-size:48px;
            font-weight:800;
            color:{color};
            line-height:1;
        ">
            {value:,.2f}
        </div>
    </div>
    """

    st.html(html)


# -------------------------------------------------
# 메인
# -------------------------------------------------

st.title("📈 Semiconductor Market Watch")

st.caption(
    f"Last synced: {now_kst().strftime('%Y-%m-%d %H:%M:%S')} (KST)"
)

# -------------------------------------------------
# ETF / Macro 목록
# -------------------------------------------------

etfs = {
    "SOXX": "SOXX",
    "USD": "USD",
    "QQQ": "QQQ",
    "QLD": "QLD"
}

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
            gap = (curr - ref["val"]) / ref["val"] * 100

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

with col1:
    usdkrw = prices["USDKRW=X"]
    if usdkrw:
        draw_macro_card(title="USD / KRW", value=usdkrw)

with col2:
    vix = prices["^VIX"]
    if vix:
        draw_macro_card(title="VIX INDEX", value=vix, is_vix=True)
