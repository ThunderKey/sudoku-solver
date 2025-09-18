<template>
  <div class="sudoku-container">
    <div class="sudoku-header">
      <h2>Sudoku Grid</h2>
    </div>
    
    <div class="sudoku-grid-wrapper">
      <div class="sudoku-grid">
        <div 
          v-for="(row, i) in 9" 
          :key="i" 
          class="sudoku-row"
        >
          <InputNumber
            v-for="(col, j) in 9"
            :key="`${i}-${j}`"
            v-model="gridValues[i][j]"
            :class="getCellClasses(i, j)"
            :disabled="isCellGiven(i, j)"
            :min="0"
            :max="9"
            :use-grouping="false"
            :allow-empty="true"
            :placeholder="''"
            size="small"
            @update:modelValue="handleCellChange(i, j, $event)"
          />
        </div>
      </div>
    </div>
    
    <div v-if="sudokuStore.gridState && !sudokuStore.gridState.is_empty" class="validation-status">
      <Message 
        v-if="sudokuStore.gridState.is_complete && sudokuStore.gridState.is_valid" 
        severity="success"
      >
        🎉 Puzzle solved!
      </Message>
      <Message 
        v-else-if="sudokuStore.gridState.is_valid" 
        severity="success"
      >
        ✅ Current state is valid
      </Message>
      <Message 
        v-else-if="sudokuStore.hasConflicts" 
        severity="error"
      >
        ❌ Current state has conflicts
      </Message>
    </div>
    
    <div v-if="sudokuStore.loading" class="loading-overlay">
      <ProgressBar mode="indeterminate" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useSudokuStore } from '@/stores/sudoku'
import InputNumber from 'primevue/inputnumber'
import Message from 'primevue/message'
import ProgressBar from 'primevue/progressbar'

const sudokuStore = useSudokuStore()

// Local grid values for immediate UI updates
const gridValues = ref<(number | null)[][]>(Array(9).fill(null).map(() => Array(9).fill(null)))

// Initialize grid values when store data changes
watch(() => sudokuStore.gridState, (newState) => {
  if (newState) {
    for (let i = 0; i < 9; i++) {
      for (let j = 0; j < 9; j++) {
        gridValues.value[i][j] = newState.grid[i][j] === 0 ? null : newState.grid[i][j]
      }
    }
  }
}, { immediate: true, deep: true })

// Check if cell is from original puzzle (given)
const isCellGiven = (row: number, col: number): boolean => {
  return sudokuStore.gridState?.given_cells?.[row]?.[col] || false
}

// Check if cell has conflicts
const hasConflict = (row: number, col: number): boolean => {
  if (!sudokuStore.gridState?.conflicts) return false
  
  return sudokuStore.gridState.conflicts.some(conflict => 
    conflict.row === row && conflict.col === col
  )
}

// Get CSS classes for cell styling
const getCellClasses = (row: number, col: number): string[] => {
  const classes = ['sudoku-cell']
  
  // Add thick borders for 3x3 box separation
  if (col === 2 || col === 5) classes.push('thick-right-border')
  if (row === 2 || row === 5) classes.push('thick-bottom-border')
  if (col === 0) classes.push('thick-left-border')
  if (row === 0) classes.push('thick-top-border')
  if (col === 8) classes.push('thick-right-border')
  if (row === 8) classes.push('thick-bottom-border')
  
  // Add styling for given cells
  if (isCellGiven(row, col)) classes.push('given-cell')
  
  // Add styling for conflicts
  if (hasConflict(row, col)) classes.push('conflict-cell')
  
  return classes
}

// Handle cell value changes
const handleCellChange = async (row: number, col: number, value: number | null) => {
  // Validate input (1-9 or null for empty)
  if (value !== null && (value < 1 || value > 9)) {
    // Reset to original value
    const originalValue = sudokuStore.gridState?.grid[row][col]
    gridValues.value[row][col] = originalValue === 0 ? null : originalValue || null
    return
  }
  
  // Update local state immediately for responsive UI
  gridValues.value[row][col] = value
  
  // Also update backend immediately for conflict detection
  const currentValue = value ?? 0
  const originalValue = sudokuStore.gridState?.grid[row][col] || 0
  
  // Only update backend if value actually changed
  if (currentValue !== originalValue) {
    const success = await sudokuStore.updateCell(row, col, currentValue)
    
    if (!success) {
      // Reset to original value if update failed
      const resetValue = originalValue === 0 ? null : originalValue
      gridValues.value[row][col] = resetValue
    }
  }
}

// Validate and update cell through API
const validateAndUpdateCell = async (row: number, col: number) => {
  const currentValue = gridValues.value[row][col] ?? 0
  const originalValue = sudokuStore.gridState?.grid[row][col] || 0
  
  // Only update if value changed
  if (currentValue !== originalValue) {
    const success = await sudokuStore.updateCell(row, col, currentValue)
    
    if (!success) {
      // Reset to original value if update failed
      const resetValue = originalValue === 0 ? null : originalValue
      gridValues.value[row][col] = resetValue
    }
  }
}

// Grid is initialized by App.vue, so we don't need to load it here
// Just ensure we have the data when component mounts
onMounted(() => {
  // Grid initialization is handled by App.vue
})
</script>

<style scoped>
.sudoku-container {
  position: relative;
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.sudoku-header {
  text-align: center;
  margin-bottom: 20px;
}

.sudoku-header h2 {
  font-family: Arial, sans-serif;
  color: #333;
  margin: 0;
}

.sudoku-grid-wrapper {
  background: #ffffff;
  border: 3px solid #000000;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.sudoku-grid {
  display: grid;
  grid-template-rows: repeat(9, 1fr);
  gap: 0;
  background: #ffffff;
}

.sudoku-row {
  display: grid;
  grid-template-columns: repeat(9, 1fr);
  gap: 0;
}

.sudoku-cell {
  width: 50px !important;
  height: 50px !important;
  border: 1px solid #ddd !important;
  border-radius: 0 !important;
  text-align: center !important;
  font-family: Arial, sans-serif !important;
  font-size: 18px !important;
  font-weight: bold !important;
  color: #333333 !important;
  background-color: #ffffff !important;
}

/* Input field specific styling */
:deep(.sudoku-cell input) {
  width: 100% !important;
  height: 100% !important;
  text-align: center !important;
  font-family: Arial, sans-serif !important;
  font-size: 18px !important;
  font-weight: bold !important;
  color: #333333 !important;
  background-color: transparent !important;
  border: none !important;
  border-radius: 0 !important;
  outline: none !important;
  padding: 0 !important;
  margin: 0 !important;
}

:deep(.sudoku-cell:hover input) {
  background-color: #f0f8ff !important;
}

:deep(.sudoku-cell:focus-within) {
  outline: 2px solid #4a90e2 !important;
  outline-offset: -2px !important;
}

/* Given cells styling */
:deep(.given-cell) {
  background-color: #f8f9fa !important;
}

:deep(.given-cell input) {
  background-color: #f8f9fa !important;
  color: #212529 !important;
  cursor: not-allowed !important;
}

/* Conflict cells styling */
:deep(.conflict-cell) {
  background-color: #ffe6e6 !important;
}

:deep(.conflict-cell input) {
  background-color: #ffe6e6 !important;
  color: #dc3545 !important;
}

/* 3x3 box separation borders */
.thick-right-border {
  border-right: 3px solid #000000 !important;
}

.thick-bottom-border {
  border-bottom: 3px solid #000000 !important;
}

.thick-left-border {
  border-left: 3px solid #000000 !important;
}

.thick-top-border {
  border-top: 3px solid #000000 !important;
}

.validation-status {
  margin-top: 20px;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

/* Responsive design */
@media (max-width: 768px) {
  .sudoku-grid-wrapper {
    padding: 5px;
  }
  
  .sudoku-cell {
    width: 40px !important;
    height: 40px !important;
    font-size: 16px !important;
  }
  
  :deep(.sudoku-cell input) {
    font-size: 16px !important;
  }
}

@media (max-width: 480px) {
  .sudoku-cell {
    width: 35px !important;
    height: 35px !important;
    font-size: 14px !important;
  }
  
  :deep(.sudoku-cell input) {
    font-size: 14px !important;
  }
}
</style>