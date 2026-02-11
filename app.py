import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import requests

# 1. 페이지 설정
st.set_page_config(
    page_title="미국 증시 & 환율 실시간 대시보드",
    page_icon="📈",
    layout="wide"
)

# 2. 데이터 수집 함수
def get_market_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1y")
        if df.empty: return 0.0, 0.0, 0.0, "N/A"
        high_val = df['High'].max()
        high_date = df['High'].idxmax().strftime('%Y-%m-%d')
        current = df['Close'].iloc[-1]
        rate = ((current - high_val) / high_val) * 100
        return current, high_val, rate, high_date
    except: return 0.0, 0.0, 0.0, "오류"

def get_vix_data():
    try:
        vix = yf.Ticker("^VIX")
        current = vix.history(period="1d")['Close'].iloc[-1]
        return current
    except: return 0.0

def get_exchange_rate():
    try:
        # 야후 파이낸스 달러/원 심볼
        ticker = yf.Ticker("USDKRW=X")
        data = ticker.history(period="2d")
        current = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2]
        change = current - prev_close
        pct_change = (change / prev_close) * 100
        return current, change, pct_change
    except: return 0.0, 0.0, 0.0

# 3. 메인 타이틀
st.title("📈 미국 지수 및 달러 환율 실시간")

# 4. 실시간 업데이트 영역
@st.fragment(run_every="10s")
def update_dashboard():
    now_kst = datetime.utcnow() + timedelta(hours=9)
    current_time = now_kst.strftime('%H:%M:%S')

    # --- 구역 1: 3대 지수 ---
    st.markdown("### 🏦 주요 지수 (52주 고점 대비)")
    idx_cols = st.columns(3)
    indices = {"나스닥 100": "^NDX", "S&P 500": "^GSPC", "다우 존스": "^DJI"}
    
    for i, (name, symbol) in enumerate(indices.items()):
        price, high_val, rate, high_date = get_market_data(symbol)
        color = "#FF4B4B" if rate >= 0 else "#31333F" # 기본 색상 설정
        # 하락률에 따른 강조색 (주식은 마이너스일 때 파란색이 일반적이나 여기선 고점대비 괴리율임)
        with idx_cols[i]:
            st.markdown(f"<h2 style='text-align: center; font-size: 22px; font-weight: 800;'>{name}</h2>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="
                    display: flex; flex-direction: column; justify-content: center;
                    background-color: #f8f9fa; padding: 25px; border-radius: 20px;
                    text-align: center; border: 2px solid #eee; min-height: 220px;
                ">
                    <h1 style="margin: 0; color: #0000FF; font-size: 48px; font-weight: bold;">{rate:+.2f}%</h1>
                    <p style="margin: 10px 0 0 0; color: #444; font-size: 18px; font-weight: 600;">현재: {price:,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <p style="text-align: center; margin-top: 10px; font-size: 13px; color: #666;">
                    52주 고점: <b>{high_val:,.2f}</b> ({high_date})
                </p>
            """, unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # --- 구역 2: 변동성 및 환율 ---
    st.markdown("### 📊 시장 지표")
    ind_cols = st.columns(2)
    
    # VIX 카드
    vix_val = get_vix_data()
    vix_color = "#FF4B4B" if vix_val >= 20 else "#008000"
    with ind_cols[0]:
        st.markdown("<h2 style='text-align: center; font-size: 22px; font-weight: 800;'>VIX </h2>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="
                display: flex; flex-direction: column; justify-content: center;
                background-color: #f8f9fa; padding: 25px; border-radius: 20px;
                text-align: center; border: 2px solid #eee; min-height: 200px;
            ">
                <h1 style="margin: 0; color: {vix_color}; font-size: 55px; font-weight: bold;">{vix_val:.2f}</h1>
            </div>
        """, unsafe_allow_html=True)

    # 달러-원 환율 카드
    rate_val, rate_change, rate_pct = get_exchange_rate()
    rate_color = "#FF4B4B" if rate_change > 0 else "#0000FF" # 상승 시 빨간색(원화약세)
    with ind_cols[1]:
        st.markdown("<h2 style='text-align: center; font-size: 22px; font-weight: 800;'>USD / KRW (환율)</h2>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="
                display: flex; flex-direction: column; justify-content: center;
                background-color: #f8f9fa; padding: 25px; border-radius: 20px;
                text-align: center; border: 2px solid #eee; min-height: 200px;
            ">
                <h1 style="margin: 0; color: {rate_color}; font-size: 55px; font-weight: bold;">{rate_val:,.2f}</h1>
                <p style="margin: 5px 0 0 0; color: {rate_color}; font-size: 18px; font-weight: 600;">
                    {rate_change:+.2f} ({rate_pct:+.2f}%)
                </p>
            </div>
        """, unsafe_allow_html=True)

    # 마지막 업데이트
    st.markdown(f"""
        <div style="text-align: left; margin-top: 30px; color: #999; font-size: 14px;">
            ⏱️ 마지막 업데이트: {current_time} (한국 시간)
        </div>
    """, unsafe_allow_html=True)

# 실행
update_dashboard()

st.divider()
st.caption("※ 데이터 출처: Yahoo Finance (환율은 실시간 기준 15~20분 지연될 수 있습니다. 김채원 사랑해)")




