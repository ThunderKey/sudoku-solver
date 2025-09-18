import { defineStore } from 'pinia'
import axios from 'axios'

// API base URL - use proxy configuration
const API_BASE = '/api'

export interface GridState {
  grid: number[][]
  original_grid: number[][]
  given_cells: boolean[][]
  is_empty: boolean
  is_valid: boolean
  is_complete: boolean
  empty_count: number
  filled_count: number
  conflicts: Array<{
    row: number
    col: number
    cells: number[][]
  }>
  version: number
}

export interface SolverInfo {
  name: string
  description: string
}

export interface SolutionStepInfo {
  current_step: number
  total_steps: number
  can_go_prev: boolean
  can_go_next: boolean
  current_description?: string
}

export interface PerformanceMetrics {
  solve_time: number
  step_count?: number
}

export interface SolveResponse {
  success: boolean
  message: string
  grid_state: GridState
  solution_info?: SolutionStepInfo
  performance_metrics?: PerformanceMetrics
}

export const useSudokuStore = defineStore('sudoku', {
  state: () => ({
    gridState: null as GridState | null,
    solvers: [] as SolverInfo[],
    solutionInfo: null as SolutionStepInfo | null,
    performanceMetrics: null as PerformanceMetrics | null,
    loading: false,
    gridLoading: false,
    solverLoading: false,
    error: null as string | null,
    initialized: false
  }),

  getters: {
    isGridLoaded: (state) => state.gridState !== null,
    hasConflicts: (state) => state.gridState?.conflicts?.length > 0,
    isSolved: (state) => state.gridState?.is_complete === true,
    isValid: (state) => state.gridState?.is_valid === true,
    hasSolution: (state) => state.solutionInfo !== null && state.solutionInfo.total_steps > 0
  },

  actions: {
    async loadGrid() {
      this.gridLoading = true
      this.error = null
      try {
        const response = await axios.get(`${API_BASE}/grid`)
        this.gridState = response.data
      } catch (error) {
        this.error = 'Failed to load grid'
        console.error('Error loading grid:', error)
      } finally {
        this.gridLoading = false
      }
    },

    async updateCell(row: number, col: number, value: number) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`${API_BASE}/grid/cell`, {
          row,
          col,
          value
        })
        
        if (response.data.success && response.data.grid_state) {
          this.gridState = response.data.grid_state
        }
        return response.data.success
      } catch (error) {
        this.error = 'Failed to update cell'
        console.error('Error updating cell:', error)
        return false
      } finally {
        this.loading = false
      }
    },

    async loadSamplePuzzle() {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(`${API_BASE}/grid/sample`)
        
        if (response.data.success && response.data.grid_state) {
          this.gridState = response.data.grid_state
          this.solutionInfo = null
          this.performanceMetrics = null
        }
        return response.data.success
      } catch (error) {
        this.error = 'Failed to load sample puzzle'
        console.error('Error loading sample puzzle:', error)
        return false
      } finally {
        this.loading = false
      }
    },

    async clearGrid(keepGiven: boolean = false) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`${API_BASE}/grid/clear`, {
          keep_given: keepGiven
        })
        
        if (response.data.success && response.data.grid_state) {
          this.gridState = response.data.grid_state
          this.solutionInfo = null
          this.performanceMetrics = null
        }
        return response.data.success
      } catch (error) {
        this.error = 'Failed to clear grid'
        console.error('Error clearing grid:', error)
        return false
      } finally {
        this.loading = false
      }
    },

    async loadSolvers() {
      this.solverLoading = true
      this.error = null
      try {
        const response = await axios.get(`${API_BASE}/solvers`)
        this.solvers = response.data
      } catch (error) {
        this.error = 'Failed to load solvers'
        console.error('Error loading solvers:', error)
      } finally {
        this.solverLoading = false
      }
    },

    async solvePuzzle(solverName: string, showSteps: boolean = true) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`${API_BASE}/solve`, {
          solver_name: solverName,
          show_steps: showSteps
        })
        
        const solveResponse: SolveResponse = response.data
        
        if (solveResponse.success) {
          this.gridState = solveResponse.grid_state
          this.solutionInfo = solveResponse.solution_info || null
          this.performanceMetrics = solveResponse.performance_metrics || null
        }
        
        return solveResponse
      } catch (error) {
        this.error = 'Failed to solve puzzle'
        console.error('Error solving puzzle:', error)
        return null
      } finally {
        this.loading = false
      }
    },

    async loadSolutionInfo() {
      try {
        const response = await axios.get(`${API_BASE}/solution`)
        this.solutionInfo = response.data
      } catch (error) {
        console.error('Error loading solution info:', error)
      }
    },

    async nextStep() {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`${API_BASE}/solution/next`)
        
        if (response.data.success) {
          this.gridState = response.data.grid_state
          this.solutionInfo = response.data.solution_info
        }
        
        return response.data.success
      } catch (error) {
        this.error = 'Failed to go to next step'
        console.error('Error going to next step:', error)
        return false
      } finally {
        this.loading = false
      }
    },

    async prevStep() {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`${API_BASE}/solution/prev`)
        
        if (response.data.success) {
          this.gridState = response.data.grid_state
          this.solutionInfo = response.data.solution_info
        }
        
        return response.data.success
      } catch (error) {
        this.error = 'Failed to go to previous step'
        console.error('Error going to previous step:', error)
        return false
      } finally {
        this.loading = false
      }
    },

    async jumpToStep(stepIndex: number) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`${API_BASE}/solution/jump`, {
          step_index: stepIndex
        })
        
        if (response.data.success) {
          this.gridState = response.data.grid_state
          this.solutionInfo = response.data.solution_info
        }
        
        return response.data.success
      } catch (error) {
        this.error = 'Failed to jump to step'
        console.error('Error jumping to step:', error)
        return false
      } finally {
        this.loading = false
      }
    },

    async loadPuzzleFromFile(file: File) {
      this.loading = true
      this.error = null
      try {
        const formData = new FormData()
        formData.append('file', file)
        
        const response = await axios.post(`${API_BASE}/grid/load`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        if (response.data.success && response.data.grid_state) {
          this.gridState = response.data.grid_state
          this.solutionInfo = null
          this.performanceMetrics = null
        }
        
        return response.data.success
      } catch (error) {
        this.error = 'Failed to load puzzle from file'
        console.error('Error loading puzzle from file:', error)
        return false
      } finally {
        this.loading = false
      }
    },

    async savePuzzle() {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(`${API_BASE}/grid/save`, {
          responseType: 'blob'
        })
        
        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        
        // Extract filename from response headers or use default
        const contentDisposition = response.headers['content-disposition']
        let filename = 'sudoku_puzzle.json'
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename=(.+)/)
          if (filenameMatch) {
            filename = filenameMatch[1].replace(/['"]/g, '')
          }
        }
        
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        return true
      } catch (error) {
        this.error = 'Failed to save puzzle'
        console.error('Error saving puzzle:', error)
        return false
      } finally {
        this.loading = false
      }
    },

    clearError() {
      this.error = null
    },



  }
})