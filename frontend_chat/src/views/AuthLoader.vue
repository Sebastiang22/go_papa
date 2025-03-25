<template>
    <div class="loader-container">
        <div class="loader">
            <div class="spinner"></div>
            <p class="color-title">{{ message }}</p>
        </div>
    </div>
</template>

<script setup>

const props = defineProps({
    message: {
        type: String,
        required: true
    }
})
</script>

<style scoped>
.loader-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: #e0e0e0;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    transition: opacity 0.5s;
}

.loader {
    text-align: center;
}

.spinner {
    margin: 0 auto;
    width: 50px;
    height: 50px;
    border: 6px solid #ccc;
    border-top-color: var(--main-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

.color-title{
    color: var(--primary-color);
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

p {
    margin-top: 20px;
    font-size: 1.2em;
}
</style>