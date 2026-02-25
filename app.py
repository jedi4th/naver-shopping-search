import streamlit as st
import requests
import pandas as pd
import re

# 1. API 주소 수정
BASE_URL = "https://openapi.naver.com/v1/search/shop.json"

def get_shopping_data(keyword):
    # API 파라미터: sort='sim'(유사도) 또는 'asc'(가격순)
    params = {"query": keyword, "display": 50, "sort": "asc"}
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
    }
    
    try:
        # 수정된 BASE_URL 사용
        res = requests.get(BASE_URL, headers=headers, params=params, timeout=10)
        
        if res.status_code == 200:
            return res.json().get('items', [])
        else:
            st.error(f"❌ 에러 발생: {res.json().get('errorMessage', '알 수 없는 오류')}")
            return []
    except Exception as e:
        st.error(f"⚠️ 연결 오류: {e}")
        return []

# 제목 정제용 함수 (정규표현식 활용)
def clean_title(title):
    return re.sub('<[^<]+?>', '', title)
