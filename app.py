import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# 1. 페이지 설정 및 디자인 개선
st.set_page_config(page_title="ETF Market Watch", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    * { font-family: 'Pretendard', sans-serif; }
    .main { background-color: #f8f9fa; }
    .metric-card {
        background: white; padding: 30px 20px; border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #f1f3f5;
        transition: transform 0.2s ease-in-out; text-align: center;
    }
    .metric-card:hover { transform: translateY(-5px); }
    </style>
    """, unsafe_allow_html=True)

# 2. 고효율 데이터 수집 로직
@st.cache_data(ttl=86400) # 전고점은 하루에 한 번만 갱신
def get_historical_high(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="2y")
        if df.empty: return None
        high_val = df['High'].max()
        high_date = df['High'].idxmax().strftime('%Y.%m.%d')
        return {"val": high_val, "date": high_date}
    except Exception:
        return None

def get_current_price(symbol):
    try:
        # history(period="1d")보다 빠른 최신가 가져오기
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info['last_price']
        return price if price is not None else 0.0
    except:
        # fast_info 실패 시 대안
        df = ticker.history(period="1d")
        return df['Close'].iloc[-1] if not df.empty else 0.0

# 3. 카드 렌더링 (HTML 컴포넌트화)
def draw_card(title, price, pct=None, sub="", mode="normal"):
    colors = {"red": "#D62828", "blue": "#003049", "green": "#2A9D8F", "orange": "#F77F00", "gray": "#6c757d"}
    
    content = ""
    if mode == "etf":
        status_color = colors["red"] if pct >= 0 else colors["blue"]
        content = f"""
            <div style="font-size:42px; font-weight:800; color:{status_color};">{pct:+.2f}%</div>
            <div style="font-size:18px; font-weight:600; color:#444; margin-top:5px;">${price:,.2f}</div>
            <div style="color:#adb5bd; font-size:11px; margin-top:12px;">ATH: {sub}</div>
        """
    elif mode == "vix":
        v_color, v_state = (colors["green"], "STABLE") if price < 20 else (colors["orange"], "CAUTION") if price < 30 else (colors["red"], "PANIC")
        content = f"""
            <div style="font-size:42px; font-weight:800; color:#212529;">{price:,.2f}</div>
            <div style="color:{v_color}; font-size:13px; font-weight:700; margin-top:12px;">● {v_state}</div>
        """
    else: # FX 등 일반 지표
        content = f'<div style="font-size:42px; font-weight:800; color:#212529;">{price:,.2f}</div>'

    st.markdown(f"""
        <div class="metric-card">
            <div style="color:#6c757d; font-size:12px; font-weight:600; letter-spacing:1px; margin-bottom:15px;">{title}</div>
            {content}
        </div>
    """, unsafe_allow_html=True)

# 4. 메인 대시보드 로직
st.title("📊 Global Market Watch")

@st.fragment(run_every="30s")
def render_dashboard():
    # 병렬 데이터 처리를 위한 티커 리스트
    etf_tickers = {"Nasdaq 100 (QQQ)": "QQQ", "S&P 500 (VOO)": "VOO"}
    macro_tickers = {"USD/KRW": "USDKRW=X", "VIX Index": "^VIX"}
    
    # 시간 표시
    kst_now = (datetime.utcnow() + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')
    st.caption(f"Last updated: {kst_now} (KST) | Auto-refresh: 30s")

    # 데이터 병렬 수집 (속도 최적화 핵심)
    all_tickers = list(etf_tickers.values()) + list(macro_tickers.values())
    with ThreadPoolExecutor() as executor:
        prices = list(executor.map(get_current_price, all_tickers))
    
    price_map = dict(zip(all_tickers, prices))

    # --- Layout: Core ETFs ---
    st.subheader("Core ETFs (Drawdown from ATH)")
    cols = st.columns(2)
    for i, (name, sym) in enumerate(etf_tickers.items()):
        with cols[i]:
            ref = get_historical_high(sym)
            curr = price_map[sym]
            if ref and curr > 0:
                gap = ((curr - ref['val']) / ref['val']) * 100
                draw_card(name, curr, gap, sub=f"${ref['val']:,.1f} ({ref['date']})", mode="etf")
            else:
                st.error(f"Data Error: {sym}")

    st.divider()

    # --- Layout: Macro Indicators ---
    m_cols = st.columns(2)
    with m_cols[0]:
        usd_price = price_map["USDKRW=X"]
        draw_card("USD / KRW Exchange Rate", usd_price) if usd_price > 0 else st.warning("USD Data N/A")
    
    with m_cols[1]:
        vix_price = price_map["^VIX"]
        draw_card("Market Volatility (VIX)", vix_price, mode="vix") if vix_price > 0 else st.warning("VIX Data N/A")

render_dashboard()
