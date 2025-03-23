<script setup>
import { ref, onMounted } from 'vue';
import { sharedState } from '../state'

import Header from '../components/Header.vue';
import ContentChat from '../components/ContentChat.vue';
import InputChat from '../components/InputChat.vue';
import api from '../api'

const ContentChatRef = ref(null);

const UpChat = (newMessage) => {
    if (newMessage.type === 'audio') {
        ContentChatRef.value.addMessage(true, true, '')
        fetchAUDIO(newMessage.data, newMessage.url)
    } else if (newMessage.type === 'text') {
        fetchCHAT(newMessage.data)
    }
}

const fetchCHAT = async (msg) => {
    ContentChatRef.value.addMessage(true, false, msg);
    ContentChatRef.value.addMessage(false, true, '');

    // Si el conversation_id no existe (porque se borró), se crea uno nuevo
    if (!localStorage.getItem("conversation_id")) {
        localStorage.setItem("conversation_id", Date.now().toString()); // Generar nuevo ID único
    }

    const conversationId = localStorage.getItem("conversation_id"); // Obtener el conversation_id existente
    const messageId = Math.random().toString(36).substring(2, 10); // ID único para cada mensaje

    let data = {
        "user_id": String(sharedState.id),
        "message_id": messageId,
        "conversation_id": conversationId, // Siempre usa el mismo hasta que se borre el chat
        "conversation_name": "default",
        "query": String(msg),
        "flag_modifier": false,
        "model_name": "gpt-4o",
        "search_tool": false
    };

    console.log("Enviando a la API:", data);

    try {
        let result = await api.requestCHAT(data);
        console.log("Respuesta de la API:", result);

        result['isUser'] = false;
        ContentChatRef.value.addMessage(false, false, result);
    } catch (error) {
        console.error('API error fetchCHAT:', error.response?.data || error.message);
    }
};

// const fetchAUDIO = async (formData, urlData) => {
//     try {
//         const result = await api.requestWhisper(formData)
//         fetchCHAT(`audio@${result.text}#${urlData}`)
//     } catch (error) {
//         console.error('API Error fetchAUDIO:', error);
//     }
// }

const fetchVote = async (data) => {
    try {
        const result = await api.requestVote(data);
        console.log(result)
    } catch (error) {
        console.error('API error fetchVote:', error);
    }
}

const loadAttachment = async (data) => {
    ContentChatRef.value.addMessage(true, false, `file@${data?.file.name}`)
    ContentChatRef.value.addMessage(false, true, '')
    const formData = new FormData();
    console.log(data.file.name)
    formData.append("file", data.file);
    try {
        const result = await api.requestAttachment(formData)
        result['isUser'] = false
        ContentChatRef.value.addMessage(false, false, result)

    } catch (error) {
        console.error('API error loadAttachment:', error);
    }
}

const cleanChat = () => {
    ContentChatRef.value.cleanMessages(); // Borra los mensajes del chat
    localStorage.removeItem("conversation_id"); // Borra el conversation_id
    console.log("Chat y conversation_id eliminados");
};

onMounted(() => {
    localStorage.setItem('transcription', 'null');

    if (!localStorage.getItem("conversation_id")) {
        localStorage.setItem("conversation_id", Date.now().toString()); // Generar ID único si no existe
    }

    ContentChatRef.value.addMessage(false, false, { 
        text: "¡Hola! 👋 Soy tu asistente virtual, listo para ayudarte a tomar tu pedido.", 
        id: Math.random(), 
        isUser: false 
    });
});
</script>

<template>
    <div class="cardContent">
        <div class="cardContent-content">
            <Header @clean="cleanChat"/>
            <ContentChat ref="ContentChatRef" @pushed_vote="fetchVote" />
            <InputChat @pushed_message="UpChat" @file_loaded="loadAttachment" />
        </div>
    </div>
</template>

<style scoped>
.cardContent {
    display: flex;
    flex-direction: column;
    padding: 20px;
    height: 100%;
    border-radius: 8px;
    background-color: #f8f8f8;
    overflow: hidden;
}

.cardContent-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
    overflow: hidden;
}
</style>