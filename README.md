# RAG 기반 신용카드 추천 시스템

사용자의 자연어 질문에 따라 최적의 신용카드를 추천해주는 RAG(Retrieval-Augmented Generation) 기반 시스템입니다.

## 주요 기능

| 구성 요소      | 설명                                                              |
| -------------- | ----------------------------------------------------------------- |
| 카드 정보 수집 | 카드고릴라에서 크롤링한 카드 혜택 정보(JSON)                      |
| 문서 임베딩    | OpenAI 임베딩 모델(text-embedding-3-small) 사용, Chroma DB에 저장 |
| 유사 카드 검색 | 사용자 질문을 임베딩 → 유사한 카드 정보 검색 (코사인 유사도 기반) |
| 응답 생성      | LangChain 기반 LLM 체인으로 카드 추천 응답 생성                   |
| Streamlit UI   | 자연어 질문 입력 → 카드 추천 결과 시각화                          |
| RAGAS 평가     | faithfulness, answer_relevancy 기반 추천 품질 정량 평가           |

## 프로젝트 구조

```
├── app/
│   ├── app.py               # Streamlit 앱 실행 파일
│   └── evaluation.py        # RAGAS 평가 실행 파일
│
├── crawling/
│   └── crawling.py          # 카드 정보 크롤링 코드
│
├── data/
│   ├── raw/                 # 크롤링된 카드 JSON 데이터
│   └── chroma_db/           # 벡터 DB 저장 디렉토리
│
├── embedding/
│   └── embedding.py         # 문서 임베딩 및 Chroma 저장 코드
│
├── rag/
│   ├── rag_chain.py         # RAG 체인 구성 코드
│   └── retriever.py         # Chroma 리트리버 설정 코드
│
├── README.md
└── requirements.txt

```

## 실행 방법

1. 의존성 설치

```
   pip install -r requirements.txt
```

2. 임베딩 수행

```
   python embedding/embedding.py
```

3. Streamlit 앱 실행

```
   streamlit run app/app.py
```

## 질문 예시

```
- 대중교통 할인 많이 되는 카드 알려줘
- 스트리밍 서비스 혜택 있는 카드 추천해줘
- 연회비 저렴한 카드 중에서 주유 혜택 있는 카드 알려줘
```

## 평가 지표

RAGAS 기반 정량 평가 수행:

| 지표             | 설명                               |
| ---------------- | ---------------------------------- |
| faithfulness     | 응답이 context와 얼마나 일치하는가 |
| answer_relevancy | 질문에 얼마나 관련된 응답인가      |

## 사용 기술

| 항목          | 내용                                                                                                                         |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **Language**  | ![Python](https://img.shields.io/badge/Python-265573?style=for-the-badge&logo=python&logoColor=white)                        |
| **Crawling**  | ![Selenium](https://img.shields.io/badge/Selenium-67BF4E?style=for-the-badge&logo=selenium&logoColor=white)                  |
| **Embedding** | ![TEXT-EMBEDDING-3-LARGE](https://img.shields.io/badge/TEXT--EMBEDDING--3--small-353535?style=for-the-badge&logoColor=white) |
| **LLM Model** | ![gpt-4.1](https://img.shields.io/badge/gpt--4.1-4B91FF?style=for-the-badge&logo=openai&logoColor=white)                     |
| **Tool**      | ![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)                                 |
| **Vector DB** | ![Chroma](https://img.shields.io/badge/ChromaDB-ff5c83?style=for-the-badge&logo=databricks&logoColor=white)                  |
