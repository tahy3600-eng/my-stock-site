import streamlit as st
import yfinance as yf
import time

# 1. 페이지 설정
st.set_page_config(
    page_title="미국 증시 전고점 실시간",
    page_icon="📈",
    layout="wide"
)

# 2. 데이터 가져오기 함수 (캐시를 1초로 설정하거나 제거)
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

# 3. 메인 화면 구성
st.title("📈 주요 지수 실시간 전고점 추적")

# 4. [핵심] 5초마다 이 부분만 다시 실행 (st.fragment)
@st.fragment(run_every="5s")
def update_dashboard():
    indices = {
        "나스닥 100": "^NDX",
        "S&P 500": "^GSPC",
        "다우 존스": "^DJI"
    }
    
    cols = st.columns(3)
    for i, (name, symbol) in enumerate(indices.items()):
        price, high_val, rate, high_date = get_market_data(symbol)
        
        with cols[i]:
            st.subheader(name)
            color = "#FF0000" if rate >= 0 else "#0000FF"
            
            st.markdown(f"""
                <div style="
                    background-color: #f8f9fa; 
                    padding: 25px; 
                    border-radius: 15px; 
                    text-align: center;
                    border: 2px solid #eee;
                ">
                    <p style="margin: 0; font-size: 16px; color: #666;">현재가: {price:,.2f} P</p>
                    <h1 style="margin: 10px 0; color: {color}; font-size: 50px; font-weight: bold;">
                        {rate:+.2f}%
                    </h1>
                    <hr style="border: 0.5px solid #ddd;">
                    <p style="margin: 5px 0; font-size: 18px; color: #333;"><b>전고점:</b> {high_val:,.2f} P</p>
                    <p style="margin: 0; font-size: 13px; color: #888;">(달성일: {high_date})</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.caption(f"🕒 마지막 업데이트: {time.strftime('%H:%M:%S')} (5초마다 자동 갱신)")

# 함수 실행
update_dashboard()

st.divider()
st.caption("※ 본 지표는 **Yahoo Finance 실시간 시세**를 바탕으로 하며, **최근 52주 신고가(고점)** 대비 현재 위치를 산출한 결과입니다.")
