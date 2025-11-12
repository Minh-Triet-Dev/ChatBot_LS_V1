from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import GROQ_API_KEY, LLM_MODEL

llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=LLM_MODEL)

router_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """
    Bạn là một bộ định tuyến thông minh.
    Nhiệm vụ của bạn là phân loại câu hỏi của người dùng.
    Tài liệu RAG hiện tại của tôi chuyên về **Chiến dịch Điện Biên Phủ và các sự kiện liên quan (1954)**.
    - Nếu câu hỏi liên quan đến Chiến dịch Điện Biên Phủ, các nhân vật, hoặc diễn biến, hãy trả lời bằng chữ **'RAG'**.
    - Nếu câu hỏi là lời chào hỏi, câu hỏi ngoài lề, hoặc không liên quan đến Điện Biên Phủ, hãy trả lời bằng chữ **'GENERAL'**.
    Chỉ trả lời 'RAG' hoặc 'GENERAL'. KHÔNG thêm bất kỳ từ nào khác.
    """),
    ("user", "{question}")
])

router_chain = router_prompt | llm | StrOutputParser()

def route_question(question_str: str): 
    intent = router_chain.invoke({"question": question_str}).strip().lower()
    print(f"DEBUG: Router phân loại là: {intent.upper()}")
    return intent
    
