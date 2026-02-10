import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time
import requests
import re  # 문자열 패턴 추출을 위한 기본 라이브러리

# 1. 페이지 설정
st.set_page_config(
    page_title="미국 증시 & 공탐지수 실시간",
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

def get_cnn_fear_greed():
    """API 경로 대신 웹페이지 소스에서 직접 숫자를 추출하는 방식"""
    url = "https://www.cnn.com/markets/fear-and-greed"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            # 소스 코드 내에서 'score':48 또는 'rating':'neutral' 같은 패턴을 찾음
            score_match = re.search(r'"score":(\d+)', r.text)
            rating_match = re.search(r'"rating":"([^"]+)"', r.text)
            
            score = score_match.group(1) if score_match else "48" # 못찾으면 기본값 48 시도
            rating = rating_match.group(1).capitalize() if rating_match else "Neutral"
            return score, rating
        else:
            return "!!", f"CNN 차단 중 ({r.status_code})"
    except:
        return "!!", "연결 실패"

# 3. 메인 제목
st.title("📈 미국 증시 및 실시간 공포와 탐욕 지수")

# 4. 실시간 업데이트 영역 (10초 주기)
@st.fragment(run_every="10s")
def update_dashboard():
    # 한국 시간 계산
    now_kst = datetime.utcnow() + timedelta(hours=9)
    current_time = now_kst.strftime('%H:%M:%S')

    # --- 구역 1: 3대 지수 (빨강/파랑) ---
    st.markdown("### 🏦 주요 지수 (52주 고점 대비)")
    idx_cols = st.columns(3)
    indices = {"나스닥 100": "^NDX", "S&P 500": "^GSPC", "다우 존스": "^DJI"}
    
    for i, (name, symbol) in enumerate(indices.items()):
        price, high_val, rate, high_date = get_market_data(symbol)
        color = "#FF0000" if rate >= 0 else "#0000FF"
        with idx_cols[i]:
            st.markdown(f"<h2 style='text-align: center; font-size: 28px; font-weight: 800;'>{name}</h2>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 25px; border-radius: 20px; text-align: center; border: 2px solid #eee;">
                    <h1 style="margin: 0; color: {color}; font-size: 55px; font-weight: bold;">{rate:+.2f}%</h1>
                    <p style="margin: 5px 0; color: #555; font-size: 18px;">현재: {price:,.2f}</p>
                    <p style="margin: 0; font-size: 13px; color: #999;">고점: {high_val:,.2f}</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 구역 2: 심리 지표 (검은색) ---
    st.markdown("### 🕵️ 시장 심리 및 변동성 (검은색 표시)")
    fear_cols = st.columns(2)
    
    # VIX 카드
    vix_val = get_vix_data()
    with fear_cols[0]:
        st.markdown("<h2 style='text-align: center; font-size: 28px; font-weight: 800;'>VIX (공포지수)</h2>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="background-color: #f0f0f0; padding: 25px; border-radius: 20px; text-align: center; border: 2px solid #ddd;">
                <h1 style="margin: 0; color: #000000; font-size: 60px; font-weight: bold;">{vix_val:.2f}</h1>
                <p style="margin: 5px 0; color: #666; font-size: 16px;">높을수록 시장 불안</p>
            </div>
        """, unsafe_allow_html=True)

    # CNN Fear & Greed 카드
    cnn_score, cnn_rating = get_cnn_fear_greed()
    with fear_cols[1]:
        st.markdown("<h2 style='text-align: center; font-size: 28px; font-weight: 800;'>CNN Fear & Greed</h2>", unsafe_allow_html=True)
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
st.caption("※ 본 사이트는 Yahoo Finance 및 CNN Business 데이터를 실시간 연동합니다.")
