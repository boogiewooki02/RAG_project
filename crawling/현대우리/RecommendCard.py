'''
chain 구성 및 카드 추천.py
'''
import os
from dotenv import load_dotenv

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from FlagEmbedding import FlagReranker

import torch
from textwrap import dedent

# 환경 변수 로드
load_dotenv()


# 1. 임베딩 모델 설정
# embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
embedding_model = HuggingFaceEmbeddings(
    model_name="dragonkue/BGE-m3-ko",
    model_kwargs={"decive":"cpu" if torch.cuda.is_available() else "cpu"},
    encode_kwargs={"normalize_embeddings":True} 
)


# Chroma retrieve 설정
persist_dir = "./chroma_card_db"
db = Chroma(
    persist_directory=persist_dir,
    embedding_function=embedding_model
)
retriever = db.as_retriever(search_kwargs={"k":5})


# re-ranker model 로드
reranker = FlagReranker("dragonkue/bge-reranker-v2-m3-ko")


# RAG 단계별 처리 함수
def retrieve_docs(query):
    return {"query":query, "docs": retriever.get_relevant_documents(query)}

def rerank_docs(inputs: dict):
    query = inputs["query"]
    docs = inputs["docs"]
    reranked = reranker.rerank(query, docs, top_k=2)

    return {"query": query, "docs":reranked}

def format_docs(docs):
    return"\n\n---\n\n".join([doc.page_content for doc in docs])


# 프롬프트 템플릿 정의
prompt = ChatPromptTemplate.from_messages([
    ("system",dedent("""
    당신은 개인의 소비 성향과 필요에 따라 최적의 신용카드를 추천해주는 AI 챗봇입니다.

    당신에게는 다음 두 가지 정보가 주어집니다:
    1. 사용자의 질문 또는 소비 패턴 설명 (예: "주유 혜택 많은 카드 추천", "외식과 편의점 자주 씀")
    2. 카드별 혜택과 유의사항이 담긴 카드 정보 목록

    카드 정보를 바탕으로 사용자의 요구에 가장 잘 부합하는 **신용카드 1~2개를 추천**해 주세요. 추천 시 다음을 따르세요:

    - 카드 이름을 정확히 명시하세요.
    - 해당 카드가 사용자의 소비 패턴과 어떻게 잘 맞는지 **명확한 이유를 들어 설명**하세요.
    - 주요 혜택과 유의사항을 요약하세요.
    - **과도한 설명이나 불필요한 반복 없이** 3~5줄 이내로 정리하세요.
    - 카드 정보에 없는 내용은 생성하지 마세요.

    카드 정보는 이미 사전 필터링되어 있으므로, 가장 적합한 카드만 추천하면 됩니다.
    """)),
    ("human", "사용자 질문: {question}\n\n카드정보:\n{context}")
])


# LLM 모델 설정
llm = ChatOpenAI(model="gpt-4.1")


# 전체 RAG 체인 구성
rag_chain = (
    RunnableLambda(retrieve_docs)
    | RunnableLambda(rerank_docs)
    | RunnableLambda(format_docs)
    | prompt
    | llm
    | StrOutputParser()
)


# 7. LLM 응답 생성
if __name__ == "__main__":
    user_query = input("사용자 질문을 입력하세요: ")
    result = rag_chain.invoke(user_query)
    print("\n추천 결과:\n")
    print(result)