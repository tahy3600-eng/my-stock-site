import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(
    page_title="Market Dashboard",
    page_icon="📊",
    layout="wide"
)

# 2. 데이터 처리 로직
@st.cache_data(ttl=3600)
def get_high_reference(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1y")
        if df.empty: return None
        high_val = df['High'].max()
        high_date = df['High'].idxmax().strftime('%Y-%m-%d') # 날짜 포맷팅
        return {"high": high_val, "date": high_date}
    except:
        return None

def get_live_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="2d")
        if df.empty: return 0.0, 0.0, 0.0
        current = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        change = current - prev_close
        pct_change = (change / prev_close) * 100
        return current, change, pct_change
    except:
        return 0.0, 0.0, 0.0

# 3. UI 컴포넌트 함수
def draw_metric_card(title, price, change_pct, sub_text="", is_vix=False):
    if is_vix:
        color = "#008000" if price < 20 else "#FF4B4B"
    else:
        color = "#FF4B4B" if change_pct >= 0 else "#0000FF"
    
    st.markdown(f"""
        <div style="
            background-color: #ffffff; padding: 25px; border-radius: 15px;
            border-top: 5px solid {color}; box-shadow: 2px 2px 12px rgba(0,0,0,0.08);
            margin-bottom: 20px; text-align: center;
        ">
            <h4 style="margin: 0; color: #666; font-size: 18px;">{title}</h4>
            <h2 style="margin: 15px 0 5px 0; color: #333; font-size: 42px; font-weight: 800;">{price:,.2f}</h2>
            <p style="margin: 0; font-weight: bold; font-size: 24px; color: {color};">{change_pct:+.2f}%</p>
            <p style="margin: 15px 0 0 0; color: #999; font-size: 13px;">{sub_text}</p>
        </div>
    """, unsafe_allow_html=True)

# 4. 메인 대시보드 레이아웃
st.title("📈 Market Index Real-time")
st.markdown("<br>", unsafe_allow_html=True)

@st.fragment(run_every="10s")
def render_dashboard():
    now = (datetime.utcnow() + timedelta(hours=9)).strftime('%H:%M:%S')
    
    # --- 구역 1: 3대 지수 ---
    st.subheader("🏦 Major Market Index")
    idx_cols = st.columns(3)
    indices = {"Nasdaq 100": "^NDX", "S&P 500": "^GSPC", "Dow Jones": "^DJI"}
    
    for i, (name, sym) in enumerate(indices.items()):
        ref = get_high_reference(sym)
        current_price, _, _ = get_live_data(sym)
        if ref and current_price > 0:
            gap_pct = ((current_price - ref['high']) / ref['high']) * 100
            with idx_cols[i]:
                # 핵심 수정: ref['date']를 f-string에 추가
                draw_metric_card(
                    name, 
                    current_price, 
                    gap_pct, 
                    f"52W High: {ref['high']:,.0f} ({ref['date']})"
                )

    st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)

    # --- 구역 2: 매크로 지표 ---
    st.subheader("📊 Macro Indicators")
    macro_cols = st.columns(2)
    
    # 1. 달러-원 환율
    with macro_cols[0]:
        ex_price, ex_change, ex_pct = get_live_data("USDKRW=X")
        draw_metric_card("USD / KRW", ex_price, ex_pct, f"Last: {ex_price:,.2f} (Change: {ex_change:+.2f})")
        
    # 2. VIX 지수
    with macro_cols[1]:
        vix_price, _, vix_pct = get_live_data("^VIX")
        draw_metric_card("VIX (Fear Index)", vix_price, vix_pct, "Market Volatility", is_vix=True)

    st.markdown(f"<p style='text-align: left; color: #bbb; font-size: 14px; margin-top: 50px;'>⏱ Last Updated: {now} (KST)</p>", unsafe_allow_html=True)

render_dashboard()
