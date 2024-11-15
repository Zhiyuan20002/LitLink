import { createApp } from 'vue';
import App from './App.vue';
import { createPinia } from 'pinia';

// 引入Ant Design Vue
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/reset.css';

const pinia = createPinia();
const app = createApp(App);

// 使用 Ant Design Vue
app.use(Antd);
app.use(pinia);
app.mount('#app');