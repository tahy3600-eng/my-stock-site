import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
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
        if df.empty:
            return 0.0, 0.0, 0.0, "N/A"

        high_val = df['High'].max()
        high_date = df['High'].idxmax().strftime('%Y-%m-%d')
        current = df['Close'].iloc[-1]
        rate = ((current - high_val) / high_val) * 100
        return current, high_val, rate, high_date
    except:
        return 0.0, 0.0, 0.0, "오류"

def get_vix_data():
    try:
        vix = yf.Ticker("^VIX")
        return vix.history(period="1d")['Close'].iloc[-1]
    except:
        return 0.0

def get_cnn_fear_greed():
    url = "https://www.cnn.com/markets/fear-and-greed"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            score_match = re.search(r'"score":(\d+)', r.text)
            return int(score_match.group(1)) if score_match else 48
        return 48
    except:
        return 48

# 3. 메인 타이틀
st.title("📈 미국 증시 및 시장 심리 실시간 현황")

# 4. 실시간 업데이트
@st.fragment(run_every="10s")
def update_dashboard():
    now_kst = datetime.utcnow() + timedelta(hours=9)
    current_time = now_kst.strftime('%H:%M:%S')

    # --- 구역 1: 주요 지수 ---
    st.markdown("### 🏦 주요 지수 (52주 고점 대비)")
    idx_cols = st.columns(3)

    indices = {
        "나스닥 100": "^NDX",
        "S&P 500": "^GSPC",
        "다우 존스": "^DJI"
    }

    for i, (name, symbol) in enumerate(indices.items()):
        price, high_val, rate, high_date = get_market_data(symbol)
        color = "#FF0000" if rate >= 0 else "#0000FF"

        with idx_cols[i]:
            st.markdown(
                f"<h2 style='text-align:center; font-size:24px; font-weight:800;'>{name}</h2>",
                unsafe_allow_html=True
            )

            st.markdown(f"""
                <div style="
                    background-color:#f8f9fa;
                    padding:25px;
                    border-radius:20px;
                    border:2px solid #eee;
                    min-height:250px;

                    display:flex;
                    flex-direction:column;
                    justify-content:center;
                    align-items:center;
                    text-align:center;
                ">
                    <h1 style="color:{color}; font-size:52px; font-weight:bold; margin:0;">
                        {rate:+.2f}%
                    </h1>
                    <p style="font-size:20px; font-weight:600; margin-top:10px;">
                        현재: {price:,.2f}
                    </p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <p style="text-align:center; font-size:14px; color:#666;">
                    52주 고점: <b>{high_val:,.2f}</b><br>
                    <span style="font-size:12px; color:#aaa;">
                        ({high_date})
                    </span>
                </p>
            """, unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # --- 구역 2: 시장 심리 ---
    st.markdown("### 🕵️ 시장 심리 및 변동성")
    fear_cols = st.columns([0.5, 1, 1, 0.5])

    # VIX
    vix_val = get_vix_data()
    vix_color = "#FF0000" if vix_val >= 20 else "#0000FF"

    with fear_cols[1]:
        st.markdown("<h2 style='text-align:center;'>VIX (공포지수)</h2>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="
                background-color:#f8f9fa;
                padding:25px;
                border-radius:20px;
                border:2px solid #eee;
                min-height:250px;

                display:flex;
                justify-content:center;
                align-items:center;
                text-align:center;
            ">
                <h1 style="color:{vix_color}; font-size:65px; font-weight:bold; margin:0;">
                    {vix_val:.2f}
                </h1>
            </div>
        """, unsafe_allow_html=True)

    # CNN Fear & Greed
    cnn_score = get_cnn_fear_greed()
    cnn_color = "#FF0000" if cnn_score <= 45 else "#666666" if cnn_score <= 55 else "#008000"

    with fear_cols[2]:
        st.markdown("<h2 style='text-align:center;'>CNN Fear & Greed</h2>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="
                background-color:#f8f9fa;
                padding:25px;
                border-radius:20px;
                border:2px solid #eee;
                min-height:250px;

                display:flex;
                justify-content:center;
                align-items:center;
                text-align:center;
            ">
                <h1 style="color:{cnn_color}; font-size:65px; font-weight:bold; margin:0;">
                    {cnn_score}
                </h1>
            </div>
        """, unsafe_allow_html=True)

    # 마지막 업데이트
    st.markdown(f"""
        <div style="text-align:right; margin-top:30px; color:#999; font-size:14px;">
            ⏱️ 마지막 업데이트: {current_time} (한국 시간)
        </div>
    """, unsafe_allow_html=True)

# 실행
update_dashboard()

st.divider()
st.caption("※ 데이터 출처: Yahoo Finance & CNN Business")
