<template>
  <div class="solver-controls">
    <!-- Solver Selection Section -->
    <Card class="control-section">
      <template #title>
        <div class="section-title">
          <i class="pi pi-cog" style="margin-right: 0.5rem;"></i>
          Solver Controls
        </div>
      </template>
      <template #content>
        <div class="control-actions">
          <!-- Solver Selection -->
          <div class="solver-selection">
            <label for="solver-dropdown" class="field-label">Choose Solver:</label>
            <Dropdown 
              id="solver-dropdown"
              v-model="selectedSolver" 
              :options="sudokuStore.solvers"
              option-label="name"
              option-value="name"
              placeholder="Select a solver"
              :loading="sudokuStore.solverLoading"
              :disabled="sudokuStore.loading || sudokuStore.solvers.length === 0"
              class="solver-dropdown"
            />
          </div>
          
          <!-- Solver Options -->
          <div class="solver-options">
            <div class="checkbox-wrapper">
              <Checkbox 
                v-model="showSteps" 
                input-id="show-steps"
                binary
                :disabled="sudokuStore.loading"
              />
              <label for="show-steps" class="checkbox-label">
                Show step-by-step solution
              </label>
            </div>
          </div>
          
          <!-- Solve Button -->
          <Button 
            label="Solve Puzzle" 
            icon="pi pi-play"
            @click="solvePuzzle"
            :loading="sudokuStore.loading"
            :disabled="!selectedSolver || sudokuStore.gridState?.is_empty"
            severity="success"
            class="solve-button"
          />
        </div>
      </template>
    </Card>

    <!-- Step Navigation Section (when solution is available) -->
    <Card v-if="sudokuStore.solutionInfo" class="control-section">
      <template #title>
        <div class="section-title">
          <i class="pi pi-step-forward" style="margin-right: 0.5rem;"></i>
          Step-by-step Solution
        </div>
      </template>
      <template #content>
        <div class="step-controls">
          <!-- Navigation Buttons -->
          <div class="nav-buttons">
            <Button 
              icon="pi pi-chevron-left"
              label="Previous"
              @click="previousStep"
              :disabled="!sudokuStore.solutionInfo?.can_go_prev || sudokuStore.loading"
              severity="secondary"
              class="nav-button"
            />
            
            <Button 
              icon="pi pi-chevron-right"
              label="Next"
              @click="nextStep"
              :disabled="!sudokuStore.solutionInfo?.can_go_next || sudokuStore.loading"
              severity="secondary"
              class="nav-button"
            />
          </div>
          
          <!-- Step Counter -->
          <div class="step-info">
            <div class="step-counter">
              Step {{ (sudokuStore.solutionInfo?.current_step || 0) + 1 }} 
              of {{ sudokuStore.solutionInfo?.total_steps || 0 }}
            </div>
            
            <!-- Current Step Description -->
            <div v-if="sudokuStore.solutionInfo?.current_description" class="step-description">
              <small>{{ sudokuStore.solutionInfo.current_description }}</small>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- Performance Metrics Section -->
    <Card v-if="sudokuStore.performanceMetrics" class="control-section">
      <template #title>
        <div class="section-title">
          <i class="pi pi-chart-line" style="margin-right: 0.5rem;"></i>
          Performance
        </div>
      </template>
      <template #content>
        <div class="performance-metrics">
          <div class="metric-item">
            <span class="metric-label">Solve Time:</span>
            <span class="metric-value">
              {{ sudokuStore.performanceMetrics.solve_time?.toFixed(4) }}s
            </span>
          </div>
          
          <div v-if="sudokuStore.performanceMetrics.step_count" class="metric-item">
            <span class="metric-label">Steps:</span>
            <span class="metric-value">
              {{ sudokuStore.performanceMetrics.step_count }}
            </span>
          </div>
          
        </div>
      </template>
    </Card>

    <!-- Solver Status Messages -->
    <div v-if="sudokuStore.loading" class="status-section">
      <Message severity="info" :closable="false">
        <div class="solving-status">
          <ProgressBar mode="indeterminate" />
          <span>Solving puzzle...</span>
        </div>
      </Message>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useSudokuStore } from '@/stores/sudoku'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import Checkbox from 'primevue/checkbox'
import Message from 'primevue/message'
import ProgressBar from 'primevue/progressbar'

const sudokuStore = useSudokuStore()

// Component state
const selectedSolver = ref<string>('')
const showSteps = ref<boolean>(true)

// Load solvers and initialize with first available solver
onMounted(async () => {
  if (sudokuStore.solvers.length === 0) {
    await sudokuStore.loadSolvers()
  }
  if (sudokuStore.solvers.length > 0 && !selectedSolver.value) {
    selectedSolver.value = sudokuStore.solvers[0].name
  }
})

// Watch for solvers to load and set default
watch(() => sudokuStore.solvers, (newSolvers) => {
  if (newSolvers.length > 0 && !selectedSolver.value) {
    selectedSolver.value = newSolvers[0].name
  }
})

// Solver operations
const solvePuzzle = async () => {
  if (!selectedSolver.value) return
  
  await sudokuStore.solvePuzzle(selectedSolver.value, showSteps.value)
}

// Step navigation
const previousStep = async () => {
  await sudokuStore.prevStep()
}

const nextStep = async () => {
  await sudokuStore.nextStep()
}
</script>

<style scoped>
.solver-controls {
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

.solver-selection {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-label {
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
}

.solver-dropdown {
  width: 100%;
}

.solver-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-label {
  font-size: 0.9rem;
  color: #495057;
  cursor: pointer;
}

.solve-button {
  width: 100%;
  justify-content: center;
  font-weight: 600;
}

.step-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.nav-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.nav-button {
  justify-content: center;
}

.step-info {
  text-align: center;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.step-counter {
  font-weight: 600;
  color: #495057;
  font-size: 1rem;
}

.step-description {
  margin-top: 0.5rem;
  color: #6c757d;
  font-style: italic;
}

.performance-metrics {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0;
}

.metric-label {
  font-weight: 600;
  color: #6c757d;
}

.metric-value {
  font-weight: 700;
  color: #495057;
}

.status-section {
  width: 100%;
}

.solving-status {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
  text-align: center;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .solver-controls {
    gap: 1rem;
  }
  
  .control-actions {
    gap: 0.75rem;
  }
  
  .nav-buttons {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
}
</style>