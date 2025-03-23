<template>
    <div ref="cardContainer"></div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue';
import * as AdaptiveCards from 'adaptivecards';

const props = defineProps({
    cardPayload: {
        type: Object,
        required: true,
    }
});

AdaptiveCards.AdaptiveCard.onProcessMarkdown = (text, result) => {
    result.outputHtml = text;
    result.didProcess = true; 
};

const cardContainer = ref(null);

const renderCard = () => {
    const adaptiveCard = new AdaptiveCards.AdaptiveCard();
    adaptiveCard.parse(props.cardPayload);
    const renderedCard = adaptiveCard.render();
    cardContainer.value.innerHTML = "";
    cardContainer.value.appendChild(renderedCard);
};

onMounted(() => {
    renderCard();
});

watch(() => props.cardPayload, () => {
    renderCard();
});
</script>

<style scoped>
div {
    padding: 10px;
}
</style>