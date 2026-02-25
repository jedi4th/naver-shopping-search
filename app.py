import streamlit as st
import requests
import pandas as pd
import re
from urllib.parse import quote

# --- 1. 페이지 설정 및 Secrets 로드 ---
st.set_page_config(page_title="네이버 최저가 검색기", layout="wide")

# Secrets 확인
if "NAVER_CLIENT_ID" not in st.secrets or "NAVER_CLIENT_SECRET" not in st.secrets:
    st.error("❌ Streamlit Cloud의 Settings > Secrets에 API 키를 등록해주세요.")
    st.stop()

CLIENT_ID = st.secrets["NAVER_CLIENT_ID"].strip()
CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"].strip()

# --- 2. 데이터 조회 함수 ---
def get_shopping_data(keyword):
    # ✅ 주소 끝에 공백이나 슬래시가 절대 없어야 합니다.
    url = "https://openapi.naver.com"
    
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Accept": "application/json" # 👈 JSON 응답을 명시적으로 요청
    }
    
    # 파라미터 설정
    params = {
        "query": keyword,
        "display": 50,
        "sort": "asc"
    }
    
    try:
        # verify=True가 기본값이나, 간혹 환경 문제 시 확인 필요
        res = requests.get(url, headers=headers, params=params, timeout=10)
        
        # 🔍 상태 코드가 200이 아니면 리다이렉트된 것임
        if res.status_code != 200:
            st.error(f"❌ 네이버 응답 에러 (코드: {res.status_code})")
            if "text/html" in res.headers.get("Content-Type", ""):
                st.warning("💡 네이버가 데이터 대신 웹페이지를 보냈습니다. URL 주소를 다시 확인하세요.")
            return []
            
        return res.json().get('items', [])
        
    except Exception as e:
        st.error(f"⚠️ 실행 중 오류 발생: {str(e)}")
        return []

# --- 3. 메인 UI ---
st.title("🔍 네이버 쇼핑 실시간 최저가")

with st.sidebar:
    query = st.text_input("상품명 입력", value="모션데스크 1800")
    price_limit = st.number_input("최대 예산(원)", value=1500000, step=10000)
    search_btn = st.button("최저가 검색")

if search_btn and query:
    with st.spinner("네이버 쇼핑 서버 연결 중..."):
        items = get_shopping_data(query)
        
        if items:
            data = []
            for i in items:
                try:
                    price = int(i.get('lprice', 0))
                    if price <= price_limit:
                        # HTML 태그 제거
                        clean_title = re.sub('<[^<]+?>', '', i['title'])
                        data.append({
                            "상품명": clean_title,
                            "최저가(원)": price,
                            "판매처": i['mallName'],
                            "링크": i['link']
                        })
                except: continue
            
            if data:
                st.success(f"✅ 조건에 맞는 상품 {len(data)}건 발견!")
                df = pd.DataFrame(data)
                st.dataframe(
                    df, 
                    column_config={"링크": st.column_config.LinkColumn("바로가기")},
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("해당 가격대의 상품이 없습니다.")
