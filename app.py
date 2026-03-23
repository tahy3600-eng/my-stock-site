import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="ETF Market Watch", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    * { font-family: 'Pretendard', sans-serif; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 수집 함수 (안정성 개선)
@st.cache_data(ttl=300)  # 5분 캐시 (기존 1시간 → 너무 김)
def get_high_info(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="2y")

        if df is None or df.empty:
            return None

        high_val = df['High'].max()
        high_date = df['High'].idxmax().strftime('%Y.%m.%d')

        return {"val": high_val, "date": high_date}
    except Exception as e:
        return None


def get_live(symbol):
    try:
        t = yf.Ticker(symbol)

        # 1순위: fast_info (가장 안정적)
        if hasattr(t, "fast_info") and "lastPrice" in t.fast_info:
            price = t.fast_info["lastPrice"]
            if price and price > 0:
                return float(price)

        # 2순위: 최근 종가 fallback
        df = t.history(period="5d")

        if df is None or df.empty:
            return 0.0

        return float(df['Close'].iloc[-1])

    except Exception as e:
        return 0.0


# 3. 카드 UI
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

    html_content = f"""
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

    st.markdown(html_content, unsafe_allow_html=True)


def get_kst_now():
    return datetime.utcnow() + timedelta(hours=9)


# 4. 메인 UI
st.title("Market Overview")

@st.fragment(run_every="30s")
def render_dashboard():

    kst_now = get_kst_now().strftime('%Y-%m-%d %H:%M:%S')
    st.caption(f"⏱ Last synced: {kst_now} (KST) | Data: Yahoo Finance")

    # --- ETF ---
    st.subheader("Core ETFs (vs ATH)")
    cols = st.columns(2)

    etfs = {
        "Nasdaq 100 (QQQ)": "QQQ",
        "S&P 500 (VOO)": "VOO"
    }

    for i, (name, sym) in enumerate(etfs.items()):
        ref = get_high_info(sym)
        curr = get_live(sym)

        with cols[i]:
            if ref is not None and curr > 0:
                gap = ((curr - ref['val']) / ref['val']) * 100
                draw_card(name, curr, gap, sub=f"${ref['val']:,.1f} ({ref['date']})", is_etf=True)
            else:
                st.warning(f"{name} 데이터 지연 (Yahoo API)")

    st.markdown("---")

    # --- 매크로 ---
    col1, col2 = st.columns(2)

    with col1:
        usd = get_live("USDKRW=X")
        if usd > 0:
            draw_card("USD / KRW", usd)
        else:
            st.error("환율 데이터 실패")

    with col2:
        vix = get_live("^VIX")
        if vix > 0:
            draw_card("VIX INDEX", vix, is_vix=True)
        else:
            st.error("VIX 데이터 실패")


render_dashboard()
