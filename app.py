import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time
import requests

# 1. 페이지 설정
st.set_page_config(
    page_title="미국 증시 & CNN 공탐지수 실시간",
    page_icon="📊",
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

def get_cnn_fear_greed():
    # [핵심 수정] CNN 서버의 차단을 피하기 위한 최신 API 경로와 정교한 헤더
    url = "https://production.dataviz.cnn.io/index/feargreed/graphdata"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.cnn.com",
        "Referer": "https://www.cnn.com/markets/fear-and-greed"
    }
    try:
        # 세션을 사용하여 연결 안정성 확보
        session = requests.Session()
        r = session.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            score = round(data['fear_and_greed']['score'])
            rating = data['fear_and_greed']['rating']
            return score, rating
        else:
            return "오류", f"접근 차단({r.status_code})"
    except Exception as e:
        return "오류", "연결 실패"

# 3. 메인 제목
st.title("📊 미국 증시 및 실시간 공포와 탐욕 지수")

# 4. 실시간 업데이트 영역 (10초 주기)
@st.fragment(run_every="10s")
def update_dashboard():
    # 한국 시간 계산
    now_kst = datetime.utcnow() + timedelta(hours=9)
    current_time = now_kst.strftime('%H:%M:%S')

    # --- 구역 1: 3대 지수 (빨강/파랑 색상 유지) ---
    st.markdown("### 🏦 주요 지수 (52주 고점 대비)")
    idx_cols = st.columns(3)
    indices = {"나스닥 100": "^NDX", "S&P 500": "^GSPC", "다우 존스": "^DJI"}
    
    for i, (name, symbol) in enumerate(indices.items()):
        price, high_val, rate, high_date = get_market_data(symbol)
        color = "#FF0000" if rate >= 0 else "#0000FF"
        with idx_cols[i]:
            st.markdown(f"<h2 style='text-align: center; font-size: 30px; font-weight: 800;'>{name}</h2>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 25px; border-radius: 20px; text-align: center; border: 2px solid #eee;">
                    <h1 style="margin: 0; color: {color}; font-size: 55px; font-weight: bold;">{rate:+.2f}%</h1>
                    <p style="margin: 5px 0; color: #555; font-size: 18px;">현재: {price:,.2f}</p>
                    <p style="margin: 0; font-size: 13px; color: #999;">고점: {high_val:,.2f}</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 구역 2: 심리 지표 (VIX & CNN - 검은색 적용) ---
    st.markdown("### 🕵️ 시장 심리 지표 (실시간)")
    fear_cols = st.columns(2)
    
    # VIX 카드 (글자색 검정)
    vix_val = get_vix_data()
    with fear_cols[0]:
        st.markdown("<h2 style='text-align: center; font-size: 30px; font-weight: 800;'>VIX (공포지수)</h2>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="background-color: #f0f0f0; padding: 25px; border-radius: 20px; text-align: center; border: 2px solid #ddd;">
                <h1 style="margin: 0; color: #000000; font-size: 60px; font-weight: bold;">{vix_val:.2f}</h1>
                <p style="margin: 5px 0; color: #666; font-size: 16px;">숫자가 높을수록 시장 공포가 큼</p>
            </div>
        """, unsafe_allow_html=True)

    # CNN Fear & Greed 카드 (글자색 검정)
    cnn_score, cnn_rating = get_cnn_fear_greed()
    with fear_cols[1]:
        st.markdown("<h2 style='text-align: center; font-size: 30px; font-weight: 800;'>CNN Fear & Greed</h2>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="background-color: #f0f0f0; padding: 25px; border-radius: 20px; text-align: center; border: 2px solid #ddd;">
                <h1 style="margin: 0; color: #000000; font-size: 60px; font-weight: bold;">{cnn_score}</h1>
                <p style="margin: 5px 0; font-size: 20px; color: #333; font-weight: bold;">상태: {cnn_rating}</p>
            </div>
        """, unsafe_allow_html=True)

    st.write(f"⏱️ 마지막 업데이트: {current_time} (한국 시간)")

# 실행
update_dashboard()

st.divider()
st.caption("※ 본 사이트는 Yahoo Finance 및 CNN Business의 실시간 데이터를 연동합니다.")
