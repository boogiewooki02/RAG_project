from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from rag.retriever import retriever

prompt_template = PromptTemplate(
    template="""
당신은 카드 추천 전문가입니다. 
주어진 Context를 바탕으로 질문에 답변해주세요.
Context에 질문에 대한 명확한 정보가 없을 경우 "관련 정보가 없습니다."라고 답변해주세요.
절대 Context에 없는 내용을 추측하거나 일반 상식을 이용해 답을 만들어서 대답하지 않습니다.

Context:{context}

질문: {question}

각 카드는 아래 형식으로 구분해주세요.
---
- 카드명: [카드명]
- 카드사: [카드사]
- 연회비: [연회비]
- 혜택: [혜택 요약]
- 카드 자세히 보기: [URL]
---
""",
    input_variables=["context", "question"]
)

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt_template
    | llm
    | StrOutputParser()
)