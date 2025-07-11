# app.py
# from rag_chain import rag_chain

# question = input("질문을 입력하세요: ")
# response = rag_chain.invoke(question)

# print(response)

import streamlit as st
from rag_chain import rag_chain

st.set_page_config(page_title="신용카드 추천 챗봇", page_icon="💳")

st.title("💳 신용카드 추천 챗봇")
st.write("자연어로 질문하면, 조건에 맞는 카드를 추천해드립니다!")

question = st.text_input("질문을 입력하세요", placeholder="예: 커피 할인 많이 되는 카드 추천해줘")

if st.button("추천받기") and question.strip():
    with st.spinner("카드 추천 중..."):
        response = rag_chain.invoke(question)
    st.markdown("### 📝 추천 결과")
    st.markdown(response)

