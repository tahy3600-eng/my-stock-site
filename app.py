import streamlit as st
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="증시 전고점 현황", layout="wide")

st.title("📈 주요 지수 전고점 대비 등락")
st.write("최근 52주(1년) 신고가를 '전고점' 기준으로 하여 현재 위치를 표시합니다.")

# 2. 데이터 가져오기 함수 (52주 기준)
@st.cache_data(ttl=60)
def get_market_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # 52주 신고가를 위해 최근 1년(1y) 데이터를 가져옴
        df = ticker.history(period="1y")
        if df.empty:
            return 0.0, 0.0, 0.0, "N/A"
            
        # 52주 최고가(전고점) 및 해당 날짜 찾기
        high_val = df['High'].max()
        high_date = df['High'].idxmax().strftime('%Y-%m-%d') # 신고가 달성 날짜
        
        current = df['Close'].iloc[-1]
        rate = ((current - high_val) / high_val) * 100
        
        return current, high_val, rate, high_date
    except Exception as e:
        return 0.0, 0.0, 0.0, "데이터 오류"

# 3. 지수 목록 (나스닥, S&P500, 다우)
indices = {
    "나스닥 100": "^NDX",
    "S&P 500": "^GSPC",
    "다우 존스": "^DJI"
}

# 4. 화면 구성 (3개의 열)
cols = st.columns(3)

for i, (name, symbol) in enumerate(indices.items()):
    price, high_val, rate, high_date = get_market_data(symbol)
    
    with cols[i]:
        st.subheader(name)
        
        # 한국식 색상 (상승/보합: 빨강, 하락: 파랑)
        color = "#FF0000" if rate >= 0 else "#0000FF"
        
        # 정보 카드 (HTML 스타일 적용)
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

st.divider()
st.caption("※ 모든 수치는 최근 52주 데이터를 기준으로 계산되었습니다.")

