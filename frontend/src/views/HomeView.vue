<script setup lang="ts">
import SudokuGrid from '@/components/SudokuGrid.vue'
import { useSudokuStore } from '@/stores/sudoku'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Message from 'primevue/message'
import Divider from 'primevue/divider'

const sudokuStore = useSudokuStore()

const loadSample = async () => {
  await sudokuStore.loadSamplePuzzle()
}

const clearGrid = async () => {
  await sudokuStore.clearGrid(false)
}

const resetToGiven = async () => {
  await sudokuStore.clearGrid(true)
}

const getStatusText = (): string => {
  const state = sudokuStore.gridState
  if (!state) return 'Unknown'
  
  if (state.is_complete && state.is_valid) return 'Solved!'
  if (state.is_valid) return 'Valid'
  if (sudokuStore.hasConflicts) return 'Has Conflicts'
  return 'Invalid'
}

const getStatusClass = (): string => {
  const state = sudokuStore.gridState
  if (!state) return 'status-unknown'
  
  if (state.is_complete && state.is_valid) return 'status-solved'
  if (state.is_valid) return 'status-valid'
  if (sudokuStore.hasConflicts) return 'status-conflict'
  return 'status-invalid'
}
</script>

<template>
  <div class="home-view">
    <div class="main-content">
      <div class="grid-section">
        <SudokuGrid />
      </div>
      
      <div class="controls-section">
        <Card class="controls-card">
          <template #title>Quick Actions</template>
          <template #content>
            <div class="action-buttons">
              <Button 
                label="Load Sample Puzzle" 
                icon="pi pi-file"
                @click="loadSample"
                :loading="sudokuStore.loading"
                class="p-button-outlined"
              />
              <Button 
                label="Clear Grid" 
                icon="pi pi-trash"
                @click="clearGrid"
                :loading="sudokuStore.loading"
                severity="secondary"
                class="p-button-outlined"
              />
              <Button 
                label="Reset to Given" 
                icon="pi pi-refresh"
                @click="resetToGiven"
                :loading="sudokuStore.loading"
                severity="info"
                class="p-button-outlined"
              />
            </div>
            
            <div v-if="sudokuStore.error" class="error-message">
              <Message severity="error" :closable="true" @close="sudokuStore.clearError()">
                {{ sudokuStore.error }}
              </Message>
            </div>
            
            <div v-if="sudokuStore.gridState && !sudokuStore.gridState.is_empty" class="grid-info">
              <Divider />
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">Filled:</span>
                  <span class="info-value">{{ sudokuStore.gridState.filled_count }}/81</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Empty:</span>
                  <span class="info-value">{{ sudokuStore.gridState.empty_count }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Status:</span>
                  <span :class="getStatusClass()">{{ getStatusText() }}</span>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-view {
  max-width: 1200px;
  margin: 0 auto;
}

.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  align-items: start;
}

.grid-section {
  display: flex;
  justify-content: center;
}

.controls-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.controls-card {
  width: 100%;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.action-buttons .p-button {
  width: 100%;
  justify-content: flex-start;
}

.error-message {
  margin: 1rem 0;
}

.grid-info {
  margin-top: 1rem;
}

.info-grid {
  display: grid;
  gap: 0.5rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0;
}

.info-label {
  font-weight: 600;
  color: #6c757d;
}

.info-value {
  font-weight: 700;
  color: #495057;
}

.status-solved {
  color: #28a745;
  font-weight: 700;
}

.status-valid {
  color: #007bff;
  font-weight: 600;
}

.status-conflict {
  color: #dc3545;
  font-weight: 600;
}

.status-invalid {
  color: #ffc107;
  font-weight: 600;
}

.status-unknown {
  color: #6c757d;
  font-weight: 600;
}

/* Responsive design */
@media (max-width: 968px) {
  .main-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .controls-section {
    order: -1;
  }
  
  .action-buttons {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .action-buttons .p-button {
    flex: 1;
    min-width: 150px;
  }
}

@media (max-width: 576px) {
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons .p-button {
    width: 100%;
  }
}
</style>
