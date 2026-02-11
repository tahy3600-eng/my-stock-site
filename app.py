import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(
    page_title="Pro-Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

# 2. 데이터 처리 로직 (최적화 적용)

@st.cache_data(ttl=3600)  # 52주 고점 데이터는 1시간(3600초) 동안 캐싱
def get_high_reference(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1y")
        if df.empty: return None
        high_val = df['High'].max()
        high_date = df['High'].idxmax().strftime('%Y-%m-%d')
        return {"high": high_val, "date": high_date}
    except:
        return None

def get_live_data(symbol):
    """현재가 및 변동률만 빠르게 가져오기"""
    try:
        ticker = yf.Ticker(symbol)
        # 2일치 데이터를 가져와 전일 대비 변동 계산
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
def draw_metric_card(title, price, change_pct, sub_text="", is_stock=True):
    """커스텀 디자인 카드 렌더링"""
    # 색상 로직: 주식/지수는 상승 시 빨강, 환율은 상황에 따라 설정 가능
    color = "#FF4B4B" if change_pct >= 0 else "#0000FF"
    
    st.markdown(f"""
        <div style="
            background-color: #ffffff; padding: 20px; border-radius: 15px;
            border-left: 5px solid {color}; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 10px; min-height: 160px;
        ">
            <h4 style="margin: 0; color: #555; font-size: 16px;">{title}</h4>
            <h2 style="margin: 10px 0; color: {color}; font-size: 32px;">{change_pct:+.2f}%</h2>
            <p style="margin: 0; font-weight: bold; font-size: 18px;">{price:,.2f}</p>
            <p style="margin: 5px 0 0 0; color: #888; font-size: 12px;">{sub_text}</p>
        </div>
    """, unsafe_allow_html=True)

# 4. 메인 대시보드 레이아웃
st.title("📊 Professional Market Dashboard")

@st.fragment(run_every="10s")
def render_dashboard():
    now = (datetime.utcnow() + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')
    
    # --- 구역 1: 3대 지수 (고점 대비 괴리율 집중) ---
    st.subheader("🏦 Market Indices (vs 52W High)")
    idx_cols = st.columns(3)
    indices = {"Nasdaq 100": "^NDX", "S&P 500": "^GSPC", "Dow Jones": "^DJI"}
    
    for i, (name, sym) in enumerate(indices.items()):
        ref = get_high_reference(sym)
        current_price, _, _ = get_live_data(sym)
        
        if ref and current_price > 0:
            gap_pct = ((current_price - ref['high']) / ref['high']) * 100
            with idx_cols[i]:
                draw_metric_card(name, current_price, gap_pct, f"52W High: {ref['high']:,.0f} ({ref['date']})")

    # --- 구역 2: 주요 종목 & 환율 ---
    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("🍎 Top Stocks (Daily)")
        stock_cols = st.columns(2)
        stocks = {"NVIDIA": "NVDA", "Apple": "AAPL", "Tesla": "TSLA", "Microsoft": "MSFT"}
        for i, (name, sym) in enumerate(stocks.items()):
            price, _, pct = get_live_data(sym)
            with stock_cols[i % 2]:
                draw_metric_card(name, price, pct, f"Symbol: {sym}")

    with col_right:
        st.subheader("💵 Macro Indicators")
        # 환율
        ex_price, ex_change, ex_pct = get_live_data("USDKRW=X")
        draw_metric_card("USD/KRW", ex_price, ex_pct, f"Change: {ex_change:+.2f}")
        
        # VIX
        vix_price, _, _ = get_live_data("^VIX")
        vix_color = "#FF4B4B" if vix_price > 20 else "#008000"
        st.markdown(f"""
            <div style="background-color: #1e1e1e; color: white; padding: 15px; border-radius: 10px; text-align: center;">
                <small>Fear Index (VIX)</small>
                <h2 style="color: {vix_color}; margin: 5px 0;">{vix_price:.2f}</h2>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"<p style='text-align: right; color: gray; padding-top: 20px;'>Last Updated: {now} (KST)</p>", unsafe_allow_html=True)

render_dashboard()
