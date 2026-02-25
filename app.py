import streamlit as st
import requests
import pandas as pd

# 1. API 키 설정 (공백 제거 필수)
CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID", "").strip()
CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET", "").strip()

def get_shopping_data(keyword):
    # API 주소 (가장 표준적인 규격)
    url = "https://openapi.naver.com"
    
    # 검색 조건
    params = {
        "query": keyword,
        "display": 50,
        "sort": "asc"
    }
    
    # ⚠️ 핵심: 네이버 차단을 피하기 위한 '진짜 브라우저' 위장 헤더
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json"
    }
    
    try:
        # requests가 주소를 안전하게 자동 조립하도록 설정
        res = requests.get(url, headers=headers, params=params, timeout=15)
        
        # 성공(200)일 때만 데이터 처리
        if res.status_code == 200:
            return res.json().get('items', [])
        else:
            # ⚠️ 에러 발생 시 HTML 코드가 아닌 '진짜 이유'를 텍스트로 출력
            st.error(f"❌ 네이버 응답 에러 (코드: {res.status_code})")
            # 에러 원인이 담긴 텍스트를 출력하여 원인 파악 (예: 403 Forbidden 등)
            with st.expander("🔍 상세 에러 내용 보기"):
                st.write(res.text)
            return []
            
    except Exception as e:
        st.error(f"⚠️ 연결 오류 발생: {str(e)}")
        return []

# --- GUI 구성 (사이드바 형태) ---
st.set_page_config(page_title="최저가 검색기", layout="wide")
st.title("🔍 네이버 쇼핑 실시간 최저가 검색")

if not CLIENT_ID or not CLIENT_SECRET:
    st.error("⚠️ Streamlit Secrets에 API 키가 설정되지 않았습니다.")
    st.stop()

with st.sidebar:
    st.header("🛒 검색 조건")
    query = st.text_input("상품명을 입력하세요", value="모션데스크 1800")
    price_limit = st.number_input("최대 예산 (원)", min_value=0, value=1500000)
    search_button = st.button("최저가 검색 시작")

if search_button and query:
    with st.spinner('네이버 데이터를 분석 중입니다...'):
        items = get_shopping_data(query)
        if items:
            data = []
            for i in items:
                try:
                    price = int(i['lprice'])
                    if price <= price_limit:
                        title = i['title'].replace("<b>", "").replace("</b>", "")
                        data.append({
                            "상품명": title,
                            "최저가(원)": price,
                            "판매처": i['mallName'],
                            "링크": i['link']
                        })
                except: continue
            
            if data:
                st.success(f"✅ 총 {len(data)}건을 찾았습니다!")
                st.dataframe(pd.DataFrame(data), column_config={"링크": st.column_config.LinkColumn("구매")}, hide_index=True, use_container_width=True)
            else:
                st.warning("⚠️ 예산 내 상품이 없습니다.")
        else:
            # 에러 메시지는 get_shopping_data 함수 내부에서 st.error로 출력됩니다.
            pass
