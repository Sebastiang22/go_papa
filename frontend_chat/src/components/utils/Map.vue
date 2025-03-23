<template>
    <div id="map" ref="mapContainer"></div>
</template>

<script setup>
import { onMounted, ref, inject } from 'vue';

const props = defineProps({
    xy: {
        type: Array,
        required: true,
    },
    ubication: {
        type: String,
        required: true,
    }
});

const mapContainer = ref(null);
const maps = props.xy || [];

onMounted(() => {
    if (navigator.onLine) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.css';
        document.head.appendChild(link);

        const script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.js';
        if (maps.length > 0) {
            script.onload = () => {
                const L = window.L;
                const map = L.map(mapContainer.value).setView(maps, 14);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors'
                }).addTo(map);

                L.marker(maps).addTo(map)
                    .bindPopup(props.ubication)
                    .openPopup();
            };
            document.body.appendChild(script);
        }
    } else {
        console.warn('No internet connection, map cannot be loaded.');
    }
});
</script>

<style scoped>
#map {
    z-index: 1;
    height: 100%;
    width: 100%;
    min-height: 400px;
}
</style>