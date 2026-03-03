import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="ETF Market Watch", page_icon="📈", layout="wide")

# -------------------------
# 매수 시그널
# -------------------------
def get_buy_signal(pct):
    if pct <= -30:
        return "STRONG BUY"
    elif pct <= -20:
        return "BUY"
    elif pct <= -10:
        return "ACCUMULATE"
    elif pct >= 0:
        return "REBALANCE"
    else:
        return "HOLD"

# -------------------------
# 데이터
# -------------------------
@st.cache_data(ttl=3600)
def get_high_info(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="2y")
        if df.empty:
            return None
        return {
            "val": df["High"].max(),
            "date": df["High"].idxmax().strftime("%Y.%m.%d")
        }
    except:
        return None

@st.cache_data(ttl=30)
def get_live(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="5d")
        if df.empty:
            return 0.0
        return df["Close"].iloc[-1]
    except:
        return 0.0

def get_kst_now():
    return datetime.utcnow() + timedelta(hours=9)

# -------------------------
# 화면
# -------------------------
st.title("Market Overview")

@st.fragment(run_every="30s")
def render_dashboard():

    kst_now = get_kst_now().strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"⏱ Last synced: {kst_now} (KST) | Data: Yahoo Finance")

    st.subheader("Core ETFs (vs ATH)")
    col1, col2 = st.columns(2)

    etfs = {
        "Nasdaq 100 (QQQ)": "QQQ",
        "S&P 500 (VOO)": "VOO"
    }

    for i, (name, sym) in enumerate(etfs.items()):
        ref = get_high_info(sym)
        curr = get_live(sym)

        with (col1 if i == 0 else col2):
            if ref and curr > 0:
                gap = ((curr - ref["val"]) / ref["val"]) * 100
                signal = get_buy_signal(gap)

                st.metric(
                    label=name,
                    value=f"${curr:,.2f}",
                    delta=f"{gap:+.2f}% vs ATH"
                )

                st.caption(f"ATH ${ref['val']:,.1f} ({ref['date']})")

                if signal == "STRONG BUY":
                    st.error(f"● {signal}")
                elif signal == "BUY":
                    st.warning(f"● {signal}")
                elif signal == "ACCUMULATE":
                    st.success(f"● {signal}")
                elif signal == "REBALANCE":
                    st.info(f"● {signal}")
                else:
                    st.write(f"● {signal}")
            else:
                st.warning("데이터 로딩 중...")

    st.markdown("---")

    m1, m2 = st.columns(2)

    with m1:
        usd = get_live("USDKRW=X")
        if usd > 0:
            st.metric("USD / KRW", f"{usd:,.2f}")
        else:
            st.error("환율 로드 실패")

    with m2:
        vix = get_live("^VIX")
        if vix > 0:
            st.metric("VIX INDEX", f"{vix:,.2f}")

            if vix < 20:
                st.success("● STABLE")
            elif vix < 30:
                st.warning("● CAUTION")
            else:
                st.error("● PANIC")
        else:
            st.error("VIX 로드 실패")

render_dashboard()
