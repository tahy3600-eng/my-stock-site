import streamlit as st
import yfinance as yf

# 1. [SEO 보강] 페이지 설정
st.set_page_config(
    page_title="미국 증시 전고점 실시간 | 52주 신고가 등락률 실시간 확인",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# [SEO 보강] 검색 로봇을 위한 보이지 않는 설명
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
        # 1. 지수 이름 크기를 50px로 확대 (퍼센트 크기와 동일)
        st.markdown(f"""
            <h1 style='
                text-
