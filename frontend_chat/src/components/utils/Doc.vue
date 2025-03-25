<template>
    <div class="card">
        <div class="card-content">
            <div class="file-icon" :style="{ backgroundColor: backgroundColor }">
                <span>{{ getFileType(docPayload) }}</span>
            </div>
            <div class="file-info">
                <p class="file-name">{{ getFileName(docPayload) }}</p>
            </div>
            <button class="download-arrow" @click="openFile(docPayload)" v-if="getFileOwn(docPayload)">
                <i class="fa fa-external-link"></i>
            </button>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
    docPayload: {
        type: String,
        required: true,
    },
});

const fileType = ref('')
const getFileType = (fileName) => {
    const extension = fileName.split('.').pop().toUpperCase();
    return extension || 'DOC';
};

const getFileName = (fileName) => {
    return fileName.split('@').pop().split('/').pop().split('.').shift();
};

const getFileOwn = (fileName) => {
    const isNotFile = (fileName.split('@').shift() != 'file')
    return isNotFile
};

const openFile = (fileUrl) => {
    window.open(fileUrl, '_blank');
};

const getBackgroundColor = (fileName) => {
  const extension = getFileType(fileName);
  switch (extension) {
    case 'PDF':
      return 'rgb(238, 67, 67)';
    case 'DOC':
    case 'DOCX':
      return 'rgb(79, 165, 236)';
    case 'XLS':
    case 'XLSX':
      return 'rgb(78, 241, 78)';
    default:
      return 'rgb(197, 197, 197)';
  }
};

const backgroundColor = computed(() => {
  return getBackgroundColor(props.docPayload);
});
</script>

<style scoped>
.card {
    display: flex;
    align-items: center;
    background-color: #ffffff9a;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    padding: 12px 16px;
    max-width: 400px;
    margin: 8px 3px;
    gap: 12px;
    font-family: Arial, sans-serif;
    user-select: none;
}

.card-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
}

.file-icon {
    background-color: #f4f4f4;
    border: 1px solid #ccc;
    border-radius: 8px;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: bold;
    color: #666;
}

.file-info {
    flex: 1;
    margin-left: 12px;
}

.file-name {
    font-size: 14px;
    font-weight: 600;
    color: var(--primary-color);
    margin: 0;
    width: 200px;
    white-space: nowrap;
    overflow: hidden; 
    text-overflow: ellipsis;
}

.download-arrow {
    background-color: var(--secundary-color);
    color: var(--primary-color);
    border: none;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.download-arrow:hover {
    background-color: var(--primary-color);
    color: var(--secundary-color);
}

.bg-blue {
  background-color: rgb(79, 165, 236);
  color: white;
}
.bg-green {
  background-color: rgb(78, 241, 78);
  color: white;
}
.bg-red {
  background-color: rgb(197, 197, 197);
  color: white;
}
</style>