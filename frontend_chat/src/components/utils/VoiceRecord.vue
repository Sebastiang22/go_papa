<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
    elapsedTime: Number,
    audioUrl: String,
    reset: Boolean,
});

const isRecording = ref(false)
const emit = defineEmits(['startRecording', 'stopRecording', 'clearRecording'])

const dynamicClasses = computed(() => {
  return {
    'voice-input': true,
    'active': props.reset,
    'inactive': !props.reset
  }
})
const startRecording = () => {
    clearRecording()
    isRecording.value = true
    emit('startRecording')
}
const stopRecording = () => {
    isRecording.value = false
    emit('stopRecording')
}
const clearRecording = () => {
    isRecording.value = false
    emit('clearRecording')
}
</script>

<template>
    <div :class="dynamicClasses">
        <button @click="startRecording" v-if="!isRecording">
            <i class="fa-solid fa-microphone input-icon main-color"></i>
        </button>
        <button @click="stopRecording" v-else>
            <div class="recording-indicator">({{ elapsedTime }}s)</div>
        </button>
        <audio :src="audioUrl" controls v-if="reset" class="audio_str"></audio>
        <button @click="clearRecording" v-if="reset">
            <i class="fa-solid fa-trash-arrow-up clean-icon"></i>
        </button>
    </div>
</template>

<style scoped>
.active{
    width: 100%;
}
.inactive{
    width: 0%;
}
.recording-indicator {
    color: red;
    font-weight: bold;
}

.input-icon {
    cursor: pointer;
    font-size: 21px;
}

.clean-icon {
    cursor: pointer;
    font-size: 16px;
    color: brown;
    margin-left: 10px
}

.voice-input {
    display: flex;
    flex-direction: row;
    align-items: center;
    align-content: center;
    justify-content: flex-start;
}

.audio_str {
    width: calc(100% - 140px);
    height: 5vh;
    margin-left: 10px;
}
</style>