<template>
  <div class="sidebar-controls">
    <!-- File Operations Section -->
    <Card class="control-section">
      <template #title>
        <div class="section-title">
          <i class="pi pi-folder" style="margin-right: 0.5rem;"></i>
          File Operations
        </div>
      </template>
      <template #content>
        <div class="control-actions">
          <!-- File Upload -->
          <div class="file-upload-section">
            <FileUpload 
              mode="basic" 
              :auto="false"
              :multiple="false"
              accept=".json,.txt"
              :max-file-size="1000000"
              choose-label="Upload Sudoku Puzzle"
              :custom-upload="true"
              @uploader="handleFileUpload"
              @select="onFileSelect"
              @remove="onFileRemove"
              class="upload-button"
            />
            <small class="upload-help">
              Supports JSON and TXT formats
            </small>
          </div>
          
          <!-- Download Button -->
          <Button 
            label="Download Current Puzzle" 
            icon="pi pi-download"
            @click="downloadPuzzle"
            :loading="sudokuStore.loading"
            severity="secondary"
            class="download-button"
          />
        </div>
      </template>
    </Card>

    <!-- Grid Operations Section -->
    <Card class="control-section">
      <template #title>
        <div class="section-title">
          <i class="pi pi-cog" style="margin-right: 0.5rem;"></i>
          Grid Operations
        </div>
      </template>
      <template #content>
        <div class="control-actions">
          <Button 
            label="Clear Grid" 
            icon="pi pi-trash"
            @click="clearGrid"
            :loading="sudokuStore.loading"
            severity="danger"
            class="grid-button"
          />
          
          <Button 
            label="Load Sample Puzzle" 
            icon="pi pi-file"
            @click="loadSample"
            :loading="sudokuStore.loading"
            class="grid-button"
          />
        </div>
      </template>
    </Card>
    
    <!-- Error Display -->
    <div v-if="sudokuStore.error" class="error-section">
      <Message 
        severity="error" 
        :closable="true" 
        @close="sudokuStore.clearError()"
      >
        {{ sudokuStore.error }}
      </Message>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useSudokuStore } from '@/stores/sudoku'
import Card from 'primevue/card'
import Button from 'primevue/button'
import FileUpload from 'primevue/fileupload'
import Message from 'primevue/message'

const sudokuStore = useSudokuStore()
const selectedFile = ref<File | null>(null)

// File upload handlers
const onFileSelect = (event: any) => {
  selectedFile.value = event.files[0]
}

const onFileRemove = () => {
  selectedFile.value = null
}

const handleFileUpload = async (event: any) => {
  if (!selectedFile.value) return
  
  try {
    await sudokuStore.loadPuzzleFromFile(selectedFile.value)
    selectedFile.value = null
  } catch (error) {
    console.error('Upload failed:', error)
  }
}

// Grid operations
const clearGrid = async () => {
  await sudokuStore.clearGrid(false)
}

const loadSample = async () => {
  await sudokuStore.loadSamplePuzzle()
}

// File download
const downloadPuzzle = async () => {
  await sudokuStore.savePuzzle()
}
</script>

<style scoped>
.sidebar-controls {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.control-section {
  width: 100%;
}

.section-title {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #495057;
}

.control-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.file-upload-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.upload-help {
  color: #6c757d;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.download-button,
.grid-button {
  width: 100%;
  justify-content: flex-start;
}

:deep(.upload-button .p-fileupload-choose) {
  width: 100%;
  justify-content: flex-start;
}

:deep(.upload-button .p-button-label) {
  flex: 1;
  text-align: left;
}

.error-section {
  width: 100%;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .sidebar-controls {
    gap: 1rem;
  }
  
  .control-actions {
    gap: 0.75rem;
  }
}
</style>