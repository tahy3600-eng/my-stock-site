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

# 2. 매수 시그널 로직
def get_buy_signal(pct):
    if pct <= -30:
        return "STRONG BUY", "#6A0DAD"
    elif pct <= -20:
        return "BUY", "#003049"
    elif pct <= -10:
        return "ACCUMULATE", "#2A9D8F"
    elif pct >= 0:
        return "REBALANCE", "#D62828"
    else:
        return "HOLD", "#6c757d"

# 3. 데이터 수집 함수
@st.cache_data(ttl=3600)
def get_high_info(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="2y")
        if df.empty:
            return None
        return {
            "val": df['High'].max(),
            "date": df['High'].idxmax().strftime('%Y.%m.%d')
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
        return df['Close'].iloc[-1]
    except:
        return 0.0

# 4. 카드 렌더링 함수
def draw_card(title, price, pct=None, sub="", is_vix=False, is_etf=False):
    C_RED, C_BLUE, C_GREEN, C_ORANGE = "#D62828", "#003049", "#2A9D8F", "#F77F00"

    main_display = ""
    sub_display = ""
    footer_html = ""

    if is_etf:
        status_color = C_RED if pct >= 0 else C_BLUE
        signal, s_color = get_buy_signal(pct)

        main_display = f"""
        <div style="font-size:48px; font-weight:800; color:{status_color}; line-height:1;">
        {pct:+.2f}%
        </div>
        """

        sub_display = f"""
        <div style="font-size:20px; font-weight:600; color:#444; margin-top:8px;">
        ${price:,.2f}
        </div>
        """

        if sub:
            footer_html = f"""
            <div style="color:#adb5bd; font-size:11px; margin-top:15px; font-weight:400;">
            ATH {sub}
            </div>
            """

        footer_html += f"""
        <div style="margin-top:12px; font-weight:800; font-size:14px; color:{s_color}; letter-spacing:1px;">
        ● {signal}
        </div>
        """

    elif is_vix:
        if price < 20:
            v_color, v_state = C_GREEN, "STABLE"
        elif price < 30:
            v_color, v_state = C_ORANGE, "CAUTION"
        else:
            v_color, v_state = C_RED, "PANIC"

        main_display = f"""
        <div style="font-size:45px; font-weight:800; color:#212529; line-height:1;">
        {price:,.2f}
        </div>
        """

        footer_html = f"""
        <div style="color:{v_color}; font-size:13px; font-weight:700; margin-top:15px; letter-spacing:1px;">
        ● {v_state}
        </div>
        """

    else:
        main_display = f"""
        <div style="font-size:45px; font-weight:800; color:#212529; line-height:1;">
        {price:,.2f}
        </div>
        """

    html_content = f"""
    <div style="background:white; padding:40px 20px; border-radius:24px;
                box-shadow:0 4px 20px rgba(0,0,0,0.03);
                border:1px solid #f1f3f5;
                text-align:center; margin-bottom:20px;">
        <div style="color:#6c757d; font-size:12px; font-weight:600;
                    letter-spacing:1.2px; margin-bottom:15px;
                    text-transform:uppercase;">
            {title}
        </div>
        {main_display}
        {sub_display}
        {footer_html}
    </div>
    """

    st.markdown(html_content, unsafe_allow_html=True)

def get_kst_now():
    return datetime.utcnow() + timedelta(hours=9)

# 5. 메인 레이아웃
st.title("Market Overview")

@st.fragment(run_every="30s")
def render_dashboard():
    kst_now = get_kst_now().strftime('%Y-%m-%d %H:%M:%S')
    st.caption(f"⏱ Last synced: {kst_now} (KST) | Data: Yahoo Finance")

    # 상단 ETF
    st.subheader("Core ETFs (vs ATH)")
    idx_cols = st.columns(2)

    etfs = {
        "Nasdaq 100 (QQQ)": "QQQ",
        "S&P 500 (VOO)": "VOO"
    }

    for i, (name, sym) in enumerate(etfs.items()):
        ref = get_high_info(sym)
        curr = get_live(sym)

        with idx_cols[i]:
            if ref and curr > 0:
                gap = ((curr - ref['val']) / ref['val']) * 100
                draw_card(
                    name,
                    curr,
                    gap,
                    sub=f"${ref['val']:,.1f} ({ref['date']})",
                    is_etf=True
                )
            else:
                st.warning(f"{name} 데이터를 불러오는 중...")

    st.markdown("---")

    # 하단 매크로 지표
    m_col1, m_col2 = st.columns(2)

    with m_col1:
        usd = get_live("USDKRW=X")
        if usd > 0:
            draw_card("USD / KRW", usd)
        else:
            st.error("환율 로드 실패")

    with m_col2:
        vix = get_live("^VIX")
        if vix > 0:
            draw_card("VIX INDEX", vix, is_vix=True)
        else:
            st.error("VIX 로드 실패")

render_dashboard()
