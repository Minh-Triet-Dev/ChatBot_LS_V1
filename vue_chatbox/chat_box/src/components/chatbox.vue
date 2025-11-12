<template>
  <div class="chatbot-container grok-inspired">
    <div class="chat-main-content">
      <div class="chat-header-grok">
        <div class="header-content">
          <h1>ChatBox Lịch Sử Việt Nam</h1>
        </div>
      </div>
    </div>
    
    <div class="messages-list" ref="messagesContainer">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="['message-wrapper', message.sender]"
      >
        <div v-if="message.type === 'text'" class="message-content-wrapper">
          <p v-html="formatContent(message.content)"></p>
        </div>

        <div v-else-if="message.type === 'image'" class="message-content-wrapper is-image-mode">
          <div class="image-section">
            <p class="user-image-prompt">Hỏi: {{ message.userQuestion || 'Phân tích ảnh' }}</p>
            <img :src="message.imagePreview" alt="Ảnh đã gửi" class="sent-image" />
          </div>
        </div>
      </div>
      
      <div v-if="isLoading" class="message-wrapper bot">
        <div class="message-content-wrapper is-loading">
          <span class="dot-flashing"></span>
          Đang suy nghĩ...
        </div>
      </div>
    </div>
    
    <div class="input-area-grok">
      <div class="grok-features-row">
        <button class="grok-feature-button" @click="setMode('text')" :class="{ active: currentMode === 'text' }">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="18" height="18">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H16.5m-13.5 3.375c0 1.01.794 1.831 1.8 1.831h1.95v-1.875a.375.375 0 01.375-.375H12a.375.375 0 01.375.375v1.875h1.95c1.006 0 1.8-.82 1.8-1.831V6.991c0-1.01-.794-1.831-1.8-1.831H4.8c-1.006 0-1.8.82-1.8 1.831v6.384z" />
          </svg>
          Hỏi Text
        </button>
        <button class="grok-feature-button" @click="setMode('image')" :class="{ active: currentMode === 'image' }">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="18" height="18">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
          </svg>
          Upload Ảnh
        </button>
      </div>

      <div class="input-container-grok">
        <form @submit.prevent="currentMode === 'text' ? sendTextMessage() : sendImageMessage()" class="input-form-grok">
          
          <div class="main-input-wrapper">
            <input
              v-if="currentMode === 'text'"
              v-model="inputText"
              type="text"
              placeholder="Hỏi AI Lịch Sử bất cứ điều gì..."
              :disabled="isLoading"
              class="text-input-grok"
            />

            <template v-else>
              <div class="image-input-fields">
                
                <label v-if="!selectedImageFile" for="image-upload" class="image-upload-label">
                  <span class="placeholder-text">🖼️ Chọn ảnh từ máy tính để phân tích...</span>
                  <input
                    id="image-upload"
                    type="file"
                    accept="image/*"
                    @change="handleImageUpload"
                    ref="fileInput"
                    :disabled="isLoading"
                    hidden
                  />
                </label>

                <div v-else class="image-question-input-with-preview">
                    <img v-if="imagePreviewUrl" :src="imagePreviewUrl" alt="Ảnh đã chọn" class="selected-image-preview" />
                    <input
                        v-model="imageQuestion"
                        type="text"
                        placeholder="Nhập câu hỏi về ảnh (Ví dụ: Ý nghĩa của lá cờ là gì?)"
                        :disabled="isLoading"
                        class="text-input-grok question-for-image"
                    />
                </div>
              </div>
            </template>
          </div>

          <button 
            type="submit" 
            :disabled="isLoading || (currentMode === 'text' && !inputText.trim()) || (currentMode === 'image' && !selectedImageFile)" 
            class="send-button-grok"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import axios from 'axios';

// --- State Variables ---
const API_BASE = 'http://127.0.0.1:8000/chat/';
const messages = ref([
  {
    sender: 'bot',
    type: 'text',
    content: 'Chào bạn! Tôi là **AI Lịch Sử**. Bạn có thể hỏi tôi bằng văn bản hoặc tải lên hình ảnh để tôi phân tích. 🇻🇳',
  },
  // {
  //   sender: 'user',
  //   type: 'text',
  //   content: 'Xin chào! Hôm nay thế nào?',
  // },
]);
const inputText = ref('');
const imageQuestion = ref(''); 
const currentMode = ref('text'); 
const isLoading = ref(false);
const selectedImageFile = ref(null);
const fileInput = ref(null);
const messagesContainer = ref(null);
const imagePreviewUrl = ref(null); 

// --- Functions ---
const formatContent = (text) => {
    if (!text) return '';
    // Xử lý **Bold**
    return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
};

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

watch(messages, scrollToBottom, { deep: true });

const setMode = (mode) => {
    currentMode.value = mode;
    // Reset input khi chuyển chế độ
    inputText.value = '';
    imageQuestion.value = ''; 
    selectedImageFile.value = null;
    imagePreviewUrl.value = null; // Reset preview URL khi chuyển mode
    if (fileInput.value) {
      fileInput.value.value = '';
    }
};

// --- Xử lý Gửi Text ---
const sendTextMessage = async () => {
  const userText = inputText.value.trim();
  if (!userText) return;

  messages.value.push({ sender: 'user', type: 'text', content: userText });
  inputText.value = '';
  isLoading.value = true;

  try {
    const response = await axios.post(`${API_BASE}text`, {
      question: userText,
    });

    messages.value.push({
      sender: 'bot',
      type: 'text',
      content: response.data.answer || 'Xin lỗi, tôi không thể trả lời câu hỏi này.',
    });
  } catch (error) {
    console.error('Lỗi khi gửi Text API:', error);
    messages.value.push({
      sender: 'bot',
      type: 'text',
      content: 'Lỗi kết nối. Vui lòng thử lại sau.',
    });
  } finally {
    isLoading.value = false;
  }
};

// --- Xử lý Upload Ảnh ---
const handleImageUpload = (event) => {
  const file = event.target.files[0];
  selectedImageFile.value = file;
  imageQuestion.value = ''; 

  // TẠO VÀ GÁN PREVIEW URL NGAY KHI CHỌN ẢNH
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreviewUrl.value = e.target.result;
    };
    reader.readAsDataURL(file);
  } else {
    imagePreviewUrl.value = null;
  }
};

const sendImageMessage = async () => {
  if (!selectedImageFile.value) return;

  const file = selectedImageFile.value;
  const question = imageQuestion.value.trim() || 'Phân tích hình ảnh này về mặt lịch sử'; 

  const formData = new FormData();
  formData.append('image_file', file);
  formData.append('question', question); 


  messages.value.push({
      sender: 'user',
      type: 'image',
      imagePreview: imagePreviewUrl.value, 
      userQuestion: question, 
  });
  
  
  selectedImageFile.value = null;
  imageQuestion.value = '';
  imagePreviewUrl.value = null; 
  if (fileInput.value) {
    fileInput.value.value = '';
  }
  setMode('text'); // Chuyển về mode text sau khi gửi
  
  isLoading.value = true;
  sendImageApi(formData);
};

const sendImageApi = async (formData) => {
  try {
    const response = await axios.post(`${API_BASE}image`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    const botAnswer = response.data.answer || 'Không thể phân tích ảnh.';
    messages.value.push({
        sender: 'bot',
        type: 'text',
        content: botAnswer,
    });

    if (response.data.error) {
        messages.value.push({
            sender: 'bot',
            type: 'text',
            content: `Lỗi: ${response.data.error}`,
        });
    }

  } catch (error) {
    console.error('Lỗi khi gửi Image API:', error);
    messages.value.push({
        sender: 'bot',
        type: 'text',
        content: 'Lỗi kết nối hoặc xử lý ảnh. Vui lòng thử lại.',
    });
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
/* --- Định nghĩa màu sắc cố định --- */
/* Đỏ Cờ đậm: #EF5350 */
/* Đỏ đậm (User Bubble): #C62828 */
/* Vàng Cờ: #FFEB3B */
/* Vàng Kem (Bot Bubble): #FFFDE7 */
/* Trắng (Input/User Text): #FFFFFF */
/* Chữ Đen: #212121 */

.chatbot-container.grok-inspired {
  max-width: 1100px; 
  height: 98vh; 
  margin: 1vh auto;
  border: 1px solid #c62828;
  border-radius: 16px;
  display: flex;
  flex-direction: column; 
 
  background-color: #aa0f0d; 
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
  color: #ffffff; 
  overflow: hidden;
}


.chat-header-grok {
  text-align: center;
  padding: 20px;
  border-bottom: 1px solid #c62828;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  background-color: #b10d0a; 
  flex-shrink: 0;
}

.header-content {
    display: flex;
    align-items: center;
    gap: 10px;
}

.chat-header-grok h1 {
  font-size: 2.4em; /* Tăng cỡ chữ */
  font-weight: 700;
  color: #ffeb3b; /* Chữ tiêu đề VÀNG */
  margin: 0;
}

.flag-icon {
    width: 35px;
    height: 25px;
}


.messages-list {
  flex-grow: 1; 
  padding: 20px 40px;
  overflow-y: auto;
  /* Nền khung chat là ĐỎ */
  background-color: #ef5350; 
  position: relative;
  
  /* Background Quốc kỳ bằng URL */
  background-image: url('https://cdn-media.sforum.vn/storage/app/media/thanhhuyen/%E1%BA%A3nh%20l%C3%A1%20c%E1%BB%9D%20vi%E1%BB%87t%20nam/anh-la-co-viet-nam-1.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

/* Lớp phủ (Giữ nguyên 1 để cờ hiển thị rõ) */
.messages-list::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: inherit; 
    background-size: inherit;
    background-position: inherit;
    background-repeat: inherit;
    opacity: 1; 
    pointer-events: none; 
    z-index: 0;
}



.message-wrapper {
  position: relative;
  z-index: 1;
  display: flex;
  margin-bottom: 20px; 
  align-items: flex-start;
}

.message-wrapper.user {
  justify-content: flex-end; 
}

.message-wrapper.bot {
  justify-content: flex-start; 
}

.message-content-wrapper {
  max-width: 65%; /* Tăng max-width để mở rộng bong bóng chat */
  padding: 18px 25px; 
  border-radius: 25px; 
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  box-shadow: 0 2px 8px rgba(0,0,0,0.4); 
  font-size: 1.2rem; /* Tăng cỡ chữ */
}

.message-content-wrapper p {
    margin: 0;
}


.message-wrapper.user .message-content-wrapper {
  background-color: #c62828 !important; /* Đỏ đậm */
  color: #ffffff !important; 
  border: 1px solid #ffffff; /* Viền trắng */
  border-bottom-right-radius: 6px; 
}


.message-wrapper.bot .message-content-wrapper {
  background-color: #fffde7; /* Vàng kem */
  color: #212121; /* Chữ Đen */
  border: 1px solid #ffeb3b; /* Viền Vàng */
  border-bottom-left-radius: 6px; 
}


.message-content-wrapper.is-image-mode {
  padding: 10px; /* Giảm padding cho khối ảnh */
  display: block;
}

.message-content-wrapper .image-section {
    max-width: 100%;
}

.message-content-wrapper .sent-image {
  max-width: 100%; 
  max-height: 400px; /* Giới hạn chiều cao */
  border-radius: 12px;
  margin-top: 10px;
  object-fit: contain; /* Đảm bảo ảnh hiển thị đầy đủ trong khung */
}

.message-content-wrapper .user-image-prompt {
    font-size: 0.95rem;
    color: #ffeb3b;
    font-weight: bold;
    margin-bottom: 5px !important;
}



.input-area-grok {
  flex-shrink: 0; 
  padding: 20px 40px;
  border-top: 1px solid #c62828;
  /* Nền khung dưới là ĐỎ */
  background-color: #af0e0c; 
}


.grok-features-row {
  display: flex;
  justify-content: flex-start;
  gap: 10px;
  margin-bottom: 15px; 
  padding-left: 0; 
}

.grok-feature-button {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 10px 18px;
  border: 1px solid #ffeb3b; /* Viền VÀNG */
  border-radius: 25px;
  background-color: #fffde7; /* Vàng Kem */
  color: #c62828; /* Chữ ĐỎ ĐẬM */
  font-size: 1em;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.grok-feature-button.active {
  background-color: #ffeb3b; /* VÀNG CỜ */
  border-color: #ffeb3b;
  color: #c62828; 
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.grok-feature-button.active svg {
  color: #c62828; 
}

.input-form-grok {
  display: flex;
  align-items: center;
  border: 1px solid #ffcc80;
  border-radius: 30px; 
  background-color: #ffffff; /* 🎯 NỀN TRẮNG TINH */
  padding: 12px 20px; 
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.main-input-wrapper {
    flex-grow: 1;
}

.text-input-grok {
  flex-grow: 1;
  border: none;
  background: transparent !important;
  outline: none; 
  font-size: 1.1rem; 
  padding: 5px 0;
  color: #212121 !important; /* Chữ Đen */
  width: 100%; 
}

.text-input-grok::placeholder {
  color: #ffb74d; 
}


.image-question-input-with-preview {
    display: flex;
    flex-direction: column; /* Đặt ảnh và input theo chiều dọc */
    align-items: flex-start;
    flex-grow: 1;
    gap: 8px; /* Khoảng cách giữa ảnh và input */
}

.selected-image-preview {
    max-width: 150px; /* Giới hạn kích thước ảnh preview */
    max-height: 150px;
    border-radius: 8px;
    object-fit: contain;
    border: 1px solid #ffeb3b;
    padding: 5px;
    background-color: #fffde7;
}

.text-input-grok.question-for-image {
    width: calc(100% - 10px); /* Đảm bảo input nằm gọn */
    border: 1px dashed #ffb74d; /* Viền đứt nét để phân biệt */
    border-radius: 15px;
    padding: 8px 15px;
    font-size: 1rem;
}


.send-button-grok {
  background-color: #ffeb3b; /* Vàng Cờ */
  color: #c62828; 
  border: none;
  border-radius: 50%;
  width: 45px; 
  height: 45px; 
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  
  margin-left: 5px; 
  
  flex-shrink: 0;
}

.send-button-grok:hover:not(:disabled) {
  background-color: #fbc02d; 
}

.send-button-grok:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}


.message-content-wrapper.is-loading {
    display: flex;
    align-items: center;
    font-style: italic;
    color: #888;
    background-color: #fff8e1; /* Vàng nhạt */
}

.dot-flashing {
  position: relative;
  width: 5px;
  height: 5px;
  border-radius: 5px;
  background-color: #fbc02d; 
  color: #fbc02d;
  animation: dotFlashing 1s infinite linear alternate;
  animation-delay: 0.5s;
  margin-right: 10px;
  display: inline-block;
}

.dot-flashing::before, .dot-flashing::after {
  content: "";
  display: inline-block;
  position: absolute;
  top: 0;
  width: 5px;
  height: 5px;
  border-radius: 5px;
  background-color: #fbc02d;
  color: #fbc02d;
  animation: dotFlashing 1s infinite linear alternate;
}

.dot-flashing::before {
  left: -10px;
  animation-delay: 0s;
}

.dot-flashing::after {
  left: 10px;
  animation-delay: 1s;
}

@keyframes dotFlashing {
  0% {
    background-color: #fbc02d;
  }
  50%, 100% {
    background-color: #ffea00; 
  }
}
</style>