import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="Pro-Market Dashboard", page_icon="📈", layout="wide")

# 전역 스타일 설정
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    * { font-family: 'Pretendard', sans-serif; }
    .main { background-color: #fcfcfc; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 수집 함수
@st.cache_data(ttl=3600)
def get_high_info(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="1y")
        return {"val": df['High'].max(), "date": df['High'].idxmax().strftime('%Y.%m.%d')}
    except: return None

def get_live(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="2d")
        curr = df['Close'].iloc[-1]
        return curr
    except: return 0.0

# 3. 강화된 카드 렌더링 함수
def draw_card(title, price, pct=None, sub="", is_vix=False, is_index=False):
    # 색상 팔레트
    C_RED, C_BLUE, C_GREEN, C_ORANGE = "#D62828", "#003049", "#2A9D8F", "#F77F00"
    
    main_display = ""
    sub_display = ""
    card_color = "#333"

    if is_index:
        # 지수 카드 로직: 퍼센트(%)를 크게, 수치를 작게
        card_color = C_RED if pct >= 0 else C_BLUE
        main_display = f'<div style="font-size:48px; font-weight:800; color:{card_color};">{pct:+.2f}%</div>'
        sub_display = f'<div style="font-size:22px; font-weight:600; color:#444; margin-top:5px;">{price:,.2f}</div>'
        footer = f'<div style="color:#adb5bd; font-size:11px; margin-top:15px;">{sub}</div>'
    
    elif is_vix:
        # VIX 3단계 로직
        if price < 20:
            v_color, v_state = C_GREEN, "STABLE"
        elif price < 30:
            v_color, v_state = C_ORANGE, "CAUTION"
        else:
            v_color, v_state = C_RED, "PANIC"
        
        main_display = f'<div style="font-size:45px; font-weight:800; color:#212529;">{price:,.2f}</div>'
        footer = f'<div style="color:{v_color}; font-size:12px; font-weight:700; margin-top:15px;">● {v_state}</div>'
    
    else:
        # 환율 카드 로직 (심플하게 수치만)
        main_display = f'<div style="font-size:45px; font-weight:800; color:#212529;">{price:,.2f}</div>'
        footer = ""

    html = f"""
    <div style="background:white; padding:35px 20px; border-radius:24px; box-shadow:0 10px 30px rgba(0,0,0,0.02); border:1px solid #f1f3f5; text-align:center; margin-bottom:20px;">
        <div style="color:#6c757d; font-size:13px; font-weight:600; letter-spacing:1px; margin-bottom:10px; text-transform:uppercase;">{title}</div>
        {main_display}
        {sub_display}
        {footer}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# 4. 레이아웃
st.title("Market Overview")

def get_kst_now():
    return datetime.utcnow() + timedelta(hours=9)

@st.fragment(run_every="10s")
def render():
    kst_now = get_kst_now().strftime('%H:%M:%S')
    st.caption(f"⏱ Last synced: {kst_now} (KST)")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- 상단: 3대 지수 (전고점 대비 상태 표시) ---
    idx_cols = st.columns(3)
    indices = {"Nasdaq 100": "^NDX", "S&P 500": "^GSPC", "Dow Jones": "^DJI"}
    
    for i, (name, sym) in enumerate(indices.items()):
        ref = get_high_info(sym)
        curr = get_live(sym)
        if ref and curr > 0:
            gap = ((curr - ref['val']) / ref['val']) * 100
            with idx_cols[i]:
                draw_card(name, curr, gap, sub=f"ATH {ref['val']:,.0f} ({ref['date']})", is_index=True)

    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

    # --- 하단: 매크로 지표 ---
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        usd = get_live("USDKRW=X")
        draw_card("USD / KRW", usd)
    with m_col2:
        vix = get_live("^VIX")
        draw_card("VIX INDEX", vix, is_vix=True)

render()
