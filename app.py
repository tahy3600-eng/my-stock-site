import streamlit as st
import yfinance as yf
import time

# 1. 페이지 설정
st.set_page_config(
    page_title="미국 증시 전고점 추적기",
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
st.write("지난 1년(52주)의 최고치인 **'전고점'** 대비 현재 지수의 위치를 실시간으로 분석합니다.")

# 4. 실시간 자동 업데이트 영역 (10초 주기)
@st.fragment(run_every="10s")
def update_dashboard():
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
            # 카드 내부 디자인: 이름 상단 배치, 단위 P 제거
            st.markdown(f"""
                <div style="
                    background-color: #f8f9fa; 
                    padding: 30px 20px; 
                    border-radius: 20px; 
                    text-align: center;
                    border: 2px solid #eee;
                ">
                    <h2 style="margin: 0 0 15px 0; font-size: 32px; color: #333; font-weight: 800;">
                        {name}
                    </h2>
                    <h1 style="margin: 0; color: {color}; font-size: 65px; font-weight: bold;">
                        {rate:+.2f}%
                    </h1>
                    <p style="margin: 10px 0 0 0; font-size: 20px; color: #666; font-weight: 500;">
                        현재가: {price:
