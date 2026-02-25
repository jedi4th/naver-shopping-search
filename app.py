import streamlit as st
import requests
import pandas as pd

# 1. API 키 설정 (공백 제거 포함)
CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID", "").strip()
CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET", "").strip()

def get_shopping_data(keyword):
    # API 주소 (변수 없이 고정)
    url = "https://openapi.naver.com"
    
    # ⚠️ 핵심: 검색어를 주소에 직접 넣지 않고 params로 전달하면 공백 오류가 해결됩니다.
    params = {
        "query": keyword,
        "display": 50,
        "sort": "asc"
    }
    
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    
    try:
        # requests가 주소를 안전하게 자동 조립합니다.
        res = requests.get(url, headers=headers, params=params, timeout=10)
        
        if res.status_code == 200:
            return res.json().get('items', [])
        else:
            st.error(f"❌ 네이버 에러 (코드: {res.status_code})")
            st.write(f"상세 원인: {res.text}")
            return []
    except Exception as e:
        st.error(f"⚠️ 연결 오류: {e}")
        return []

# --- GUI 구성 (왼쪽 사이드바) ---
st.set_page_config(page_title="최저가 검색기", layout="wide")
st.title("🔍 실시간 네이버 쇼핑 최저가 검색")

if not CLIENT_ID or not CLIENT_SECRET:
    st.error("⚠️ Streamlit Secrets에 API 키를 먼저 설정해 주세요.")
    st.stop()

with st.sidebar:
    st.header("🛒 검색 필터")
    query = st.text_input("상품명을 입력하세요", value="모션데스크 1800")
    price_limit = st.number_input("최대 예산 (원)", min_value=0, value=1500000, step=10000)
    search_button = st.button("최저가 검색 시작")

if search_button and query:
    with st.spinner('데이터를 가져오는 중...'):
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
                            "가격(원)": price,
                            "판매처": i['mallName'],
                            "링크": i['link']
                        })
                except: continue
            
            if data:
                st.success(f"✅ 총 {len(data)}건을 찾았습니다.")
                st.dataframe(
                    pd.DataFrame(data), 
                    column_config={"링크": st.column_config.LinkColumn("구매 바로가기")},
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.warning("⚠️ 예산 내 상품이 없습니다.")
