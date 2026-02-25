import streamlit as st
import requests
import pandas as pd

# 1. API 키 설정 (Streamlit Secrets에서 가져오기)
CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID", "").strip()
CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET", "").strip()

def get_shopping_data(keyword):
    # 네이버 쇼핑 검색 API 표준 주소
    url = "https://openapi.naver.com"
    
    params = {
        "query": keyword,
        "display": 50,
        "sort": "asc"
    }
    
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "User-Agent": "Mozilla/5.0", # 일반 브라우저처럼 보이게 설정
        "Accept": "*/*"
    }
    
    try:
        # 응답을 받되 바로 JSON으로 바꾸지 않고 대기
        res = requests.get(url, headers=headers, params=params, timeout=10)
        
        # 성공(200)일 때만 데이터로 처리
        if res.status_code == 200:
            return res.json().get('items', [])
        else:
            # ⚠️ 여기가 핵심: 에러가 나면 네이버가 보낸 진짜 '글자'들을 화면에 보여줍니다.
            st.error(f"❌ 네이버 응답 에러 (코드: {res.status_code})")
            # HTML 코드를 텍스트로 출력하여 원인 파악 (예: 403 Forbidden 등)
            st.text_area("🔍 상세 에러 원인 (이 내용을 확인해 보세요)", value=res.text, height=200)
            return []
            
    except Exception as e:
        st.error(f"⚠️ 연결 오류 발생: {str(e)}")
        return []

# --- GUI 구성 (사이드바 형태) ---
st.set_page_config(page_title="최저가 검색기", layout="wide")
st.title("🔍 실시간 네이버 쇼핑 최저가 검색")

# API 키가 설정되지 않은 경우 안내
if not CLIENT_ID or not CLIENT_SECRET:
    st.error("⚠️ Streamlit Secrets에 API 키가 설정되지 않았습니다.")
    st.info("오른쪽 하단 [Manage app] -> [Settings] -> [Secrets]에 키를 넣으셨나요?")
    st.stop()

with st.sidebar:
    st.header("🛒 검색 필터")
    query = st.text_input("상품명을 입력하세요", value="모션데스크 1800")
    price_limit = st.number_input("최대 예산 (원)", min_value=0, value=1500000, step=10000)
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
                        data.append({"상품명": title, "최저가(원)": price, "판매처": i['mallName'], "링크": i['link']})
                except: continue
            
            if data:
                st.success(f"총 {len(data)}건의 최저가 상품 발견!")
                st.dataframe(pd.DataFrame(data), column_config={"링크": st.column_config.LinkColumn("구매")}, hide_index=True, use_container_width=True)
            else:
                st.warning("설정한 예산 내에 상품이 없습니다.")
