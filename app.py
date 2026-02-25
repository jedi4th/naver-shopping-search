import streamlit as st
import requests
import pandas as pd
import re

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="최저가 검색기", layout="wide")

# --- 2. API 키 로드 ---
CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID", "").strip()
CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET", "").strip()

# --- 3. 데이터 가져오기 함수 ---
def get_shopping_data(keyword):
    # 공식 주소: https://openapi.naver.com
    url = "https://openapi.naver.com"
    
    params = {"query": keyword, "display": 50, "sort": "asc"}
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
    }
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        
        # 🔍 [디버깅] 네이버가 보낸 실제 응답을 화면에 표시
        if res.status_code != 200:
            st.error(f"❌ 네이버 API 호출 실패 (코드: {res.status_code})")
            with st.expander("상세 에러 원인 보기"):
                st.write("네이버 응답 내용:", res.text) # 여기에 진짜 이유가 찍힙니다.
            return []

        return res.json().get('items', [])
        
    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {str(e)}")
        return []

def clean_html(text):
    return re.sub('<[^<]+?>', '', text)

# --- 4. 메인 화면 ---
st.title("🔍 네이버 쇼핑 최저가 검색기")

if not CLIENT_ID or not CLIENT_SECRET:
    st.error("⚠️ Secrets에 API 키가 없습니다.")
    st.stop()

with st.sidebar:
    st.header("🛒 검색 조건")
    query = st.text_input("상품명", value="모션데스크 1800")
    price_limit = st.number_input("최대 예산", value=1500000)
    search_button = st.button("검색 시작")

if search_button and query:
    items = get_shopping_data(query)
    
    if items:
        data = []
        for i in items:
            try:
                price = int(i['lprice'])
                if price <= price_limit:
                    data.append({
                        "상품명": clean_html(i['title']),
                        "가격": price,
                        "몰": i['mallName'],
                        "링크": i['link']
                    })
            except: continue
        
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.warning("예산 내 상품이 없습니다.")
