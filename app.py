import streamlit as st
import requests
import pandas as pd
import re

# --- 1. 페이지 설정 및 API 키 로드 ---
st.set_page_config(page_title="최저가 검색기", layout="wide")

CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID", "").strip()
CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET", "").strip()

# --- 2. 기능 함수 정의 ---

def get_shopping_data(keyword):
    # 네이버 쇼핑 검색 API 엔드포인트 (v1 경로 포함 필수)
    url = "https://openapi.naver.com"
    
    # 정렬 옵션: sim(유사도), date(날짜), asc(가격오름차순), dsc(가격내림차순)
    params = {"query": keyword, "display": 50, "sort": "asc"}
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "User-Agent": "Mozilla/5.0"
    }
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        
        if res.status_code == 200:
            return res.json().get('items', [])
        else:
            # 상세 에러 메시지 출력
            st.error(f"❌ 네이버 API 에러 (코드: {res.status_code})")
            st.info(f"원인: {res.text}")
            return []
            
    except Exception as e:
        st.error(f"⚠️ 연결 중 오류 발생: {str(e)}")
        return []

def clean_html(text):
    """HTML 태그(<b> 등)를 깔끔하게 제거합니다."""
    return re.sub('<[^<]+?>', '', text)

# --- 3. GUI 화면 구성 ---

st.title("🔍 실시간 네이버 쇼핑 최저가 검색")

# API 키 누락 시 경고
if not CLIENT_ID or not CLIENT_SECRET:
    st.error("⚠️ Streamlit Secrets에 네이버 API 키가 설정되지 않았습니다.")
    st.info(".streamlit/secrets.toml 파일에 NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 입력해주세요.")
    st.stop()

# 사이드바 설정
with st.sidebar:
    st.header("🛒 검색 조건")
    query = st.text_input("상품명을 입력하세요", value="모션데스크 1800")
    price_limit = st.number_input("최대 예산 (원)", min_value=0, value=1500000, step=10000)
    search_button = st.button("최저가 검색 시작")

# 검색 버튼 클릭 시 로직
if search_button and query:
    with st.spinner('데이터를 가져오는 중...'):
        items = get_shopping_data(query)
        
        if items:
            data = []
            for i in items:
                try:
                    price = int(i['lprice'])
                    if price <= price_limit:
                        data.append({
                            "상품명": clean_html(i['title']),
                            "최저가(원)": price,
                            "판매처": i['mallName'],
                            "링크": i['link']
                        })
                except:
                    continue
            
            if data:
                st.success(f"✅ 예산 내 상품 총 {len(data)}건을 찾았습니다.")
                
                # 데이터프레임 시각화
                df = pd.DataFrame(data)
                st.dataframe(
                    df, 
                    column_config={
                        "링크": st.column_config.LinkColumn("구매 링크"),
                        "최저가(원)": st.column_config.NumberColumn(format="%d원")
                    }, 
                    hide_index=True, 
                    use_container_width=True
                )
            else:
                st.warning("⚠️ 예산 범위 내에 상품이 없습니다.")
        else:
            st.info("검색 결과가 없습니다.")
