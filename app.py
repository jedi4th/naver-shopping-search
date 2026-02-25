import streamlit as st
import requests
import pandas as pd

# 1. API 키 설정 (공백 제거 로직 강화)
try:
    CLIENT_ID = st.secrets.get("NAVER_CLIENT_ID", "").strip()
    CLIENT_SECRET = st.secrets.get("NAVER_CLIENT_SECRET", "").strip()
except Exception:
    st.error("❌ Streamlit Secrets 설정에 오류가 있습니다.")
    st.stop()

def get_shopping_data(keyword):
    # API 주소
    url = "https://openapi.naver.com"
    
    # 파라미터 구성
    params = {
        "query": keyword,
        "display": 50,
        "sort": "asc"
    }
    
    # ⚠️ 핵심: 네이버 차단을 피하기 위한 '브라우저 위장' 헤더 설정
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://share.streamlit.io",
        "Referer": "https://share.streamlit.io"
    }
    
    try:
        # 요청 보내기
        res = requests.get(url, headers=headers, params=params, timeout=15)
        
        # 성공 시 데이터 반환
        if res.status_code == 200:
            return res.json().get('items', [])
        else:
            # ⚠️ 에러 발생 시 HTML 코드가 아닌 '진짜 이유'를 텍스트로만 추출하여 출력
            st.error(f"❌ 네이버 응답 에러 (코드: {res.status_code})")
            # 에러 메시지가 HTML인 경우 앞부분만 출력하여 원인 파악
            error_msg = res.text[:500]
            st.code(error_msg, language="html")
            return []
            
    except Exception as e:
        st.error(f"⚠️ 시스템 연결 오류: {str(e)}")
        return []

# --- GUI 구성 (사이드바 형태) ---
st.set_page_config(page_title="최저가 검색기", layout="wide")
st.title("🔍 실시간 네이버 쇼핑 최저가 검색기")

if not CLIENT_ID or not CLIENT_SECRET:
    st.warning("⚠️ Streamlit Secrets에 API 키를 먼저 입력해 주세요.")
    st.stop()

with st.sidebar:
    st.header("🛒 검색 필터")
    query = st.text_input("상품명을 입력하세요", value="모션데스크 1800")
    price_limit = st.number_input("최대 예산 (원)", min_value=0, value=1500000, step=10000)
    search_button = st.button("최저가 검색 시작")

if search_button and query:
    with st.spinner('데이터를 분석 중입니다...'):
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
                            "최저가(원)": price,
                            "판매처": i['mallName'],
                            "링크": i['link']
                        })
                except: continue
            
            if data:
                st.success(f"✅ 총 {len(data)}건의 상품을 찾았습니다!")
                st.dataframe(
                    pd.DataFrame(data), 
                    column_config={"링크": st.column_config.LinkColumn("구매 링크")},
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.warning("⚠️ 설정한 예산 범위 내에 상품이 없습니다.")
        else:
            st.info("💡 검색 결과가 없거나 API 권한 설정 문제입니다.")
