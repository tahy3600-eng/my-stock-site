import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="Minimal Market", page_icon="📈", layout="wide")

# 전역 스타일 설정 (폰트 및 배경)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #fcfcfc; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 수집 로직 (캐싱)
@st.cache_data(ttl=3600)
def get_high_ref(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="1y")
        return {"high": df['High'].max(), "date": df['High'].idxmax().strftime('%Y.%m.%d')}
    except: return None

def get_live(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="2d")
        curr = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        return curr, ((curr - prev) / prev) * 100
    except: return 0.0, 0.0

# 3. 직관적인 미니멀 카드 함수
def draw_card(title, price, pct=None, sub="", is_vix=False):
    # 색상 정의
    color_red = "#E63946" # 부드러운 빨강
    color_blue = "#457B9D" # 차분한 파랑
    color_green = "#2A9D8F" # 안정적인 초록
    
    main_color = "#333"
    pct_html = ""
    
    if is_vix:
        status_color = color_green if price < 20 else color_red
        status_text = "STABLE" if price < 20 else "VOLATILE"
        sub = f"<span style='color:{status_color}; font-weight:bold;'>● {status_text}</span>"
    elif pct is not None:
        main_color = color_red if pct >= 0 else color_blue
        pct_html = f'<div style="font-size: 20px; font-weight: 700; color:{main_color};">{pct:+.2f}%</div>'

    st.markdown(f"""
        <div style="
            background: white; 
            padding: 30px 20px; 
            border-radius: 20px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            border: 1px solid #f0f0f0;
            text-align: center;
            margin-bottom: 20px;
        ">
            <div style="color: #888; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">{title}</div>
            <div style="font-size: 36px; font-weight: 800; color: #222; margin-bottom: 5px;">{price:,.2f}</div>
            {pct_html}
            <div style="color: #bbb; font-size: 11px; margin-top: 15px;">{sub}</div>
        </div>
    """, unsafe_allow_html=True)

# 4. 레이아웃 구성
st.title("Market Overview")
st.caption(f"Last sync: {datetime.now().strftime('%H:%M:%S')} (KST)")
st.markdown("---")

@st.fragment(run_every="10s")
def render():
    # --- 지수 섹션 ---
    col1, col2, col3 = st.columns(3)
    indices = {"NASDAQ 100": "^NDX", "S&P 500": "^GSPC", "DOW JONES": "^DJI"}
    
    for i, (name, sym) in enumerate(indices.items()):
        ref = get_high_ref(sym)
        curr, _ = get_live(sym)
        gap = ((curr - ref['high']) / ref['high']) * 100 if ref else 0
        with [col1, col2, col3][i]:
            draw_card(name, curr, gap, f"ATH: {ref['high']:,.0f} ({ref['date']})")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 매크로 섹션 ---
    col_l, col_r = st.columns(2)
    
    with col_l:
        usd, _ = get_live("USDKRW=X")
        draw_card("USDKRW", usd)
        
    with col_r:
        vix, _ = get_live("^VIX")
        draw_card("VIX INDEX", vix, is_vix=True)

render()
