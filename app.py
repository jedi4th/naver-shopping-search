import streamlit as st
import requests
import pandas as pd

# 1. Streamlit Secrets에서 API 키 가져오기
# (설정에서 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET을 미리 입력해야 합니다)
try:
    CLIENT_ID = st.secrets["NAVER_CLIENT_ID"].strip()
    CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"].strip()
except KeyError:
    st.error("❌ Streamlit Secrets 설정에 API 키가 없습니다. [Settings] -> [Secrets]를 확인하세요.")
    st.stop()

def get_shopping_data(keyword):
    # 네이버 쇼핑 검색 API 주소
    url = "https://openapi.naver.com"
    
    # 검색 파라미터 (최저가순: asc)
    params = {
        "query": keyword.strip(),
        "display": 50,
        "sort": "asc"
    }
    
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    
    try:
        # API 호출
        res = requests.get(url, headers=headers, params=params, timeout=10)
        
        if res.status_code == 200:
            # 성공 시 데이터 반환
            return res.json().get('items', [])
        else:
            # 실패 시 네이버가 보내는 상세 에러 메시지 출력
            st.error(f"❌ 네이버 에러 코드: {res.status_code}")
            st.write(f"🔍 상세 원인: {res.text}")
            return []
            
    except Exception as e:
        st.error(f"⚠️ 네트워크 연결 오류: {e}")
        return []

# --- 2. GUI 화면 구성 (왼쪽 사이드바 형태) ---
st.set_page_config(page_title="최저가 검색기", layout="wide")
st.title("🔍 네이버 쇼핑 실시간 최저가 검색")

# 왼쪽 사이드바 입력창
with st.sidebar:
    st.header("🛒 검색 필터")
    search_query = st.text_input("상품명을 입력하세요", value="모션데스크 1800")
    max_price = st.number_input("최대 예산 (원)", min_value=0, value=1500000, step=10000)
    search_button = st.button("최저가 검색 시작")

# --- 3. 검색 결과 처리 로직 ---
if search_button and search_query:
    with st.spinner('실시간 최저가 데이터를 가져오는 중...'):
        items = get_shopping_data(search_query)
        
        if items:
            processed_data = []
            for item in items:
                # 최저가 필터링 (lprice는 문자열로 올 수 있어 int 변환 필요)
                try:
                    lprice = int(item['lprice'])
                except ValueError:
                    continue
                
                if lprice <= max_price:
                    # 제목에서 <b> 태그 제거
                    title = item['title'].replace("<b>", "").replace("</b>", "")
                    processed_data.append({
                        "상품명": title,
                        "가격(원)": lprice,
                        "판매처": item['mallName'],
                        "링크": item['link']
                    })
            
            if processed_data:
                df = pd.DataFrame(processed_data)
                st.success(f"✅ '{search_query}' 검색 완료! (총 {len(df)}건 발견)")
                
                # 결과 테이블 출력 (링크는 클릭 가능하게 설정)
                st.dataframe(
                    df, 
                    column_config={"링크": st.column_config.LinkColumn("구매 링크 바로가기")},
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.warning("⚠️ 설정하신 예산 범위 내에 검색 결과가 없습니다.")
        else:
            # 검색 결과가 아예 없거나 API 오류인 경우 위에서 에러 메시지가 뜹니다.
            pass
