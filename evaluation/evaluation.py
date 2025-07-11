# evaluation.py
from app.rag_chain import rag_chain
from app.retriever import retriever
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

questions = [
    "대중교통이랑 커피 할인 되는 카드 추천해줘",
    "반려동물 보험 혜택 있는 카드가 있어?",
    "해외여행 시 유용한 카드 추천해줘",
    "연회비가 10만원 이하인 카드 중에서 추천해줘",
    "디지털 구독 서비스 혜택이 있는 카드가 뭐야?",
]

answers = []
contexts = []
for q in questions:
    result = rag_chain.invoke(q)
    answers.append(result)
    docs = retriever.get_relevant_documents(q)
    contexts.append([d.page_content for d in docs])

dataset = Dataset.from_dict({
    "question": questions,
    "answer": answers,
    "contexts": contexts,
})

metrics = [faithfulness, answer_relevancy]
results = evaluate(dataset=dataset, metrics=metrics)

print(results.to_pandas())