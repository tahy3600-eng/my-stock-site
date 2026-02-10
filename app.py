import streamlit as st
import yfinance as yf
import time

# 1. 페이지 설정
st.set_page_config(
    page_title="미국 증시 실시간 추적기",
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
st.write("지난 1년(52주)의 최고치인 **'전고점'** 대비 현재 위치를 10초마다 분석합니다.")

# 4. 실시간 업데이트 영역
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
            # 안전한 출력을 위해 HTML 문자열을 변수에 담아 실행
            html_content = f"""
            <div style="
                background-color: #f8f9fa; 
                padding: 35px 20px; 
                border-radius: 20px; 
                text-align: center;
                border: 2px solid #eee;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
            ">
                <h2 style="margin: 0 0 15px 0; font-size: 36px; color: #222; font-weight: 800;">
                    {name}
                </h2>
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
            st.markdown(html_content, unsafe_allow_html=True)
            
    st.write(f"⏱️ 마지막 갱신: {time.strftime('%H:%M:%S')} (10초 주기)")

# 실행
update_dashboard()

st.divider()
st.caption("※ 본 지표는 **Yahoo Finance 실시간 시세**를 바탕으로 하며, **최근 52주 신고가(고점)** 대비 현재 위치를 산출한 결과입니다.")
