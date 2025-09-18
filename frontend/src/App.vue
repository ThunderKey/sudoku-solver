<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useSudokuStore } from '@/stores/sudoku'

const sudokuStore = useSudokuStore()

onMounted(async () => {
  // Initialize the application once
  if (!sudokuStore.initialized) {
    await Promise.all([
      sudokuStore.loadGrid(),
      sudokuStore.loadSolvers()
    ])
    sudokuStore.initialized = true
  }
})
</script>

<template>
  <div id="app" class="app-container">
    <header class="app-header">
      <h1>Sudoku Solver</h1>
      <p class="subtitle">Interactive Sudoku Puzzle Solver with Step-by-Step Solutions</p>
    </header>

    <main class="app-main">
      <RouterView />
    </main>

    <footer class="app-footer">
      <p>&copy; 2025 Sudoku Solver - Built with Vue.js and PrimeVue</p>
    </footer>
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: Arial, sans-serif;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  padding: 2rem 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2.5rem;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.subtitle {
  margin: 0;
  font-size: 1.1rem;
  opacity: 0.9;
  font-weight: 300;
}

.app-main {
  flex: 1;
  background: #f8f9fa;
  padding: 2rem 1rem;
}

.app-footer {
  background: #343a40;
  color: #adb5bd;
  text-align: center;
  padding: 1rem;
  font-size: 0.9rem;
}

.app-footer p {
  margin: 0;
}

@media (max-width: 768px) {
  .app-header h1 {
    font-size: 2rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .app-main {
    padding: 1rem 0.5rem;
  }
}
</style>
