import streamlit as st
import requests
import pandas as pd

# 1. API 키 설정 (오류 방지를 위해 get 메서드 사용)
CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID", "").strip()
CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET", "").strip()

if not CLIENT_ID or not CLIENT_SECRET:
    st.error("❌ Streamlit Secrets에 API 키가 설정되지 않았습니다.")
    st.stop()

def get_shopping_data(keyword):
    # API 주소
    url = "https://openapi.naver.com"
    
    # 검색 조건
    params = {
        "query": keyword,
        "display": 50,
        "sort": "asc"
    }
    
    # 서버 차단을 피하기 위한 헤더 보강 (User-Agent 추가)
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    try:
        # 주소 파싱 오류 방지를 위해 params 옵션 사용
        res = requests.get(url, headers=headers, params=params, timeout=10)
        
        if res.status_code == 200:
            # 정상 응답 시 JSON 변환
            return res.json().get('items', [])
        else:
            # 에러 발생 시 원인 출력 (텍스트가 너무 길면 잘라서 출력)
            st.error(f"❌ 네이버 응답 에러 (코드: {res.status_code})")
            st.code(res.text[:500], language="html") 
            return []
            
    except Exception as e:
        st.error(f"⚠️ 연결 오류 상세: {str(e)}")
        return []

# --- GUI 구성 (사이드바 형태) ---
st.set_page_config(page_title="최저가 검색기", layout="wide")
st.title("🔍 실시간 네이버 쇼핑 최저가 검색")

with st.sidebar:
    st.header("🛒 검색 조건")
    query = st.text_input("상품명을 입력하세요", value="모션데스크 1800")
    price_limit = st.number_input("최대 예산 (원)", min_value=0, value=1500000, step=10000)
    if st.button("최저가 검색 시작"):
        st.session_state.search_clicked = True

# 검색 결과 출력
if st.session_state.get('search_clicked') and query:
    with st.spinner('데이터를 분석 중입니다...'):
        items = get_shopping_data(query)
        if items:
            data = []
            for i in items:
                try:
                    price = int(i['lprice'])
                    if price <= price_limit:
                        data.append({
                            "상품명": i['title'].replace("<b>", "").replace("</b>", ""),
                            "최저가(원)": price,
                            "판매처": i['mallName'],
                            "링크": i['link']
                        })
                except: continue
            
            if data:
                st.success(f"총 {len(data)}건을 찾았습니다.")
                st.dataframe(pd.DataFrame(data), column_config={"링크": st.column_config.LinkColumn("구매")}, hide_index=True, use_container_width=True)
            else:
                st.warning("예산 내 상품이 없습니다.")
