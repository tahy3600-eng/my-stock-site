import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time
import requests

# 1. 페이지 설정
st.set_page_config(
    page_title="미국 증시 & 공포 지수 대시보드",
    page_icon="📊",
    layout="wide"
)

# 2. 데이터 수집 함수들
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
    try:
        # [수정] CNN 서버 차단을 피하기 위해 더 정교한 브라우저 정보(User-Agent) 추가
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.cnn.com/markets/fear-and-greed'
        }
        url = "https://production.dataviz.cnn.io/index/feargreed/graphdata"
        r = requests.get(url, headers=headers, timeout=10) # 타임아웃 10초로 연장
        
        if r.status_code == 200:
            data = r.json()
            score = round(data['fear_and_greed']['score'])
            rating = data['fear_and_greed']['rating']
            return score, rating
        else:
            return 0, f"통신 상태 확인 ({r.status_code})"
    except: 
        return 0, "데이터 점검 중"

# 3. 메인 제목
st.title("📊 미국 증시 및 시장 심리 실시간 현황")
st.write("3대 지수와 시장의 공포 수준을 10초마다 자동 갱신합니다.")

# 4. 실시간 업데이트 영역
@st.fragment(run_every="10s")
def update_dashboard():
    now_kst = datetime.utcnow() + timedelta(hours=9)
    current_time = now_kst.strftime('%H:%M:%S')

    # --- 상단: 3대 지수 영역 ---
    st.markdown("### 🏦 주요 지수 (52주 고점 대비)")
    idx_cols = st.columns(3)
    indices = {"나스닥 100": "^NDX", "S&P 500": "^GSPC", "다우 존스": "^DJI"}
    
    for i, (name, symbol) in enumerate(indices.items()):
        price, high_val, rate, high_date = get_market_data(symbol)
        color = "#FF0000" if rate >= 0 else "#0000FF"
        with idx_cols[i]:
            st.markdown(f"<h2 style='text-align: center; font-size: 32px; font-weight: 800; margin-bottom: 5px;'>{name}</h2>", unsafe_allow_html=True)
            card_html = f"""
            <div style="background-color: #f8f9fa; padding: 30px 20px; border-radius: 20px; text-align: center; border: 2px solid #eee; box-shadow: 0px 4px 10px rgba(0,0,0,0.05);">
                <h1 style="margin: 0; color: {color}; font-size: 60px; font-weight: bold;">{rate:+.2f}%</h1>
                <p style="margin: 10px 0 0 0; font-size: 20px; color: #555;">현재가: {price:,.2f}</p>
                <hr style="border: 0.5px solid #ddd; margin: 20px 0;">
                <p style="margin: 0; font-size: 16px; color: #888;">전고점: {high_val:,.2f} ({high_date})</p>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 하단: 공포 지수 영역 ---
    st.markdown("### 🕵️ 시장 심리 및 변동성")
    fear_cols = st.columns(2)
    
    # VIX 카드
    vix_val = get_vix_data()
    vix_color = "#FF0000" if vix_val >= 20 else "#0000FF"
    with fear_cols[0]:
        st.markdown("<h2 style='text-align: center; font-size: 32px; font-weight: 800; margin-bottom: 5px;'>VIX (공포지수)</h2>", unsafe_allow_html=True)
        vix_html = f"""
        <div style="background-color: #fff4f4; padding: 30px 20px; border-radius: 20px; text-align: center; border: 2px solid #ffcccc;">
            <h1 style="margin: 0; color: {vix_color}; font-size: 60px; font-weight: bold;">{vix_val:.2f}</h1>
            <p style="margin: 10px 0 0 0; font-size: 18px; color: #666;">20 이상: 시장 불안 / 30 이상: 패닉</p>
        </div>
        """
        st.markdown(vix_html, unsafe_allow_html=True)

    # CNN Fear & Greed 카드
    cnn_score, cnn_rating = get_cnn_fear_greed()
    if cnn_score <= 25: cnn_color = "#FF0000"
    elif cnn_score <= 45: cnn_color = "#FF8C00"
    elif cnn_score <= 55: cnn_color = "#666666"
    else: cnn_color = "#008000"
    
    with fear_cols[1]:
        st.markdown("<h2 style='text-align: center; font-size: 32px; font-weight: 800; margin-bottom: 5px;'>CNN Fear & Greed</h2>", unsafe_allow_html=True)
        cnn_html = f"""
        <div style="background-color: #f4fff4; padding: 30px 20px; border-radius: 20px; text-align: center; border: 2px solid #ccffcc;">
            <h1 style="margin: 0; color: {cnn_color}; font-size: 60px; font-weight: bold;">{cnn_score}</h1>
            <p style="margin: 10px 0 0 0; font-size: 20px; color: #333; font-weight: bold;">상태: {cnn_rating}</p>
        </div>
        """
        st.markdown(cnn_html, unsafe_allow_html=True)

    st.write(f"⏱️ 마지막 업데이트: {current_time} (한국 시간)")

# 앱 실행
update_dashboard()

st.divider()
st.caption("※ 데이터 출처: Yahoo Finance 및 CNN Business 실시간 데이터 기준")
