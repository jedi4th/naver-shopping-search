import streamlit as st
import requests
import pandas as pd
import re

# --- 1. 페이지 설정 및 Secrets 로드 ---
st.set_page_config(page_title="최저가 검색기", layout="wide")

# Secrets에서 키 가져오기 (공백 제거 포함)
try:
    CLIENT_ID = st.secrets["NAVER_CLIENT_ID"].strip()
    CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"].strip()
except Exception:
    st.error("❌ Streamlit Cloud 설정(Settings > Secrets)에 API 키를 등록해주세요.")
    st.stop()

# --- 2. 데이터 조회 함수 ---
def get_shopping_data(keyword):
    # ✅ 주소 확인: 끝에 공백이나 슬래시가 없는지 확인하세요.
    url = "https://openapi.naver.com"
    
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "User-Agent": "Mozilla/5.0"
    }
    params = {"query": keyword, "display": 50, "sort": "asc"}
    
    try:
        # 응답 대기 시간(timeout) 설정
        res = requests.get(url, headers=headers, params=params, timeout=10)
        
        # 🔍 디버깅용: 응답이 JSON이 아닐 경우 실제 내용을 화면에 출력
        if res.status_code != 200:
            st.error(f"❌ 네이버 에러 (코드: {res.status_code})")
            st.info(f"실제 응답 내용: {res.text}") # 👈 여기서 404나 401 원인이 나옵니다.
            return []
            
        # 응답 데이터가 있는지 확인
        if not res.text.strip():
            st.error("⚠️ 네이버에서 빈 응답을 보냈습니다.")
            return []
            
        return res.json().get('items', [])
        
    except requests.exceptions.JSONDecodeError:
        st.error("⚠️ [JSON 에러] 네이버가 JSON이 아닌 데이터를 보냈습니다.")
        st.code(res.text[:500]) # 응답 앞부분 출력
        return []
    except Exception as e:
        st.error(f"⚠️ 연결 오류 발생: {str(e)}")
        return []

# --- 3. 메인 UI ---
st.title("🔍 네이버 쇼핑 최저가 검색")

with st.sidebar:
    st.header("⚙️ 검색 설정")
    query = st.text_input("상품명", value="모션데스크")
    price_limit = st.number_input("최대 예산", value=1500000)
    search_button = st.button("검색 시작")

if search_button and query:
    with st.spinner("데이터를 가져오는 중..."):
        items = get_shopping_data(query)
        
        if items:
            data = []
            for i in items:
                try:
                    price = int(i.get('lprice', 0))
                    if price <= price_limit:
                        title = re.sub('<[^<]+?>', '', i['title'])
                        data.append({
                            "상품명": title,
                            "가격": price,
                            "판매처": i['mallName'],
                            "링크": i['link']
                        })
                except: continue
            
            if data:
                st.success(f"✅ {len(data)}건의 상품을 찾았습니다.")
                st.dataframe(pd.DataFrame(data), use_container_width=True)
            else:
                st.warning("조건에 맞는 상품이 없습니다.")
