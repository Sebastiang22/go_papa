<template>
    <div class="ai">
        <div class="typing" v-if="props.msg.isLoading">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
        </div>
        <div v-else>
            <div class="content">
                <div v-for="(content, index) in extractedContent" :key="index">
                    <div v-if="content.type === 'citations'" class="citations section" v-html="content.value"></div>
                    <div v-else-if="content.type === 'table'" class="table section">
                        <table v-html="content.value"></table>
                    </div>
                    <div v-else-if="content.type === 'code'" class="code">
                        <div class="code-header">
                            <span>{{ content.lang }}</span>
                            <button class="copy-button" @click="copyToClipboard(content.value)">
                                <i class="fa-solid fa-copy"></i>
                            </button>
                        </div>
                        <pre v-html="content.value"></pre>
                    </div>
                    <div v-else-if="content.type === 'chart'" class="section">
                        <component :is="getChartComponent(content.chartType)" :data="content.data"
                            :options="content.options" :style="{ height: '400px' }" />
                    </div>
                    <div v-else-if="content.type === 'card'" class="section">
                        <CardAdaptative :cardPayload="content.value" />
                    </div>
                    <div v-else-if="content.type === 'doc'" class="section">
                        <Doc :docPayload="content.value" />
                    </div>
                    <div v-else-if="content.type === 'map'" class="section">
                        <Map :xy="content.xy" :ubication="content.ubication" />
                    </div>
                    <div v-else-if="content.type === 'image'" class="section">
                        <img :src="content.value" alt="Image Content" />
                    </div>
                    <div v-else v-html="content.value"></div>
                </div>
            </div>
            <div class="feedback" v-if="!msg.isFirst">
                <button @click="handlevote(true)" :class="{ 'voted': selectedVote }" :disabled="selectedVote !== null">
                    <i class="fa-regular fa-thumbs-up"></i>
                </button>
                <button @click="handlevote(false)" :class="{ 'voted': selectedVote === false }"
                    :disabled="selectedVote !== null">
                    <i class="fa-regular fa-thumbs-down"></i>
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { inject, computed, ref, onMounted } from 'vue'
import { Chart, BarElement, BarController, PieController, CategoryScale, LinearScale, ArcElement, Tooltip, Legend, LineController, PointElement, LineElement } from 'chart.js';
import { Bar, Pie, Line } from 'vue-chartjs';
import { marked } from 'marked';
import CardAdaptative from './CardAdaptative.vue';
import Doc from './Doc.vue';
import Map from './Map.vue';
import api from '../../api';

Chart.register(BarElement, BarController, PieController, CategoryScale, LinearScale, ArcElement, Tooltip, Legend, LineController, PointElement, LineElement);

const props = defineProps({
    msg: {
        type: Object,
        required: true,
    },
})
const emit = defineEmits(['vote'])

const selectedVote = ref(null);

const regex = /<(citations|table|chart|code|doc|image|card|map)>(.*?)<\/\1>/gs;
const extractedContent = ref([]);

const cleanContent = (content) => {
    const trimmedContent = content.trim().replace(/\n\s*\n/g, '\n').replace(/\n/g, '<br>').replace(/-\s/g, "• ");
    return marked(trimmedContent);
};
const chartComponents = {
    'bar': Bar,
    'pie': Pie,
    'line': Line,
};
const getChartComponent = (chartType) => {
    return chartComponents[chartType] || Bar;
};

const typeHandlers = {
    'code': (p2) => {
        const codeMatch = /```(\w*)\n([\s\S]*?)```/.exec(p2);
        return {
            type: 'code',
            value: cleanContent(codeMatch ? codeMatch[2] : p2),
            lang: codeMatch ? codeMatch[1] : 'plain-text',
        };
    },
    'chart': (p2) => {
        const chartData = JSON.parse(p2);
        console.log(chartData.data);
        return {
            type: 'chart',
            chartType: chartData.type,
            data: chartData.data,
            options: chartData.options || {},
        };
    },
    'card': (p2) => {
        const cardData = JSON.parse(p2);
        return {
            type: 'card',
            value: cardData,
        };
    },
    /*'doc': (p2) => {
        const cardData = JSON.parse(p2);
        return {
            type: 'doc',
            value: cardData,
        };
    },*/
    'map': (p2) => {
        const mapData = JSON.parse(p2);
        return {
            type: 'map',
            xy: mapData.xy,
            ubication: mapData.ubication,
        };
    }
    /*'table': (p2) => ({
        type: 'table',
        value: cleanContent(p2),
    }),*/
};

const processMessage = () => {
    const messageText = props.msg.text;
    let lastIndex = 0;

    messageText.replace(regex, (match, p1, p2, offset) => {
        if (offset > lastIndex) {
            extractedContent.value.push({
                type: 'text',
                value: cleanContent(messageText.slice(lastIndex, offset).trim()),
            });
        }

        const handler = typeHandlers[p1] || ((p2) => ({
            type: p1,
            value: cleanContent(p2),
        }));

        extractedContent.value.push(handler(p2));

        lastIndex = offset + match.length;
    });

    if (lastIndex < messageText.length) {
        extractedContent.value.push({
            type: 'text',
            value: cleanContent(messageText.slice(lastIndex).trim())
        });
    }
};


const handlevote = async (vote) => {
    if (selectedVote.value === null) {
        selectedVote.value = vote;
        // Emitimos el evento 'vote' (si es necesario para otros componentes)
        const voteData = {
            "id": String(props.msg.id),
            "thread_id": "User2",
            "rate": vote 
        };
        console.log('Datos enviados:', voteData)
        try {
            // Llamamos a la función requestVote para enviar la solicitud al backend
            await api.requestVote(voteData.id, voteData.rate);
            console.log("Voto enviado con éxito");
        } catch (error) {
            console.error("Error al enviar el voto:", error);
        }
    }
};

const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
        console.log('Copied to clipboard');
    }, () => {
        console.log('Failed to copy');
    });
};

onMounted(() => {
    if (props.msg.isLoading) {
        return;
    }
    processMessage();
})
</script>

<style scoped>
.ai {
    max-width: 420px;
    padding: 10px;
    border-radius: 10px;
    background-color: #f0f0f0;
    margin-bottom: 8px;
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}
.content {
    white-space: normal;
    overflow: hidden;
    text-align: left;
    margin-bottom: 0; 
    padding-bottom: 0; 
}

.feedback {
    position: absolute;
    right: 14px;
    bottom: -14px;
    display: flex;
    gap: 10px;
}

.feedback button {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background-color: white;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    transition: background-color 0.3s ease;
}

.feedback button:hover {
    background-color: #e0e0e0;
}

.feedback button.voted {
    background-color: var(--main-color);
    opacity: 0.5;
    color: white;
}

.citations {
    font-size: small;
    color: var(--main-color);
    margin-left: 15px;
}

.section {
    margin-bottom: 10px;
}

.table {
    border: 1px solid black;
    margin: 10px;
}

.code {
    background-color: #2d2d2d;
    color: #f8f8f2;
    border-radius: 5px;
    padding: 10px;
    margin: 10px 0;
    position: relative;
}

.code pre {
    white-space: pre-wrap;
    overflow: auto;
}

.code-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #9c9898;
    padding: 5px;
    border-radius: 5px 5px 0 0;
}

.copy-button {
    position: absolute;
    right: 15px;
    background: none;
    border: none;
    color: #f8f8f2;
    cursor: pointer;
    font-size: 14px;
    padding: 5px;
    border-radius: 3px;
    background-color: #6272a4;
    transition: background-color 0.3s ease;
}

.copy-button:hover {
    background-color: #50fa7b;
}

.typing {
    display: flex;
    justify-content: center;
    align-items: center;
}

.dot {
    width: 10px;
    height: 10px;
    margin: 5px 5px;
    background-color: #333;
    border-radius: 50%;
    animation: blink 1.4s infinite both;
}

.dot:nth-child(1) {
    animation-delay: 0.2s;
}

.dot:nth-child(2) {
    animation-delay: 0.4s;
}

.dot:nth-child(3) {
    animation-delay: 0.6s;
}

@keyframes blink {

    0%,
    80%,
    100% {
        opacity: 0;
    }

    40% {
        opacity: 1;
    }
}

@media (max-width: 768px) {
    .ai {
        padding: 5px 10px 15px 10px;
        margin-bottom: 12px;
        font-size: 15px;
    }
}
</style>