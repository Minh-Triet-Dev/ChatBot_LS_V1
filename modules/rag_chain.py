# from langchain_groq import ChatGroq
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import RunnablePassthrough, RunnableLambda
# from langchain_core.documents import Document
# from typing import List
# from config import GROQ_API_KEY, LLM_MODEL
# from modules.retriever import create_retriever
# from modules.vqa_tool import analyze_image_tool
# from config import DATA_FOLDER, VECTOR_INDEX_PATH

# # === Khởi tạo LLM ===
# llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=LLM_MODEL, temperature=0.0)

# # === Khởi tạo retriever ===
# pdf_retriever = create_retriever(DATA_FOLDER, VECTOR_INDEX_PATH)

# # === Tạo chuỗi Multi-query ===
# MULTI_QUERY_PROMPT = ChatPromptTemplate.from_messages([
#     ("system", "Tạo 3 câu hỏi thay thế cho câu hỏi gốc về chủ đề lịch sử."),
#     ("user", "{question}")
# ])
# query_generation_chain = MULTI_QUERY_PROMPT | llm | StrOutputParser()

# def get_unique_documents(docs: List[Document]) -> List[Document]:
#     unique, result = set(), []
#     for doc in docs:
#         if doc.page_content not in unique:
#             unique.add(doc.page_content)
#             result.append(doc)
#     return result

# def manual_multi_query_retrieval(question: str) -> List[Document]:
#     try:
#         generated = query_generation_chain.invoke({"question": question})
#         queries = [q.strip() for q in generated.split('\n') if q.strip()]
#     except:
#         queries = []
#     queries = [question] + queries
#     all_docs = []
#     for q in queries:
#         try:
#             all_docs.extend(pdf_retriever.invoke(q))
#         except:
#             pass
#     return get_unique_documents(all_docs)

# # === Tạo các chain ===
# rag_prompt = ChatPromptTemplate.from_template("""
# Sử dụng CONTEXT sau để trả lời câu hỏi người dùng.
# Nếu không đủ thông tin, hãy trả lời: "Xin lỗi, Câu hỏi của bạn nằm ngoài dữ liệu của tôi."
# CONTEXT:
# {context}

# CÂU HỎI: {question}
# """)

# rag_chain = (
#     {"context": RunnableLambda(lambda x: manual_multi_query_retrieval(x["question"])),
#      "question": RunnablePassthrough()}
#     | rag_prompt | llm | StrOutputParser()
# )

# general_prompt = ChatPromptTemplate.from_messages([
#     ("system", "Bạn là một trợ lý vui vẻ, hữu ích, nói ngắn gọn."),
#     ("user", "{question}")
# ])
# general_chat_chain = general_prompt | llm | StrOutputParser()

# image_to_text_prompt = ChatPromptTemplate.from_template("""
# VISION OUTPUT:
# {vision_output}

# CONTEXT:
# {context}

# CÂU HỎI: {question}

# Trả lời bằng tiếng Việt:
# """)

# image_to_text_chain = (
#     RunnablePassthrough.assign(
#         vision_output=RunnableLambda(lambda x: analyze_image_tool(x["image_path"], x["question"]))
#     )
#     | RunnablePassthrough.assign(
#         context=RunnableLambda(lambda x: manual_multi_query_retrieval(x["question"]))
#     )
#     | image_to_text_prompt
#     | llm
#     | StrOutputParser()
# )
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.documents import Document
from typing import List
from config import GROQ_API_KEY, LLM_MODEL, GEMINI_API_KEY 
from modules.retriever import create_retriever
from modules.vqa_tool import analyze_image_tool
from config import DATA_FOLDER, VECTOR_INDEX_PATH


llm_groq = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=LLM_MODEL, temperature=0.0)


llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.0,
    api_key=GEMINI_API_KEY 
) 


try:
    pdf_retriever = create_retriever(DATA_FOLDER, VECTOR_INDEX_PATH)
except Exception as e:
    print(f"CẢNH BÁO: Không thể khởi tạo Retriever. {e}")
    pdf_retriever = RunnableLambda(lambda x: [Document(page_content="Tài liệu mẫu: Chiến dịch Điện Biên Phủ diễn ra năm 1954."),])



MULTI_QUERY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Tạo 3 câu hỏi thay thế cho câu hỏi gốc về chủ đề lịch sử."),
    ("user", "{question}")
])

query_generation_chain = MULTI_QUERY_PROMPT | llm_groq | StrOutputParser()

def get_unique_documents(docs: List[Document]) -> List[Document]:
    unique, result = set(), []
    for doc in docs:
        if doc.page_content not in unique:
            unique.add(doc.page_content)
            result.append(doc)
    return result

def manual_multi_query_retrieval(question: str) -> List[Document]:
    # ... (Logic retrieval của bạn) ...
    try:
        generated = query_generation_chain.invoke({"question": question})
        queries = [q.strip() for q in generated.split('\n') if q.strip()]
    except:
        queries = []
    queries = [question] + queries
    all_docs = []
    for q in queries:
        try:
            # pdf_retriever.invoke(q) sử dụng Retriever (Faiss) đã được khởi tạo
            all_docs.extend(pdf_retriever.invoke(q))
        except:
            pass
    return get_unique_documents(all_docs)

# === RAG Text Chain (Dùng Groq) ===
rag_prompt = ChatPromptTemplate.from_template("""
Sử dụng CONTEXT sau để trả lời câu hỏi người dùng.
Nếu không đủ thông tin, hãy trả lời: "Xin lỗi, Câu hỏi của bạn nằm ngoài dữ liệu của tôi."
CONTEXT:
{context}

CÂU HỎI: {question}
""")

rag_chain = (
    {"context": RunnableLambda(lambda x: manual_multi_query_retrieval(x["question"])),
     "question": RunnablePassthrough()}
    | rag_prompt | llm_groq | StrOutputParser()
)

# === General Chat Chain (Dùng Groq) ===
general_prompt = ChatPromptTemplate.from_messages([
    ("system", "Bạn là một trợ lý vui vẻ, hữu ích, nói ngắn gọn."),
    ("user", "{question}")
])
general_chat_chain = general_prompt | llm_groq | StrOutputParser()

# === Image-to-Text Chain (Dùng Gemini) ===
image_to_text_prompt = ChatPromptTemplate.from_template("""
VISION OUTPUT:
{vision_output}

CONTEXT:
{context}

CÂU HỎI: {question}

Trả lời bằng tiếng Việt:
""")

image_to_text_chain = (
    RunnablePassthrough.assign(
        vision_output=RunnableLambda(lambda x: analyze_image_tool(x["image_path"], x["question"]))
    )
    | RunnablePassthrough.assign(
        context=RunnableLambda(lambda x: manual_multi_query_retrieval(x["question"]))
    )
    | image_to_text_prompt
    | llm_gemini 
    | StrOutputParser()
)