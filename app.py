import streamlit as st
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="증시 전고점 현황", layout="wide")

st.title("📈 주요 지수 전고점 대비 등락")

# 2. 데이터 가져오기 함수
@st.cache_data(ttl=60)
def get_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="5y")
        if df.empty:
            return 0, 0, 0
        ath = df['High'].max()
        current = df['Close'].iloc[-1]
        rate = ((current - ath) / ath) * 100
        return current, ath, rate
    except:
        return 0, 0, 0

# 3. 지수 목록
indices = {
    "나스닥 100": "^NDX",
    "S&P 500": "^GSPC",
    "다우 존스": "^DJI"
}

# 4. 화면 구성 (숫자만 크게)
cols = st.columns(3)

for i, (name, symbol) in enumerate(indices.items()):
    price, ath, rate = get_data(symbol)
    
    with cols[i]:
        st.subheader(name)
        
        # 상승/하락에 따른 색상 결정 (상승:빨강, 하락:파랑)
        color = "#FF0000" if rate >= 0 else "#0000FF"
        
        # 현재가 표시
        st.write(f"현재가: **{price:,.2f} P**")
        
        # 하락률/상승률을 아주 크게 표시
        st.markdown(f"""
            <div style="
                background-color: #f8f9fa; 
                padding: 30px; 
                border-radius: 15px; 
                text-align: center;
                border: 2px solid #eee;
            ">
                <p style="margin: 0; font-size: 20px; color: #333;">전고점 대비</p>
                <h1 style="margin: 0; color: {color}; font-size: 60px; font-weight: bold;">
                    {rate:+.2f}%
                </h1>
            </div>
        """, unsafe_allow_html=True)
        
        # 전고점 정보
        st.write(f"전고점: {ath:,.2f} P")

st.divider()
st.caption("데이터: Yahoo Finance | 1분마다 자동 갱신")
import streamlit as st
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(page_title="증시 전고점 현황", layout="wide")

st.title("📈 주요 지수 전고점 대비 등락")
st.write("최근 52주(1년) 신고가를 '전고점' 기준으로 하여 현재 위치를 확인합니다.")

# 2. 데이터 가져오기 함수 (52주 기준)
@st.cache_data(ttl=60)
def get_market_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # 52주 신고가를 위해 최근 1년(1y) 데이터를 가져옴
        df = ticker.history(period="1y")
        if df.empty:
            return 0, 0, 0, "N/A"
            
        # 52주 최고가(전고점) 및 해당 날짜 찾기
        high_52w = df['High'].max()
        high_date = df['High'].idxmax().strftime('%Y-%m-%d') # 신고가 달성 날짜
        
        current = df['Close'].iloc[-1]
        rate = ((current - high_52w) / high_52w) * 100
        
        return current, high_52w, rate, high_date
    except:
        return 0, 0, 0, "오류"

# 3. 지수 목록
indices = {
    "나스닥 100": "^NDX",
    "S&P 500": "^GSPC",
    "다우 존스": "^DJI"
}

# 4. 화면 구성
cols = st.columns(3)

for i, (name, symbol) in enumerate(indices.items()):
    price, high_val, rate, high_date = get_market_data(symbol)
    
    with cols[i]:
        st.subheader(name)
        
        # 한국식 색상 (상승/보합: 빨강, 하락: 파랑)
        color = "#FF0000" if rate >= 0 else "#0000FF"
        
        # 정보 카드 (그래프 없이 숫자 강조)
        st.markdown(f"""
            <div style="
                background-color: #f8f9fa; 
                padding: 25px; 
                border-radius: 15px; 
                text-align: center;
                border: 2px solid #eee;
            ">
                <p style="margin: 0; font-size: 16px; color: #666;">현재가: {price:,.2f} P</p>
                <h1 style="margin: 10px 0; color: {color}; font-size: 55px; font-weight: bold;">
                    {rate:+.2f}%
                </h1>
                <hr style="border: 0.5px solid #ddd;">
                <p style="margin: 5px 0; font-size: 18px; color: #333;"><b>전고점
