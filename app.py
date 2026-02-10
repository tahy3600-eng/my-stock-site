import streamlit as st
import yfinance as yf

# 1. [SEO 보강] 페이지 설정 (검색 엔진에 노출될 정보)
st.set_page_config(
    page_title="미국 증시 전고점 실시간 | 52주 신고가 등락률 실시간 확인", # 검색창에 뜨는 제목
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# [SEO 보강] 검색 로봇을 위한 보이지 않는 설명 (메타 설명 대신 상단 배치)
st.markdown("""
    <p style="display:none;">나스닥, S&P500, 다우존스 지수의 52주 신고가 대비 현재 하락률과 전고점 달성일을 실시간으로 제공하는 대시보드입니다.</p>
""", unsafe_allow_html=True)

# 제목 및 자연스러운 설명
st.title("📈 주요 지수 전고점 대비 등락")
st.write("지난 1년(52주)의 최고치인 **'전고점'** 대비 현재 지수의 위치를 실시간으로 분석합니다.")

# 2. 데이터 가져오기 함수 (52주 기준)
@st.cache_data(ttl=60)
def get_market_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1y") # 52주(1년) 데이터
        if df.empty:
            return 0.0, 0.0, 0.0, "N/A"
            
        high_val = df['High'].max() # 52주 신고가
        high_date = df['High'].idxmax().strftime('%Y-%m-%d') # 달성 날짜
        current = df['Close'].iloc[-1] # 현재가
        rate = ((current - high_val) / high_val) * 100 # 등락률
        
        return current, high_val, rate, high_date
    except Exception as e:
        return 0.0, 0.0, 0.0, "데이터 오류"

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
        
        # 한국식 색상 (상승:빨강, 하락:파랑)
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

st.divider()
st.caption("※ 모든 데이터는 Yahoo Finance 실시간 시세를 기준으로 하며 52주 데이터를 활용합니다.")

