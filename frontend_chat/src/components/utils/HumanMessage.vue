<script setup>
import { onMounted, ref } from 'vue';
import Doc from './Doc.vue'

let urlaudio = ref('')
let textaudio = ref('')

const props = defineProps({
    msg: {
        type: Object,
        required: true
    },
})

const getFileType = (fileName) => {
    const isFile = fileName.split('@').shift()
    return isFile
};

const getAudio = () => {
    const audio = props.msg.text.split('@').pop().split('#')
    textaudio.value = audio.shift()
    urlaudio.value = audio.pop()
};

onMounted(() => {
    getAudio()
});

</script>

<template>
    <div class="user">
        <span v-if="getFileType(msg.text) == 'file'">
            {{'Has cargado un ocumento adjunto:'}}
            <Doc :docPayload="msg.text" />
        </span>
        <span v-else-if="getFileType(msg.text) == 'audio'" class="audioText">
            {{textaudio}}
            <audio :src="urlaudio" controls style="margin-top: 5px;"></audio>
        </span>
        <span v-else>{{ msg.text }}</span>
    </div>
</template>

<style scoped>
.user {
    max-width: 420px;
    min-width: 50px;
    padding: 1% 2% 1.5% 2%;
    border-radius: 10px;
    background-color: #d1edff;
    margin-left: auto;
    white-space: pre-wrap;
    overflow: hidden;
    user-select: text;
    text-align: left;
}

.audioText{
    display: flex;
    flex-direction: column;
}

@media (max-width: 768px) {
    .user {
        font-size: 14px;
    }
}
</style>