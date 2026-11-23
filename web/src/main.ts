import { createApp } from 'vue'
import './style.css'
import './styles/product-shell.css'
import './styles/journey.css'
import './styles/design-tokens.css'
import './styles/ui.css'
import App from './App.vue'
import { createProductRouter } from './router'

const router = createProductRouter()
const app = createApp(App)
app.use(router)
void router.isReady().then(() => app.mount('#app'))
