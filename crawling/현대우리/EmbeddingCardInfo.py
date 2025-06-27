import os
import json
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# 환경 변수 로드
load_dotenv()


# 설정 상수
CARD_FOLDER = "./cards"
CHROMA_PERSIST_DIR = "./chroma_card_db"
EMBEDDING_MODEL_NAME = "dragonkue/BGE-m3-ko"

embedding_model = HuggingFaceEmbeddings(
    model_name = EMBEDDING_MODEL_NAME,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings":True}
)

# 3. Document 생성 함수
def create_document_from_card(card_json: dict) -> Document:
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
        "inactive": card_json.get("inactive", ""),
        "issuer": card_json.get("issuer", ""),
        "card_name": card_json.get("card_name", ""),
        "annual_fee": card_json.get("annual_fee", ""),
        "brands": ", ".join(card_json.get("brands", []))
    }

    return Document(page_content=content, metadata=metadata)

# 4. 모든 카드 JSON 파일 Document로 변환
documents = []
for filename in os.listdir(CARD_FOLDER):
    if filename.endswith(".json"):
        file_path = os.path.join(CARD_FOLDER, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            
            card_data = json.load(f)
            documents.append(create_document_from_card(card_data))


db = Chroma.from_documents(
    documents=documents,
    embedding=embedding_model,
    persist_directory=CHROMA_PERSIST_DIR
)
db.persist()

print(f"총 {len(documents)}개의 카드가 Chroma DB에 저장되었습니다.")
