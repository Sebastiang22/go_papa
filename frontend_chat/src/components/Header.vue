<script setup>
import { ref } from 'vue'
import { sharedState } from '../state'

const emit = defineEmits(['clean'])

const cleanMessage = () => {
    emit('clean')
}
</script>

<template>
    <div class="header"> Hola
        <strong :style="{ color: '#6b2329' }">{{ sharedState.name }}</strong>, 
        Estás usando el <span class="main-color" style="text-decoration: underline; cursor: pointer;"
            ><strong> <a href="https://www.instagram.com/lingui.ai?igsh=M2J0MGtnYTF0eHNt" target="_blank" style="text-decoration: none; color: inherit;">Chat de Tars</a></strong> </span>. Estaré encantado de ayudarte!
        <!-- <div class="tooltip-container">
            <i class="fas fa-trash clean-icon main-color" @click="cleanMessage"></i>
            <span class="tooltip-text">Limpiar mensajes</span>
        </div> -->
    </div>
</template>

<style scoped>
.header {
    padding: 0px 10px 15px 10px;
    border-bottom: 1px solid #ccc;
    font-size: 14px;
    text-align: left;
    position: relative;
}

.tooltip-container {
    position: absolute;
    top: 10px;
    right: 10px;
    cursor: pointer;
}

.tooltip-text {
    visibility: hidden;
    width: 120px;
    background-color: #555;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 5px;
    position: absolute;
    z-index: 1;
    top: 50%;
    right: 165%;
    margin-top: -20px;
    opacity: 0;
    transition: opacity 0.3s;
    font-size: 12px;
}

.clean-icon {
    transition: transform 0.3s;
}

.tooltip-container:hover .clean-icon {
    transform: scale(1.2);
}

.tooltip-container:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
}

@media (max-width: 768px) {
  .header {
    padding: 0px 0px 10px 0px;
    font-size: 12px;
  }
}
</style>