import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'

// PrimeVue Components
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dropdown from 'primevue/dropdown'
import FileUpload from 'primevue/fileupload'
import Card from 'primevue/card'
import Divider from 'primevue/divider'
import ProgressBar from 'primevue/progressbar'
import Message from 'primevue/message'
import Sidebar from 'primevue/sidebar'
import Panel from 'primevue/panel'

// PrimeIcons
import 'primeicons/primeicons.css'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(PrimeVue, {
  ripple: true
})

// Register PrimeVue components globally
app.component('Button', Button)
app.component('InputNumber', InputNumber)
app.component('DataTable', DataTable)
app.component('Column', Column)
app.component('Dropdown', Dropdown)
app.component('FileUpload', FileUpload)
app.component('Card', Card)
app.component('Divider', Divider)
app.component('ProgressBar', ProgressBar)
app.component('Message', Message)
app.component('Sidebar', Sidebar)
app.component('Panel', Panel)

app.mount('#app')
