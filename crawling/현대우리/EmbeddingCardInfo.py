import os
import json
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import openai

from dotenv import load_dotenv



load_dotenv()

# 임베딩 모델 설정 (OpenAI, text-embedding-3-small 사용)
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# 2. 데이터 폴더 경로
folder_path = "./cards"  # 사용자 환경에 맞게 수정
persist_dir = "./chroma_card_db"

# 3. Document 생성 함수
def create_document_from_card(card_json):
    # content 구성: 혜택 + 유의사항
    benefit_texts = []
    for benefit in card_json.get("benefits", []):
        summary = benefit.get("summary", "")
        details = "\n".join(benefit.get("details", []))
        benefit_texts.append(f"{summary}\n{details}")
    benefits_combined = "\n\n".join(benefit_texts)
    cautions_combined = "\n".join(card_json.get("cautions", []))
    content = f"[혜택 요약 및 상세]\n{benefits_combined}\n\n[유의사항]\n{cautions_combined}"

    # metadata 구성
    metadata = {
        "issuer": card_json.get("issuer", ""),
        "card_name": card_json.get("card_name", ""),
        "brands": ", ".join(card_json.get("brands", []))
    }

    return Document(page_content=content, metadata=metadata)

# 4. 모든 카드 JSON 파일 Document로 변환
documents = []
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            card_json = json.load(f)
            doc = create_document_from_card(card_json)
            documents.append(doc)

# 5. Chroma DB에 저장
db = Chroma.from_documents(
    documents=documents,
    embedding=embedding_model,
    persist_directory=persist_dir
)

db.persist()
print(f"총 {len(documents)}개의 카드가 Chroma DB에 저장되었습니다.")
