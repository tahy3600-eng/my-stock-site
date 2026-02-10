import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta # 추가 설치 없이 기본 제공됨
import time

# 1. 페이지 설정 및 SEO
st.set_page_config(
    page_title="미국 증시 전고점 실시간 추적기",
    page_icon="📈",
    layout="wide"
)

# 2. 데이터 가져오기 함수
def get_market_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1y")
        if df.empty:
            return 0.0, 0.0, 0.0, "N/A"
        
        high_val = df['High'].max()
        high_date = df['High'].idxmax().strftime('%Y-%m-%d')
        current = df['Close'].iloc[-1]
        rate = ((current - high_val) / high_val) * 100
        
        return current, high_val, rate, high_date
    except:
        return 0.0, 0.0, 0.0, "오류"

# 3. 메인 제목
st.title("📈 주요 지수 전고점 대비 등락")
st.write("지난 1년(52주)의 최고치인 **'전고점'** 대비 현재 위치를 10초마다 실시간으로 분석합니다.")

# 4. 실시간 업데이트 영역 (10초 주기)
@st.fragment(run_every="10s")
def update_dashboard():
    # [핵심] 라이브러리 설치 없이 한국 시간 계산 (표준시 + 9시간)
    now_kst = datetime.utcnow() + timedelta(hours=9)
    current_time = now_kst.strftime('%H:%M:%S')
    
    indices = {
        "나스닥 100": "^NDX",
        "S&P 500": "^GSPC",
        "다우 존스": "^DJI"
    }
    
    cols = st.columns(3)
    
    for i, (name, symbol) in enumerate(indices.items()):
        price, high_val, rate, high_date = get_market_data(symbol)
        color = "#FF0000" if rate >= 0 else "#0000FF"
        
        with cols[i]:
            # 지수 이름 상단 배치
            st.markdown(f"<h2 style='text-align: center; font-size: 34px; font-weight: 800; margin-bottom: 10px; color: #333;'>{name}</h2>", unsafe_allow_html=True)
            
            # 카드 디자인
            card_html = f"""
            <div style="
                background-color: #f8f9fa; 
                padding: 35px 20px; 
                border-radius: 20px; 
                text-align: center;
                border: 2px solid #eee;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
            ">
                <h1 style="margin: 0; color: {color}; font-size: 68px; font-weight: bold; letter-spacing: -2px;">
                    {rate:+.2f}%
                </h1>
                <p style="margin: 15px 0 0 0; font-size: 22px; color: #555; font-weight: 600;">
                    현재가: {price:,.2f}
                </p>
                <hr style="border: 0.5px solid #ddd; margin: 25px 0;">
                <p style="margin: 5px 0; font-size: 18px; color: #444;">
                    <b>전고점:</b> {high_val:,.2f}
                </p>
                <p style="margin: 0; font-size: 14px; color: #999;">
                    (달성일: {high_date})
                </p>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
    # 한국 시간 기준 표시
    st.write(f"⏱️ 마지막 갱신: {current_time} (한국 시간 기준)")

# 실행
update_dashboard()

# 5. 하단 공지
st.divider()
st.caption("※ 본 지표는 **Yahoo Finance 실시간 시세**를 바탕으로 하며, **최근 52주 신고가** 대비 현재 위치를 산출한 결과입니다.")
