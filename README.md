# SKN13-3rd-2Team

## 프로젝트 구조 (임시)

card-rag-bot/
├── data/           # 크롤링 및 전처리된 카드 등의 데이터 저장
│   ├── raw/        # 원본 크롤링 JSON 파일 (예: 카드고릴라 크롤링 결과물)
│   └── processed/  # 문장화 및 임베딩용 정제 데이터
│
├── crawling/       # 카드 정보 수집용 크롤러 및 HTML 파서 코드
│
├── embedding/      # 문서 임베딩 생성 및 벡터 DB 저장 스크립트
│
├── RAG/            # LangGraph 기반 RAG 체인 정의 및 노드 구성
│
├── app/            # 챗봇 실행 로직 (추후 streamlit 등 사용 시)
