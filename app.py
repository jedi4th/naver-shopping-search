import streamlit as st
import requests
import pandas as pd
import re

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="최저가 검색기", layout="wide")

# --- 2. API 키 로드 (Streamlit Secrets) ---
# .streamlit/secrets.toml 파일에 저장되어 있어야 합니다.
CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID", "").strip()
CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET", "").strip()

# --- 3. 데이터 가져오기 함수 ---
def get_shopping_data(keyword):
    # ✅ 중요: v1/search/shop.json 까지 정확히 입력되어야 합니다.
    url = "https://openapi.naver.com"
    
    params = {
        "query": keyword, 
        "display": 50, 
        "sort": "asc"  # 가격 오름차순(최저가순)
    }
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "User-Agent": "Mozilla/5.0"
    }
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        
        # 상태 코드가 200이 아니면 에러 메시지 상세 출력
        if res.status_code != 200:
            st.error(f"❌ 네이버 API 호출 실패 (코드: {res.status_code})")
            st.code(res.text) # 에러의 진짜 이유 확인용
            return []

        # JSON 변환 시도
        return res.json().get('items', [])
        
    except requests.exceptions.JSONDecodeError:
        st.error("⚠️ 네이버 응답이 JSON 형식이 아닙니다. URL 주소를 확인하세요.")
        return []
    except Exception as e:
        st.error(f"⚠️ 시스템 오류 발생: {str(e)}")
        return []

def clean_html(text):
    """상품명에 포함된 <b> 태그 등을 제거"""
    return re.sub('<[^<]+?>', '', text)

# --- 4. 메인 GUI 화면 ---
st.title("🔍 실시간 네이버 쇼핑 최저가 검색")

if not CLIENT_ID or not CLIENT_SECRET:
    st.error("⚠️ [설정 필요] .streamlit/secrets.toml 파일에 API 키를 입력해주세요.")
    st.stop()

# 사이드바 입력창
with st.sidebar:
    st.header("🛒 검색 조건")
    query = st.text_input("상품명을 입력하세요", value="모션데스크 1800")
    price_limit = st.number_input("최대 예산 (원)", min_value=0, value=1500000, step=10000)
    search_button = st.button("최저가 검색 시작")

# 검색 실행
if search_button and query:
    with st.spinner('네이버 쇼핑 데이터를 분석 중입니다...'):
        items = get_shopping_data(query)
        
        if items:
            processed_data = []
            for item in items:
                try:
                    price = int(item['lprice'])
                    if price <= price_limit:
                        processed_data.append({
                            "상품명": clean_html(item['title']),
                            "최저가(원)": price,
                            "판매처": item['mallName'],
                            "링크": item['link']
                        })
                except (ValueError, KeyError):
                    continue
            
            if processed_data:
                st.success(f"✅ 예산 내 상품 {len(processed_data)}건을 발견했습니다.")
                
                df = pd.DataFrame(processed_data)
                # 데이터프레임 출력 설정
                st.dataframe(
                    df, 
                    column_config={
                        "링크": st.column_config.LinkColumn("구매하기"),
                        "최저가(원)": st.column_config.NumberColumn(format="%d원")
                    }, 
                    hide_index=True, 
                    use_container_width=True
                )
            else:
                st.warning(f"⚠️ '{query}' 검색 결과 중 {price_limit:,}원 이하 상품이 없습니다.")
        else:
            st.info("검색 결과가 없거나 API 설정을 확인해야 합니다.")
