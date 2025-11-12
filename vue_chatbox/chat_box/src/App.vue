<script setup>
import Chatbot from './components/chatbox.vue'

</script>

<template>
  <Chatbot />
</template>

<style >
body {
  margin: 0;
  font-family: -apple-system, BlinkMacMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;

  background-image: url('https://cdn-media.sforum.vn/storage/app/media/hinh-nen-powerpoint-lich-su-viet-nam-1.jpeg');
  background-size: cover; 
  background-position: center; 
  background-repeat: no-repeat;
  background-attachment: fixed;
  background-color: #ae0c0a !important; 
}
</style>



<!-- .text-input-grok {
  flex-grow: 1;
  border: none;
  background: transparent !important;
  outline: none; /* Đã sửa lỗi thiếu : */
  font-size: 1.1rem; 
  padding: 5px 0;
  color: #212121 !important; /* Chữ Đen */
  width: 100%; /* Đã sửa lỗi thiếu ; */
}

.text-input-grok::placeholder {
  color: #ffb74d; /* Đã sửa lỗi thiếu ; */
}

.send-button-grok {
  background-color: #ffeb3b; /* Vàng Cờ */
  color: #c62828; /* Đã sửa lỗi thiếu ; */
  border: none;
  border-radius: 50%;
  width: 45px; /* Đã sửa lỗi thiếu ; */
  height: 45px; 
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  
  /* SỬA LỖI: Đặt margin-left về 5px hoặc 0 để sát góc */
  margin-left: 5px; 
  
  flex-shrink: 0;
} -->