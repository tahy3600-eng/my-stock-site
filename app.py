import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# 1. 페이지 설정 및 전역 스타일
st.set_page_config(page_title="Market Overview", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    * { font-family: 'Pretendard', sans-serif; }
    .main { background-color: #f8f9fa; }
    [data-testid="column"] { padding: 0 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 수집 함수
@st.cache_data(ttl=3600)
def get_high_info(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="1y")
        if df.empty: return None
        return {"val": df['High'].max(), "date": df['High'].idxmax().strftime('%Y.%m.%d')}
    except: return None

def get_live(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="2d")
        if df.empty: return 0.0
        return df['Close'].iloc[-1]
    except: return 0.0

# 3. 카드 렌더링 함수 (태그 노출 방지 로직 적용)
def draw_card(title, price, pct=None, sub="", is_vix=False, is_index=False):
    # 색상 상수
    C_RED, C_BLUE, C_GREEN, C_ORANGE = "#D62828", "#003049", "#2A9D8F", "#F77F00"
    
    main_display = ""
    sub_display = ""
    footer_html = ""

    if is_index:
        # 지수 카드: 퍼센트(%)가 메인, 수치가 서브
        # 현재가가 전고점보다 높거나 같으면 빨강(신고가), 낮으면 파랑
        status_color = C_RED if pct >= 0 else C_BLUE
        main_display = f'<div style="font-size:48px; font-weight:800; color:{status_color}; line-height:1;">{pct:+.2f}%</div>'
        sub_display = f'<div style="font-size:20px; font-weight:600; color:#444; margin-top:8px;">{price:,.2f}</div>'
        if sub:
            footer_html = f'<div style="color:#adb5bd; font-size:11px; margin-top:15px; font-weight:400;">ATH {sub}</div>'
    
    elif is_vix:
        # VIX: 3단계 상태 로직
        if price < 20:
            v_color, v_state = C_GREEN, "STABLE"
        elif price < 30:
            v_color, v_state = C_ORANGE, "CAUTION"
        else:
            v_color, v_state = C_RED, "PANIC"
        
        main_display = f'<div style="font-size:45px; font-weight:800; color:#212529; line-height:1;">{price:,.2f}</div>'
        footer_html = f'<div style="color:{v_color}; font-size:13px; font-weight:700; margin-top:15px; letter-spacing:1px;">● {v_state}</div>'
    
    else:
        # 환율 등 기타 매크로
        main_display = f'<div style="font-size:45px; font-weight:800; color:#212529; line-height:1;">{price:,.2f}</div>'

    # 모든 HTML을 들여쓰기 없는 단일 문자열로 결합 (마크다운 버그 방지 핵심)
    html_content = (
        f'<div style="background:white; padding:40px 20px; border-radius:24px; '
        f'box-shadow:0 4px 20px rgba(0,0,0,0.03); border:1px solid #f1f3f5; '
        f'text-align:center; margin-bottom:20px;">'
        f'<div style="color:#6c757d; font-size:12px; font-weight:600; '
        f'letter-spacing:1.2px; margin-bottom:15px; text-transform:uppercase;">{title}</div>'
        f'{main_display}{sub_display}{footer_html}</div>'
    )
    
    st.markdown(html_content, unsafe_allow_html=True)

# 4. 한국 시간 헬퍼 함수
def get_kst_now():
    return datetime.utcnow() + timedelta(hours=9)

# 5. 메인 레이아웃
st.title("Market Overview")

@st.fragment(run_every="10s")
def render_dashboard():
    # 시간 표시 (KST)
    kst_now = get_kst_now().strftime('%H:%M:%S')
    st.caption(f"⏱ Last synced: {kst_now} (KST)")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- 상단: 3대 지수 섹션 ---
    idx_cols = st.columns(3)
    indices = {"Nasdaq 100": "^NDX", "S&P 500": "^GSPC", "Dow Jones": "^DJI"}
    
    for i, (name, sym) in enumerate(indices.items()):
        ref = get_high_info(sym)
        curr = get_live(sym)
        if ref and curr > 0:
            gap = ((curr - ref['val']) / ref['val']) * 100
            with idx_cols[i]:
                draw_card(name, curr, gap, sub=f"{ref['val']:,.0f} ({ref['date']})", is_index=True)

    st.markdown("<div style='margin: 15px 0;'></div>", unsafe_allow_html=True)

    # --- 하단: 매크로 지표 섹션 ---
    m_col1, m_col2 = st.columns(2)
    
    with m_col1:
        usd = get_live("USDKRW=X")
        draw_card("USD / KRW", usd)
        
    with m_col2:
        vix = get_live("^VIX")
        draw_card("VIX INDEX", vix, is_vix=True)

# 실행
render_dashboard()
