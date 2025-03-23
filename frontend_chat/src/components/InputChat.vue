<script setup>
import VoiceRecord from './utils/VoiceRecord.vue';
import Attachment from './utils/Attachment.vue';
import { ref, onUnmounted } from 'vue'

const emit = defineEmits(['pushed_message', 'file_loaded'])

const newMessage = ref("");

const audioUrl = ref(null);
const isRecording = ref(false);
const resetAudio = ref(false);
const elapsedTime = ref(0);
let mediaRecorder;
let audioChunks = [];
let timer;
let audioBlob;

const UpChat = () => {
    if (newMessage.value === "" && !audioBlob) return;

    let reponse_estruct = {
        type: null,
        data: null,
        url: null
    }

    if (newMessage.value === "" && audioBlob) {
        reponse_estruct.type = 'audio'
        reponse_estruct.data = processAudio()
        reponse_estruct.url = audioUrl.value
    } else if (newMessage.value !== "" && !audioBlob) {
        reponse_estruct.type = 'text'
        reponse_estruct.data = newMessage.value
    }
    emit('pushed_message', reponse_estruct)
    clearMessage()
}

const processAudio = () => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    return formData
}

const startRecording = async () => {
    clearMessage()
    isRecording.value = true
    elapsedTime.value = 0
    timer = setInterval(() => elapsedTime.value++, 1000);

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
        clearInterval(timer);
        audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        audioChunks = [];
        audioUrl.value = URL.createObjectURL(audioBlob);
    };

    mediaRecorder.start();
};

const stopRecording = () => {
    mediaRecorder.stop();
    resetAudio.value = true
    isRecording.value = false;
};

const clearMessage = () => {
    audioBlob = null
    newMessage.value = ""
    audioUrl.value = null
    resetAudio.value = false
};

const file_loaded = (data) => {
    emit('file_loaded', data)
}

onUnmounted(() => {
    clearInterval(timer);
});

</script>

<template>
    <div class="chat-input">
        <VoiceRecord class="record-icon" :reset="resetAudio" :audioUrl="audioUrl" :elapsedTime="elapsedTime"
            @startRecording="startRecording" @stopRecording="stopRecording" @clearRecording="clearMessage" />
        <Attachment class="attachment-icon" @file_loaded="file_loaded" />
        <input type="text" v-model="newMessage" @keyup.enter="UpChat" placeholder="Escribe un mensaje..." />
        <button class="input-icon send-icon main-color" @click="UpChat">
            <i class="fa-solid fa-circle-arrow-up"></i>
        </button>
    </div>
</template>

<style scoped>
.chat-input {
    position: relative;
    display: flex;
    align-items: center;
    padding: 10px 0;
    padding-bottom: calc(env(safe-area-inset-bottom) + 20px);
}

.chat-input input {
    width: 100%;
    padding: 2% 70px;
    box-sizing: border-box;
    border: 2px solid #ccc;
    border-radius: 15px;
}

.input-icon {
    cursor: pointer;
    font-size: 24px;
    z-index: 2;
}

/* .record-icon {
    position: absolute;
    left: 20px;
} */

.attachment-icon {
    position: absolute;
    left: 15px;
}

.send-icon {
    position: absolute;
    right: 10px;
}

@media (max-width: 768px) {
    .chat-input {
        margin-bottom: 10px;
    }
    .chat-input input {
        font-size: 14px;
    }
    .send-icon {
        right: 10px;
    }
}
</style>