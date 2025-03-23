<script setup>
import { ref } from 'vue';

const emit = defineEmits(['file_loaded']); 

const acceptedFiles = "" //".mp3, .mp4, .wav, audio/*"

const isRecording = ref(false)
const fileInput = ref(null);

const attached = () => {
    fileInput.value.click();
};

const handleFiles = (event) => {
    const uploadedFiles = event.target.files || event.dataTransfer.files;
    let type = 'Unknown'
    Array.from(uploadedFiles).forEach((file) => {
        if (file.name.endsWith('.png') || file.name.endsWith('.jpg')) {
          type = 'image'
        } else if (file.name.endsWith('.wav')) {
          type = 'audio'
        }else if (file.name.endsWith('.pdf')) {
          type = 'pdf'
        }
        emit('file_loaded', { type, file })
    });
  };


</script>

<template>
    <div class="dynamicClasses">
        <button @click="attached()" v-if="!isRecording">
            <i class="fa-solid fa-paperclip input-icon main-color"></i>
            <input type="file" @change="handleFiles" ref="fileInput" class="file-input" :accept="acceptedFiles"/>
        </button>
        <div v-else>
            <i class="fa-solid fa-clipboard-check input-icon main-color"></i>
        </div>
    </div>
</template>


<style scoped>
.input-icon {
    cursor: pointer;
    font-size: 21px;
}
.file-input {
  display: none;
}
</style>