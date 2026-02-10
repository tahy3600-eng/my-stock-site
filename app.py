import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import time
import requests
import re

# 1. 페이지 설정
st.set_page_config(
    page_title="미국 증시 & 시장 심리 대시보드",
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
    url = "https://www.cnn.com/markets/fear-and-greed"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            score_match = re.search(r'"score":(\d+)', r.text)
            rating_match = re.search(r'"rating":"([^"]+)"', r.text)
            score = int(score_match.group(1)) if score_match else 48
            rating = rating_match.group(1).capitalize() if rating_match else "Neutral"
            return score, rating
        return 48, "Neutral"
    except: return 48, "Neutral"

# 3. 메인 타이틀
st.title("📈 미국 증시 및 시장 심리 실시간 현황")

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
        color = "#FF0000" if rate >= 0 else "#0000FF"
        with idx_cols[i]:
            st.markdown(f"<h2 style='text-align: center; font-size: 24px; font-weight: 800; color: #333;'>{name}</h2>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="
                    display: flex; flex-direction: column; justify-content: center;
                    background-color: #f8f9fa; padding: 25px; border-radius: 20px;
                    text-align: center; border: 2px solid #eee; min-height: 250px;
                ">
                    <h1 style="margin: 0; color: {color}; font-size: 52px; font-weight: bold;">{rate:+.2f}%</h1>
                    <p style="margin: 10px 0 0 0; color: #444; font-size: 20px; font-weight: 600;">현재: {price:,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <p style="text-align: center; margin-top: 10px; font-size: 14px; color: #666;">
                    52주 고점: <b>{high_val:,.2f}</b><br>
                    <span style="color: #aaa; font-size: 12px;">({high_date} 달성)</span>
                </p>
            """, unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # --- 구역 2: 심리 지표 (가운데 정렬) ---
    st.markdown("### 🕵️ 시장 심리 및 변동성")
    
    # 3열을 만들되, 양옆을 비우고 가운데 2개 카드를 배치하기 위해 columns 조절
    # [1, 1, 1] 비율로 생성하여 가운데 위주로 배치
    fear_cols = st.columns([1, 1, 1])
    
    # VIX 카드 (가운데 열의 첫 번째)
    vix_val = get_vix_data()
    vix_color = "#FF0000" if vix_val >= 20 else "#0000FF"
    with fear_cols[0]:
        st.markdown("<h2 style='text-align: center; font-size: 24px; font-weight: 800; color: #333;'>VIX (공포지수)</h2>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="
                display: flex; flex-direction: column; justify-content: center;
                background-color: #f8f9fa; padding: 25px; border-radius: 20px;
                text-align: center; border: 2px solid #eee; min-height: 250px;
            ">
                <h1 style="margin: 0; color: {vix_color}; font-size: 60px; font-weight: bold;">{vix_val:.2f}</h1>
                <p style="margin: 15px 0 0 0; font-size: 14px; color: #999;">변동성 수치 (20 이상 위험)</p>
            </div>
        """, unsafe_allow_html=True)

    # CNN 공탐지수 카드 (가운데 열의 두 번째)
    cnn_score, cnn_rating = get_cnn_fear_greed()
    if cnn_score <= 45: cnn_color = "#FF0000"
    elif cnn_score <= 55: cnn_color = "#666666"
    else: cnn_color = "#008000"
    
    with fear_cols[1]:
        st.markdown("<h2 style='text-align: center; font-size: 24px; font-weight: 800; color: #333;'>CNN Fear & Greed</h2>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="
                display: flex; flex-direction: column; justify-content: center;
                background-color: #f8f9fa; padding: 25px; border-radius: 20px;
                text-align: center; border: 2px solid #eee; min-height: 250px;
            ">
                <h1 style="margin: 0; color: {cnn_color}; font-size: 60px; font-weight: bold;">{cnn_score}</h1>
                <p style="margin: 15px 0 0 0; font-size: 18px; color: {cnn_color}; font-weight: bold;">상태: {cnn_rating}</p>
            </div>
        """, unsafe_allow_html=True)

    st.write(f"⏱️ 마지막 업데이트: {current_time} (한국 시간)")

# 실행
update_dashboard()

st.divider()
st.caption("※ 데이터 출처: Yahoo Finance & CNN Business")
