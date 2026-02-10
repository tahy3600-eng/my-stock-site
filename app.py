import streamlit as st
import yfinance as yf

# 1. 페이지 설정
st.set_page_config(
    page_title="미국 증시 전고점 실시간",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 제목 및 설명
st.title("📈 주요 지수 전고점 대비 등락")
st.write("지난 1년(52주)의 최고치인 **전고점** 대비 현재 지수의 위치를 실시간으로 분석합니다.")

# 2. 데이터 가져오기 함수
@st.cache_data(ttl=60)
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
    except Exception:
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
        # [수정] 지수 이름을 카드 밖 상단에 50px 크기로 배치
        title_style = "text-align: center; color: #333; font-size: 50px; font-weight: bold; margin-bottom: 10px;"
        st.markdown(f"<h1 style='{title_style}'>{name}</h1>", unsafe_allow_html=True)
        
        # 색상 결정 (상승 빨강 / 하락 파랑)
        color = "#FF0000" if rate >= 0 else "#0000FF"
        
        # [수정] 카드 내부 HTML (P 단위 제거 및 깔끔한 정리)
        card_html = f"""
            <div style="
                background-color: #f8f9fa; 
                padding: 25px; 
                border-radius: 15px; 
                text-align: center;
                border: 2px solid #eee;
                margin-bottom: 20px;
            ">
                <p style="margin: 0; font-size: 16px; color: #666;">현재가: {price:,.2f}</p>
                <h1 style="margin: 10px 0; color: {color}; font-size: 50px; font-weight: bold;">
                    {rate:+.2f}%
                </h1>
                <hr style="border: 0.5px solid #ddd;">
                <p style="margin: 5px 0; font-size: 18px; color: #333;"><b>전고점:</b> {high_val:,.2f}</p>
                <p style="margin: 0; font-size: 13px; color: #888;">(달성일: {high_date})</p>
            </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

st.divider()
st.caption("※ 모든 데이터는 Yahoo Finance 실시간 시세를 바탕으로 하며, 최근 52주 신고가(고점) 대비 현재 위치를 산출한 결과입니다.")

