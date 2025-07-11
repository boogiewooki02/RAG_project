# embedding.py
import json
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# 임베딩 모델 설정
e_model_id = "text-embedding-3-small"
embedding_model = OpenAIEmbeddings(model=e_model_id)

# Chroma DB 로드
collection_name = "card_info"
persis_directory = "../data/chroma_db"

vector_store = Chroma(
    collection_name=collection_name,
    embedding_function=embedding_model,
    persist_directory=persis_directory,
)

# 카드사 리스트
brands = ["국민", "농협", "롯데", "삼성", "신한", "우리", "하나", "현대", "BC", "IBK기업"]

# 각 카드사 임베딩
for brand in brands:
    with open(f"../data/raw/{brand}.json", "r", encoding="utf-8") as f:
        card_data = json.load(f)

    documents = []
    for card in card_data:
        doc_text = f"{card['name']}는 {card['brand']}에서 발급한 {card['c_brand']} 카드입니다. "
        doc_text += f"연회비는 국내 {card['fee_domestic']}원, 해외겸용 {card['fee_global']}원입니다.\n"
        for b in card['benefits']:
            doc_text += f"- [{b['category']}] {b['short_description']} / {b['detail_description']}\n"
        doc_text += f"카드 신청은 {card['url']}에서 가능합니다.\n"

        documents.append(
            Document(page_content=doc_text, metadata={"name": card['name'], "brand": card['brand'], "c_brand": card['c_brand'], "fee_domestic": card['fee_domestic'], "fee_global": card['fee_global']})
        )
    vector_store.add_documents(documents)
    print(f"{brand}카드 임베딩 추가 완료")

# DB 저장
vector_store.persist()
print("모든 카드 문서가 Chroma DB에 저장되었습니다.")