<script setup>

import AIMessage from './utils/IAMessage.vue'
import UserMessage from './utils/HumanMessage.vue'
import { ref, inject, nextTick, watch, computed } from 'vue'

const emit = defineEmits(['pushed_vote'])
const scrollContainer = ref(null);

const addMessage = (isUser, isLoading, newMessage) => {
    if (isUser) {
        handleUserMessage(isLoading, newMessage);
    } else {
        handleBotMessage(isLoading, newMessage);
    }
    scrollToBottom();
};

const handleUserMessage = (isLoading, newMessage) => {
    if (isLoading) {
        messages.value.push({ text: "procesando audio...", isUser: true, isLoading });
    } else {
        if (messages.value[messages.value.length - 1]?.isUser) {
            messages.value.pop();
        }
        const message = {
            id: messages.value.length + 1,
            isUser: true,
            text: newMessage,
        };
        messages.value.push(message);
    }

};

const handleBotMessage = (isLoading, newMessage) => {
    if (isLoading) {
        messages.value.push({ isUser: false, isLoading });
    } else {
        if (messages.value.length === 0) {
            newMessage.isFirst = true;
        } else {
            newMessage.isFirst = false;
        }
        messages.value.pop();
        messages.value.push(newMessage);
    }
};

const handleVote = (vote) => {
    emit('pushed_vote', vote)
}

const scrollToBottom = async () => {
    await nextTick()
    const container = scrollContainer.value;
    container.scrollTop = container.scrollHeight;
};

const cleanMessages = () => {
    if (messages.value.length > 1) {
        messages.value = []
        addMessage(false, false, { text: "¡Hola! 👋 Bienvenido a GoPapa, estoy listo para tomar tu pedido!", id: Math.random(), isUser: false })
    }
}

defineExpose({
    addMessage,
    cleanMessages
});

const messages = ref([])

</script>

<template>
    <div class="chat-container">
        <div class="image-wrapper">
            <img 
                src="../assets/food-french-fries-vertical.jpg" 
                alt="Fondo de papas fritas" 
                class="bg-image bg-image-small"
            >
        </div>
        <div class="messages" ref="scrollContainer">
            <div class="message" v-for="msg in messages" :key="msg.id">
                <UserMessage :msg="msg" v-if="msg.isUser" />
                <AIMessage :msg="msg" @vote="handleVote" v-else />
            </div>
        </div>
    </div>
</template>

<style scoped>
.chat-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
    position: relative;
}

.image-wrapper {
    position: absolute;
    width: 99%;
    height: 97%;
    top: 20px;
    right: 110px;
    overflow: visible;
    display: flex;
    justify-content: center;
    align-items: center;
}

.messages {
    overflow-y: auto;
    margin-bottom: -32px;
    flex-grow: 1;
    z-index: 0;
}

.message {
    padding: 10px;
    display: flex;
}

.message:first-child {
    margin-top: 10px;
}

.message:last-child {
    margin-bottom: 40px;
}

.bg-image {
    width: 80%;
    object-fit: cover;
    position: absolute;
    opacity: 0.3;
}

.bg-image-small {
    max-width: 80%;
    top: 10%;
    left: 30%;
}

.bg-image-big {
    max-width: 58%;
    top: 7%;
    left: 46%;
}

@media (max-width: 768px) {
    .message {
        padding: 5px;
    }
    .messages {
        padding: 3px;
    }
}
</style>