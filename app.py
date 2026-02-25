import streamlit as st
import requests
import pandas as pd

# 1. API 키 설정 (오류 방지를 위해 get 메서드 사용)
CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID", "").strip()
CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET", "").strip()

def get_shopping_data(keyword):
    # API 주소 (정확한 규격 확인)
    url = "https://openapi.naver.com"
    
    params = {
        "query": keyword,
        "display": 50,
        "sort": "asc"
    }
    
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*"
    }
    
    try:
        # 세션을 사용하여 통신의 안정성을 높임
        session = requests.Session()
        res = session.get(url, headers=headers, params=params, timeout=10)
        
        if res.status_code == 200:
            return res.json().get('items', [])
        else:
            # 에러 발생 시 네이버가 보내는 실제 HTML/텍스트 내용을 출력하여 원인 파악
            st.error(f"❌ 네이버 응답 에러 (코드: {res.status_code})")
            with st.expander("상세 에러 내용 보기"):
                st.write(res.text)
            return []
            
    except Exception as e:
        st.error(f"⚠️ 연결 오류 발생: {str(e)}")
        return []

# --- GUI 구성 (사이드바 형태) ---
st.set_page_config(page_title="최저가 검색기", layout="wide")
st.title("🔍 실시간 네이버 쇼핑 최저가 검색")

if not CLIENT_ID or not CLIENT_SECRET:
    st.warning("⚠️ 사이드바 하단 'Settings'에서 API 키(Secrets)를 먼저 설정해 주세요.")
    st.stop()

with st.sidebar:
    st.header("🛒 검색 필터")
    query = st.text_input("상품명을 입력하세요", value="모션데스크 1800")
    price_limit = st.number_input("최대 예산 (원)", min_value=0, value=1500000, step=10000)
    search_button = st.button("최저가 검색 시작")

if search_button and query:
    with st.spinner('데이터 분석 중...'):
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
                st.success(f"총 {len(data)}건 발견!")
                st.dataframe(pd.DataFrame(data), column_config={"링크": st.column_config.LinkColumn("구매")}, hide_index=True, use_container_width=True)
            else:
                st.warning("예산 내 상품이 없습니다.")
