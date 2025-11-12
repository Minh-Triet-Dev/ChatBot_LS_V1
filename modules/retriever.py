import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

def create_retriever(data_folder: str, index_path: str):
    """
    Tải Vector Store đã có nếu tồn tại (index.faiss và index.pkl),
    nếu không sẽ tạo mới từ các file TXT trong data_folder.
    """
    
    embeddings = SentenceTransformerEmbeddings(model_name="intfloat/multilingual-e5-large")

    
    faiss_file = os.path.join(index_path, "index.faiss")
    pkl_file = os.path.join(index_path, "index.pkl")

    if os.path.exists(faiss_file) and os.path.exists(pkl_file):
        try:
            
            vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
            print(f"Đã tải Vector Store từ '{index_path}' (Không cần tạo lại).")
            return vector_store.as_retriever(search_kwargs={"k": 7})
        except Exception as e:
            print(f"Lỗi khi tải Vector Store: {e}. Tiến hành tạo mới.")
            

   
    print(f"Không tìm thấy Index cũ hoặc Index bị thiếu file. Bắt đầu tạo Index mới.")

    if not os.path.exists(data_folder):
        print(f"Lỗi: Thư mục dữ liệu không tồn tại: {data_folder}")
        return None

    data_files = [f for f in os.listdir(data_folder) if f.endswith('.txt')]
    if not data_files:
        print(f"Lỗi: Không tìm thấy file TXT nào trong thư mục '{data_folder}'.")
        return None

    all_docs: List[Document] = []
    for filename in data_files:
        file_path = os.path.join(data_folder, filename)
        loader = TextLoader(file_path, encoding='utf-8')
        all_docs.extend(loader.load())

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    document_chunks = text_splitter.split_documents(all_docs)

    vector_store = FAISS.from_documents(document_chunks, embeddings)
    
    
    os.makedirs(index_path, exist_ok=True)
    vector_store.save_local(index_path)
    
    print(f"Đã tạo Vector Store mới và lưu tại '{index_path}'.")
    return vector_store.as_retriever(search_kwargs={"k": 3})