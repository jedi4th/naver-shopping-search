import streamlit as st
import requests
import pandas as pd
import re

# 페이지 설정
st.set_page_config(page_title="네이버 최저가 검색기", layout="wide")

# 1. Secrets 로드 확인 (에러 방지)
try:
    CLIENT_ID = st.secrets["NAVER_CLIENT_ID"].strip()
    CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"].strip()
except KeyError:
    st.error("❌ Streamlit Cloud의 Settings -> Secrets에 API 키를 등록해주세요.")
    st.stop()

def get_shopping_data(keyword):
    # 정확한 쇼핑 API 주소
    url = "https://openapi.naver.com"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
    }
    params = {"query": keyword, "display": 50, "sort": "asc"}
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        
        # ⚠️ 성공(200)이 아닐 경우 텍스트로 에러 원인 출력 후 중단
        if res.status_code != 200:
            st.error(f"❌ 네이버 API 에러 (코드: {res.status_code})")
            st.info(f"상세 원인: {res.text}") # 여기서 401(인증실패) 등이 표시됨
            return []
            
        # JSON 변환 전 데이터 유무 확인
        if not res.text:
            return []
            
        return res.json().get('items', [])
        
    except Exception as e:
        st.error(f"⚠️ 연결 오류: {str(e)}")
        return []

# --- GUI 구성 ---
st.title("🔍 실시간 최저가 검색 (Streamlit Cloud)")

with st.sidebar:
    query = st.text_input("상품명", value="모션데스크")
    price_limit = st.number_input("최대 예산", value=1000000)
    search_button = st.button("검색 실행")

if search_button and query:
    with st.spinner("데이터 조회 중..."):
        items = get_shopping_data(query)
        if items:
            results = []
            for i in items:
                price = int(i.get('lprice', 0))
                if price <= price_limit:
                    results.append({
                        "상품명": re.sub('<[^<]+?>', '', i['title']),
                        "가격": price,
                        "판매처": i['mallName'],
                        "링크": i['link']
                    })
            if results:
                st.dataframe(pd.DataFrame(results), use_container_width=True)
            else:
                st.warning("예산 내 상품이 없습니다.")
