import streamlit as st
import requests
import pandas as pd

# 1. API 키를 Streamlit 클라우드 설정(Secrets)에서 안전하게 가져오는 설정
CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]

def get_shopping_data(keyword):
    url = "https://openapi.naver.com"
    params = {"query": keyword, "display": 50, "sort": "asc"}
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            return res.json().get('items', [])
        return []
    except:
        return []

# 2. 사용자가 요청한 왼쪽 사이드바 GUI 구성
st.set_page_config(page_title="최저가 검색기", layout="wide")
st.title("🔍 네이버 쇼핑 실시간 최저가 검색")

with st.sidebar:
    st.header("🛒 검색 필터")
    search_query = st.text_input("상품명을 입력하세요", value="모션데스크 1800")
    max_price = st.number_input("최대 예산 (원)", min_value=0, value=1000000, step=10000)
    search_button = st.button("최저가 검색 시작")

# 3. 결과 출력 로직
if search_button and search_query:
    with st.spinner('네이버 데이터를 분석 중입니다...'):
        items = get_shopping_data(search_query)
        if items:
            processed_data = []
            for item in items:
                lprice = int(item['lprice'])
                if lprice <= max_price:
                    title = item['title'].replace("<b>", "").replace("</b>", "")
                    processed_data.append({
                        "상품명": title,
                        "가격(원)": lprice,
                        "판매처": item['mallName'],
                        "링크": item['link']
                    })
            
            if processed_data:
                df = pd.DataFrame(processed_data)
                st.success(f"성공! {len(df)}건의 상품을 찾았습니다.")
                st.dataframe(
                    df, 
                    column_config={"링크": st.column_config.LinkColumn("구매 링크")},
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.warning("설정한 예산 내에 상품이 없습니다.")
        else:
            st.error("데이터를 가져오지 못했습니다. API 설정을 확인해 주세요.")
