import streamlit as st
import json
import pandas as pd
from urllib.request import Request, urlopen
from urllib.parse import quote, urlencode

# 1. API 키 설정 (공백 제거 포함)
CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID", "").strip()
CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET", "").strip()

def get_shopping_data(keyword):
    # API 주소 및 파라미터 설정
    base_url = "https://openapi.naver.com"
    params = {
        "query": keyword,
        "display": 50,
        "sort": "asc"
    }
    
    # 주소 조립 (URL 인코딩 자동 처리)
    query_string = urlencode(params)
    full_url = f"{base_url}?{query_string}"
    
    # 요청 헤더 구성
    request = Request(full_url)
    request.add_header("X-Naver-Client-Id", CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
    request.add_header("User-Agent", "Mozilla/5.0")
    
    try:
        # urllib을 이용한 직접 호출 (requests 라이브러리 미사용)
        with urlopen(request, timeout=10) as response:
            res_code = response.getcode()
            if res_code == 200:
                response_body = response.read().decode('utf-8')
                return json.loads(response_body).get('items', [])
            else:
                st.error(f"❌ 서버 응답 에러: {res_code}")
                return []
    except Exception as e:
        # 상세 에러 메시지 출력
        st.error(f"⚠️ 연결 오류 상세: {str(e)}")
        st.info("팁: 네이버 개발자 센터에서 '검색' API 권한이 추가되었는지 다시 확인해 보세요.")
        return []

# --- 사이드바 GUI 구성 ---
st.set_page_config(page_title="최저가 검색기", layout="wide")
st.title("🔍 네이버 쇼핑 실시간 최저가 검색기")

if not CLIENT_ID or not CLIENT_SECRET:
    st.error("⚠️ Streamlit Secrets에 API 키가 설정되지 않았습니다.")
    st.stop()

with st.sidebar:
    st.header("🛒 검색 필터")
    search_query = st.text_input("상품명을 입력하세요", value="모션데스크 1800")
    max_price = st.number_input("최대 예산 (원)", min_value=0, value=1500000, step=10000)
    search_button = st.button("최저가 검색 시작")

if search_button and search_query:
    with st.spinner('데이터를 불러오는 중...'):
        items = get_shopping_data(search_query)
        
        if items:
            processed_data = []
            for item in items:
                try:
                    lprice = int(item['lprice'])
                    if lprice <= max_price:
                        title = item['title'].replace("<b>", "").replace("</b>", "")
                        processed_data.append({
                            "상품명": title,
                            "최저가(원)": lprice,
                            "판매처": item['mallName'],
                            "링크": item['link']
                        })
                except: continue
            
            if processed_data:
                df = pd.DataFrame(processed_data)
                st.success(f"검색 성공! 총 {len(df)}건을 찾았습니다.")
                st.dataframe(
                    df, 
                    column_config={"링크": st.column_config.LinkColumn("구매 링크")},
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.warning("예산 범위 내에 상품이 없습니다.")
        else:
            st.info("검색 결과가 없거나 API 권한 문제입니다.")
