import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# -------------------------------
# 1. 페이지 설정
# -------------------------------

st.set_page_config(
    page_title="Semiconductor Market Watch",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');

* {
    font-family: 'Pretendard', sans-serif;
}

.main {
    background-color: #f8f9fa;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 2. 캐시 구조
# -------------------------------

@st.cache_resource
def get_ticker(sym):
    return yf.Ticker(sym)


@st.cache_data(ttl=300)
def get_high_info(sym):
    try:
        t = get_ticker(sym)

        # 종가 기준 ATH
        df = t.history(period="10y")

        if df.empty:
            return None

        high = df["Close"].max()
        idx = df["Close"].idxmax()

        return {
            "val": float(high),
            "date": idx.strftime('%Y.%m.%d')
        }

    except Exception as e:
        print(f"{sym} ATH 오류: {e}")
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
                price = (
                    fi.get("lastPrice")
                    or fi.get("regularMarketPrice")
                )

            # fallback
            if not price:
                df = t.history(period="5d")

                if not df.empty:
                    price = df["Close"].iloc[-1]

            result[sym] = float(price) if price else 0.0

        except Exception as e:
            print(f"{sym} 가격 오류: {e}")
            result[sym] = 0.0

    return result


def now_kst():
    return datetime.utcnow() + timedelta(hours=9)


# -------------------------------
# 3. 카드 UI
# -------------------------------

def draw_card(title, price, pct=None, sub="", is_vix=False, is_etf=False):

    C_RED = "#D62828"
    C_BLUE = "#003049"
    C_GREEN = "#2A9D8F"

    main_display = ""
    sub_display = ""
    footer_html = ""

    # ETF 카드
    if is_etf:

        status_color = C_RED if pct >= 0 else C_BLUE

        main_display = f"""
        <div style="
            font-size:48px;
            font-weight:800;
            color:{status_color};
            line-height:1;
        ">
            {pct:+.2f}%
        </div>
        """

        sub_display = f"""
        <div style="
            font-size:20px;
            font-weight:600;
            color:#444;
            margin-top:8px;
        ">
            ${price:,.2f}
        </div>
        """

        if sub:
            footer_html = f"""
            <div style="
                color:#adb5bd;
                font-size:11px;
                margin-top:15px;
            ">
                ATH {sub}
            </div>
            """

    # Macro 카드
    else:

        color = "#212529"

        # VIX 색상 처리
        if is_vix:

            if price >= 25:
                color = C_RED
            elif price <= 15:
                color = C_GREEN

        main_display = f"""
        <div style="
            font-size:45px;
            font-weight:800;
            color:{color};
        ">
            {price:,.2f}
        </div>
        """

    html = f"""
    <div style="
        background:white;
        padding:24px 14px;
        border-radius:24px;
        box-shadow:0 4px 20px rgba(0,0,0,0.03);
        border:1px solid #f1f3f5;
        text-align:center;
        margin-bottom:20px;
    ">
        <div style="
            color:#6c757d;
            font-size:12px;
            font-weight:600;
            letter-spacing:1.2px;
            margin-bottom:15px;
        ">
            {title}
        </div>

        {main_display}

        {sub_display}

        {footer_html}
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


# -------------------------------
# 4. 메인
# -------------------------------

st.title("Semiconductor Market Watch")


@st.fragment(run_every="30s")
def dashboard():

    st.caption(
        f"⏱ Last synced: {now_kst().strftime('%Y-%m-%d %H:%M:%S')} (KST) | Data: Yahoo Finance"
    )

    # -------------------------------
    # ETF
    # -------------------------------

    etfs = {
        "SOXX (1x)": "SOXX",
        "USD (2x)": "USD"
    }

    # -------------------------------
    # Macro
    # -------------------------------

    macro = {
        "USD / KRW": "USDKRW=X",
        "VIX INDEX": "^VIX"
    }

    symbols = list(etfs.values()) + list(macro.values())

    prices = get_prices(symbols)

    # -------------------------------
    # ETF Section
    # -------------------------------

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

                draw_card(
                    title=name,
                    price=curr,
                    pct=gap,
                    sub=f"${ref['val']:,.1f} ({ref['date']})",
                    is_etf=True
                )

            else:
                st.warning(f"{name} 데이터 지연")

    st.markdown("---")

    # -------------------------------
    # Macro Section
    # -------------------------------

    col1, col2 = st.columns(2)

    # 환율
    with col1:

        p = prices["USDKRW=X"]

        if p:
            draw_card("USD / KRW", p)
        else:
            st.error("환율 데이터 오류")

    # VIX
    with col2:

        p = prices["^VIX"]

        if p:
            draw_card(
                "VIX INDEX",
                p,
                is_vix=True
            )
        else:
            st.error("VIX 데이터 오류")


dashboard()
