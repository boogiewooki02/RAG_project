# 신용카드 추천 챗봇 시스템

## 🍀 팀명 및 팀원

**팀명**: 신용불량자  
**팀원**: 고범석, 김동욱, 우민규, 홍성의, 홍채우

<table>
  <tr>
    <td><img src="./figure/profile_범석.png" width="250"/></td>
    <td><img src="./figure/profile_동욱.png" width="250"/></td>
    <td><img src="./figure/profile_민규.png" width="250"/></td>
    <td><img src="./figure/profile_성의.png" width="250"/></td>
    <td><img src="./figure/profile_채우.jpg" width="250"/></td>
  </tr>
  <tr>
    <td><a href="https://github.com/qjazk0000">고범석</a></td>
    <td><a href="https://github.com/boogiewooki02">김동욱</a></td>
    <td><a href="https://github.com/mingyu-oo">우민규</a></td>
    <td><a href="https://github.com/seonguihong">홍성의</a></td>
    <td><a href="https://github.com/HCWDDD">홍채우</a></td>
  </tr>
</table>

## 📌 프로젝트 소개

이 프로젝트는 사용자의 질문 한 줄로 최적의 신용카드를 추천해주는 RAG 기반 AI 챗봇입니다.
카드 혜택 정보는 여러 사이트에 분산돼 있고, 각 카드사의 챗봇은 자사 카드만 추천하는 한계가 있습니다.
본 시스템은 여러 카드사의 정보를 통합하고, 자연어 질문에 대해 LLM이 문서 기반으로 응답함으로써 신뢰성 있는 카드 비교/추천을 제공합니다.

| 항목               | 설명                                                                                                                                                       |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 프로젝트 목표      | 사용자 요구에 따른 맞춤형 신용카드를 추천하는 대화형 RAG 기반 챗봇 구축                                                                                    |
| 기존 서비스 한계   | [카드고릴라](https://www.card-gorilla.com): 여러 카드사는 포함되지만 대화형 추천 기능 없음<br>각 카드사 사이트: 대화형 챗봇이 있어도 자사 카드만 추천 가능 |
| 본 시스템의 차별점 | 자연어 기반 대화형 카드 추천<br>여러 카드사 카드 동시 비교 가능                                                                                            |

## 🔨 기술 스택

| 항목                   | 내용                                                                                                                         |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **Language**           | ![Python](https://img.shields.io/badge/Python-265573?style=for-the-badge&logo=python&logoColor=white)                        |
| **Crawler**            | ![Selenium](https://img.shields.io/badge/Selenium-67BF4E?style=for-the-badge&logo=selenium&logoColor=white)                  |
| **Embedding**          | ![TEXT-EMBEDDING-3-LARGE](https://img.shields.io/badge/TEXT--EMBEDDING--3--small-353535?style=for-the-badge&logoColor=white) |
| **LLM Model**          | ![gpt-4.1](https://img.shields.io/badge/gpt--4.1-4B91FF?style=for-the-badge&logo=openai&logoColor=white)                     |
| **Collaboration Tool** | ![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)                                 |
| **Vector DB**          | ![Chroma](https://img.shields.io/badge/Pinecone-ff5c83?style=for-the-badge&logo=databricks&logoColor=white)                  |

---

## 📂 시스템 구성

1.  **데이터 수집 및 전처리**

    - 출처: 카드고릴라의 카드 정보 페이지 (카드id 기반 URL)
    - 수집 항목: 카드명, 카드사, 브랜드(VISA, Mastercard), 연회비, 혜택, 유의사항
    - 처리 방식: Selenium으로 동적 요소 렌더링, HTML 파싱, JSON으로 저장
    - 발급 불가 카드 필터링: "신규발급이 중단된 카드입니다." 문자열 포함 데이터 수집 X
    - 혜택 분류: 주요 혜택 항목은 benefits으로 추출

2.  **문서 임베딩**

    - 임베딩 모델: text-embedding-3-small (OPEN AI)
    - 벡터 DB: Pinecone DB
    - 문서 구성: 카드 설명 문장 + 혜택 요약/상세 텍스트 + 메타데이터
    - 규모: 약 1700개 문서 벡터화
    - 메타데이터: 카드명, 브랜드, 연회비 등 검색 필터링용 정보 포함

    **개선 과정**
    - 기존 방식의 한계
    벡터 유사도만으로는 카드 간 유사도 구분이 어렵고, 조건 충족 여부 판단이 어려움
    - 초기 개선 방안
    메타데이터 필터링을 적용해 카드사/연회비 등의 조건 기반 정밀 검색 가능
    단점: 조건을 일부만 충족해도 추천되는 경우가 있어 정확도 저하 우려
    - 최종 개선 방안
    사용자 질문을 LangChain LLM을 통해 4개의 paraphrase로 확장
    → 각각 임베딩 후 평균 벡터를 계산해 대표 의미 벡터 생성
    → 평균 벡터를 사용하여 벡터 DB에 질의

4.  **Chain 구성**

```
# 코드
recommend_chain = (
    RunnablePassthrough()
    | {"query": RunnablePassthrough(), "vector": expand_and_embed}
    | RunnableMap({
        "query": lambda x: x["query"],
        "cards": search_similar_cards_with_filter
    })
    | RunnableMap({
        "query": lambda x: x["query"],
        "cards_block": lambda x: format_cards(x["cards"])
    })
    | RunnableLambda(make_prompt)
    | llm # gpt-4.1
    | parser
)
```

<!-- ![체인 이미지](./figure/rag_chain.png) -->

| 단계                    | 설명                                                                            | 목적/특징                                     |
| ----------------------- | ------------------------------------------------------------------------------- | --------------------------------------------- |
| **사용자 입력**         | 사용자가 자연어로 카드 조건 입력 (`"연회비 적고 쇼핑 혜택 많은 카드 추천해줘"`) | 추천 조건 입력 시작                           |
| **쿼리 확장 및 임베딩** | 입력 쿼리를 4개 유사 표현으로 확장 후 임베딩 → 평균 벡터 계산                   | 다양한 표현 반영, 검색 정확도 향상            |
| **유사 카드 검색**      | 평균 벡터로 유사 카드 Top-k 검색 + 조건 필터링 (카드사, 연회비 등)              | 벡터 유사도 기반 카드 후보군 생성             |
| **카드 정보 정리**      | 검색된 카드 정보를 사람이 읽기 쉬운 텍스트 블록으로 변환                        | 카드 정보 context 생성 (카드명, 혜택 등 포함) |
| **프롬프트 생성**       | 입력 쿼리 + 카드 정보를 조합해 LLM용 최적화된 자연어 프롬프트 생성              | 요약 요청 포맷 포함, 정보 왜곡 방지           |
| **LLM 응답 생성**       | 완성된 프롬프트로 LLM 응답 생성                                                 | 자연어 카드 추천 결과 생성                    |
| **응답 파싱**           | 출력된 응답 문자열을 최종 형태로 정리                                           | 유저가 바로 활용할 수 있는 결과 제공          |
| **RAGAS 평가**          | `answer_relevancy` 기반 응답 관련성 자동 평가                                   | 수치 기반 품질 평가 가능, 개선 피드백 제공    |

4. **RAG 성능 평가**

   - 평가 도구: **RAGAS**
   - 지표:
     - faithfulness: 응답의 문서 근거 충실도
     - answer_relevancy: 질문과 응답의 관련성
   - 평가 데이터: 사용자 입력

   ![ragas 이미지](./figure/ragas2.png)

---

## 🧩 시스템 구조도

```mermaid
flowchart LR
    %% 첫 번째 줄: 입력 처리 및 검색
    subgraph 단계1[🧩 Input & Vector Search]
        A[Start: RunnablePassthrough]
        B{{Split Input}}
        B1[query: RunnablePassthrough]
        B2[vector: expand_and_embed]
        C[RunnableMap:\nquery: x.query,\ncards: search_similar_cards_with_filter]
        A --> B --> B1
        B --> B2
        B1 & B2 --> C
    end

    %% 두 번째 줄: 포맷 → 프롬프트 → LLM
    subgraph 단계2[🧠 Prompt & LLM Inference]
        D[RunnableMap:\nquery: x.query,\ncards_block: format_cards x.cards]
        E[RunnableLambda:\nmake_prompt x]
        F[LLM e.g., GPT-4]
        G[Output Parser]
        H[Final Output]
        C --> D --> E --> F --> G --> H
    end
```

---

## 💬 예시 입력/출력

입력창

```
원하는 동작을 선택하세요:
1. 추천 결과 요약 보기
2. 재검색(새로운 쿼리)
3. 카드 홈페이지(URL) 모두 보기
4. 종료
```

예시 질문

```
"삼성카드 중에서 배달 혜택 있는 카드 알려줘"
“OTT, 통신비 혜택이 있는 카드 추천해줘”
“연회비 1만원 이하면서 스트리밍 할인 있는 카드 알려줘”
```

출력 예시

```
- 카드명: CU 배달의민족 삼성카드 taptap
- 카드사: 삼성카드
- 연회비(국내): 0원
- 브랜드: Mastercard
- 혜택:
   CU·배달의민족 삼성카드 taptap
   배달의민족 15,000원 이상 결제 시 월 3회, 건당 2,000원 청구할인(최대 6,000원)
   전월 30만원 이상 이용 시 제공, 발급 후 1개월 간 실적 조건 없음
```

---

## ⚙️ 추후 발전 계획

![웹 이미지](./figure/chatting.png)

1. 카드별 혜택 세부 비교 지원 :
  사용자가 한 번의 검색/질문으로 추천받은 여러 카드를
  혜택, 연회비, 실적조건 등 주요 항목별로 표 형태로 비교할 수 있는 기능을 제공합니다.

2. 대화 내역 기반 추가 질의 응답 :
  이전 대화 맥락을 기억하는 챗봇 구조로 발전시켜,
  사용자가 카드 추천 후 “이 카드 혜택 중 교통 할인만 다시 알려줘”,
  “연회비 더 싼 카드만 다시 보여줘” 등
   **후속 질문(후행 질의)**에 자연스럽게 답변이 이어지도록 구현할 예정입니다.

3. 추가적으로 고려 중인 기능 :
  사용자가 은행/카드사에서 받은 소비내역(xml 파일 등)을 업로드하면,
  자동으로 주요 소비 패턴 분석 및 맞춤형 카드 추천 기능 제공 (예: 최근 3개월 카페·주유·쇼핑 최다 이용 → 해당 혜택 많은 카드 추천)
  추천 카드 간 혜택/조건/예상 적립액 비교 표/차트 자동 생성
