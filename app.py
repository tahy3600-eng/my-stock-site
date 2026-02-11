import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="Market Dashboard", page_icon="📈", layout="wide")

# 전역 스타일 설정
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    * { font-family: 'Pretendard', sans-serif; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 수집 함수 (캐싱)
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
        prev = df['Close'].iloc[-2]
        return curr, ((curr - prev) / prev) * 100
    except: return 0.0, 0.0

# 3. 카드 렌더링 함수
def draw_card(title, price, pct=None, sub="", is_vix=False):
    RED, BLUE, GREEN = "#D62828", "#003049", "#2A9D8F"
    pct_html = ""
    sub_html = ""
    
    if is_vix:
        vix_color = GREEN if price < 20 else RED
        vix_state = "STABLE" if price < 20 else "RISKY"
        sub_html = f'<div style="color:{vix_color}; font-size:12px; font-weight:700; margin-top:15px;">● {vix_state}</div>'
    elif pct is not None:
        p_color = RED if pct >= 0 else BLUE
        pct_html = f'<div style="font-size:20px; font-weight:800; color:{p_color};">{pct:+.2f}%</div>'
        if sub:
            sub_html = f'<div style="color:#adb5bd; font-size:11px; margin-top:15px;">{sub}</div>'
    
    html = f"""<div style="background:white; padding:35px 20px; border-radius:24px; box-shadow:0 10px 30px rgba(0,0,0,0.02); border:1px solid #f1f3f5; text-align:center; margin-bottom:20px;"><div style="color:#6c757d; font-size:13px; font-weight:600; letter-spacing:1px; margin-bottom:10px; text-transform:uppercase;">{title}</div><div style="font-size:40px; font-weight:800; color:#212529; letter-spacing:-1px; margin-bottom:5px;">{price:,.2f}</div>{pct_html}{sub_html}</div>"""
    st.markdown(html, unsafe_allow_html=True)

# 4. 대시보드 레이아웃
st.title("Market Overview")

# 헬퍼 함수: 항상 한국 시간을 반환
def get_kst_now():
    return datetime.utcnow() + timedelta(hours=9)

@st.fragment(run_every="10s")
def render():
    # 업데이트 시간 표기 수정
    kst_now = get_kst_now().strftime('%H:%M:%S')
    st.caption(f"⏱ Last synced: {kst_now} (KST)")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- 상단: 3대 지수 ---
    idx_cols = st.columns(3)
    indices = {"Nasdaq 100": "^NDX", "S&P 500": "^GSPC", "Dow Jones": "^DJI"}
    
    for i, (name, sym) in enumerate(indices.items()):
        ref = get_high_info(sym)
        curr, _ = get_live(sym)
        gap = ((curr - ref['val']) / ref['val']) * 100 if ref else 0
        with idx_cols[i]:
            draw_card(name, curr, gap, sub=f"ATH {ref['val']:,.0f} ({ref['date']})")

    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

    # --- 하단: 매크로 지표 ---
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        usd, _ = get_live("USDKRW=X")
        draw_card("USD / KRW", usd)
    with m_col2:
        vix, _ = get_live("^VIX")
        draw_card("VIX INDEX", vix, is_vix=True)

render()
