
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel
import os
import shutil
from typing import Dict, Any


from modules.rag_chain import rag_chain, general_chat_chain, image_to_text_chain
from modules.router import route_question
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough


router_runnable = RunnableLambda(lambda x: route_question(x["question"]))

final_rag_chain = RunnablePassthrough.assign(
    route=router_runnable
) | RunnableBranch(
    (lambda x: x["route"] == "rag", rag_chain),
    general_chat_chain,
)


app = FastAPI(title="Dien Bien Phu Chatbot API", version="1.0")


origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],    
)



class TextRequest(BaseModel):
    """Mô hình dữ liệu cho câu hỏi dạng text."""
    question: str



class ChatResponse(BaseModel):
    """Mô hình dữ liệu cho phản hồi."""
    answer: str
    mode: str
    

UPLOAD_DIR = "uploaded_temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)



@app.post("/chat/text", response_model=ChatResponse)
def chat_text(request: TextRequest):
    """
    Xử lý câu hỏi dạng văn bản. Sử dụng Router để quyết định RAG hay General Chat.
    """
    try:
        input_data = {"question": request.question}
        response = final_rag_chain.invoke(input_data)
        
        mode = route_question(request.question) 
        
        return ChatResponse(answer=response, mode=f"{mode} chat")
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Lỗi xử lý câu hỏi: {str(e)}"
        )



@app.post("/chat/image", response_model=ChatResponse)
async def chat_image(
    question: str = Form(..., description="Câu hỏi liên quan đến hình ảnh"), 
    image_file: UploadFile = File(..., description="File ảnh để phân tích") 
):
    """
    Xử lý câu hỏi về hình ảnh (VQA + RAG) bằng cách nhận file ảnh.
    """
    
    file_extension = os.path.splitext(image_file.filename)[1]
    
    temp_file_name = f"{os.urandom(16).hex()}{file_extension}" 
    temp_file_path = os.path.join(UPLOAD_DIR, temp_file_name)
    
    try:
        
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
            
        
        response = image_to_text_chain.invoke({
            "question": question, 
            "image_path": temp_file_path 
        })
        
        return ChatResponse(answer=response, mode="image-to-text RAG (VQA)")
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Lỗi xử lý VQA: {str(e)}"
        )
    finally:

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)