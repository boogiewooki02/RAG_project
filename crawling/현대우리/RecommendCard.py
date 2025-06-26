import os
import openai
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

# Chroma DB 위치
persist_dir = "./chroma_card_db"

# 1. 임베딩 모델 설정 (text-embedding-3-small)
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# 2. GPT 설정
llm = ChatOpenAI(model="gpt-4.1")

# 3. Chroma 벡터 DB 로드
db = Chroma(
    persist_directory=persist_dir,
    embedding_function=embedding_model
)

# 4. 사용자 질문 입력 받기
query = input("사용자 질문을 입력하세요: ")

# 5. 유사 문서 검색
retrieved_docs = db.similarity_search(query, k=3)

# 6. 문서 내용을 LLM에게 전달할 프롬프트로 구성
context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])

system_prompt = """당신은 신용카드 추천 챗봇입니다. 사용자 질문을 참고하고 아래의 카드 혜택 및 유의사항 정보를 기반으로 가장 적절한 카드를 추천해 주세요.
카드명을 명시하고, 혜택 설명과 유의사항을 요약해서 알려주세요.
"""

messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content=f"사용자 질문: {query}\n\n카드 정보:\n{context}")
]


# 7. LLM 응답 생성
response = llm.invoke(messages)
print("추천 결과:")
print(response.content)