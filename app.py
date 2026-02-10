import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time
import requests

# 1. 페이지 설정
st.set_page_config(
    page_title="미국 증시 & 시장 심리 대시보드",
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
    """CNN API 주소 변경에 대응한 최신 경로 시도"""
    urls = [
        "https://production.dataviz.cnn.io/index/feargreed/graphdata", # 기존 경로
        "https://www.cnn.com/markets/fear-and-greed" # 메인 페이지 (백업용)
    ]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    
    try:
        # 첫 번째 API 경로 시도
        r = requests.get(urls[0], headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            score = round(data['fear_and_greed']['score'])
            rating = data['fear_and_greed']['rating']
            return score, rating
        else:
            # API가 막혔을 경우 VIX 지수를 활용한 자체 심리 점수 계산 (대체제)
            vix = get_vix_data()
            if vix > 0:
                # VIX가 높을수록 공포(점수 낮음), 낮을수록 탐욕(점수 높음)으로 환산
                calc_score = max(0, min(100, round(100 - (vix * 2))))
                if calc_score <= 25: rating = "Extreme Fear (대체)"
                elif calc_score <= 45: rating = "Fear (대체)"
                elif calc_score <= 55: rating = "Neutral (대체)"
                elif calc_score <= 75: rating = "Greed (대체)"
                else: rating = "Extreme Greed (대체)"
                return calc_score, rating
            return 0, "서버 점검 중"
    except:
        return 0, "데이터 일시 오류"

# 3. 메인 화면
st.title("📊 미국 증시 및 시장 심리 실시간 현황")
st.write("3대 지수와 시장 공포 수준을 10초마다 자동 업데이트합니다.")

# 4. 업데이트 영역
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
        color = "#FF0000" if rate >= 0 else "#0000FF"
        with idx_cols[i]:
            st.markdown(f"<h2 style='text-align: center; font-size: 30px; font-weight: 800;'>{name}</h2>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 25px; border-radius: 20px; text-align: center; border: 2px solid #eee;">
                    <h1 style="margin: 0; color: {color}; font-size: 55px;">{rate:+.2f}%</h1>
                    <p style="margin: 5px 0; color: #555; font-size: 18px;">현재: {price:,.2f}</p>
                    <p style="margin: 0; font-size: 13px; color: #999;">고점: {high_val:,.2f}</p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 구역 2: 심리 지표 ---
    st.markdown("### 🕵️ 시장 심리 지표")
    fear_cols = st.columns(2)
    
    # VIX 카드
    vix_val = get_vix_data()
    vix_color = "#FF0000" if vix_val >= 20 else "#0000FF"
    with fear_cols[0]:
        st.markdown("<h2 style='text-align: center; font-size: 30px; font-weight: 800;'>VIX (공포지수)</h2>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="background-color: #fff4f4; padding: 25px; border-radius: 20px; text-align: center; border: 2px solid #ffcccc;">
                <h1 style="margin: 0; color: {vix_color}; font-size: 55px;">{vix_val:.2f}</h1>
                <p style="margin: 5px 0; color: #666;">20 이상: 시장 불안 / 30 이상: 패닉</p>
            </div>
        """, unsafe_allow_html=True)

    # CNN Fear & Greed (실패 시 VIX 기반 산출)
    cnn_score, cnn_rating = get_cnn_fear_greed()
    if cnn_score <= 25: cnn_color = "#FF0000"
    elif cnn_score <= 45: cnn_color = "#FF8C00"
    elif cnn_score <= 55: cnn_color = "#666666"
    else: cnn_color = "#008000"
    
    with fear_cols[1]:
        st.markdown("<h2 style='text-align: center; font-size: 30px; font-weight: 800;'>Fear & Greed</h2>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="background-color: #f4fff4; padding: 25px; border-radius: 20px; text-align: center; border: 2px solid #ccffcc;">
                <h1 style="margin: 0; color: {cnn_color}; font-size: 55px;">{cnn_score}</h1>
                <p style="margin: 5px 0; font-size: 18px; color: #333; font-weight: bold;">{cnn_rating}</p>
            </div>
        """, unsafe_allow_html=True)

    st.write(f"⏱️ 마지막 업데이트: {current_time} (한국 시간)")

# 실행
update_dashboard()

st.divider()
st.caption("※ 본 데이터는 Yahoo Finance 실시간 데이터를 기반으로 구성되었습니다.")
