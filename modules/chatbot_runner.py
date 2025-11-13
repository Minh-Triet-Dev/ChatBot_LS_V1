from langchain_core.runnables import RunnableBranch
from modules.rag_chain import rag_chain, general_chat_chain, image_to_text_chain
from modules.router import route_question
def ask_rag_chatbot(question: str):
    final_chain = RunnableBranch(
        (lambda x: route_question(x) == "rag", rag_chain),
        general_chat_chain,
    )
    response = final_chain.invoke({"question": question})
    print("\n--- TRẢ LỜI TEXT ---\n", response)

def ask_vqa_chatbot(question: str, image_path: str):
    print(f"\n--- IMAGE-TO-TEXT RAG ---\nẢnh: {image_path}")
    response = image_to_text_chain.invoke({"question": question, "image_path": image_path})
    print("\n--- KẾT QUẢ ---\n", response)

def run_chatbot():
    print("\n========== CHATBOT ==========")
    print("1  - Hỏi đáp văn bản")
    print("2️  - Hỏi đáp hình ảnh")
    print("Thoát: 'exit'")

    while True:
        mode = input("\nChọn chế độ (1/2): ").strip().lower()
        if mode in ["exit", "thoat"]: break

        if mode == "1":
            while True:
                q = input("Câu hỏi ('back' để quay lại): ").strip()
                if q in ["back", "exit"]: break
                ask_rag_chatbot(q)

        elif mode == "2":
            img = input("Đường dẫn ảnh ('back' để quay lại): ").strip()
            if img in ["back", "exit"]: continue
            q = input("Câu hỏi về ảnh: ").strip()
            ask_vqa_chatbot(q, img)

