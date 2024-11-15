<script setup lang="ts">
import {nextTick, onMounted, PropType, ref, watch} from 'vue';
import {DeleteTwoTone, SendOutlined, LoadingOutlined} from '@ant-design/icons-vue';
import {marked} from "marked";
import zhipuaiLogo from '../assets/zhipuai.svg';
import openaiLogo from '../assets/openai.svg';
import litlinkLogo from '../assets/litlink_ai_logo.png';
import claudeLogo from '../assets/claude.svg';
import web_search_Logo from '../assets/web_search.png';
import ProgrammerLogo from '../assets/programmer.png';
import doubaoLogo from '../assets/doubao.png';
import qwenLogo from '../assets/qwen.svg';
import ollamaLogo from '../assets/ollama.svg';
import gemmaLogo from '../assets/google-gemini-icon.svg';
import mistralLogo from '../assets/Mistral.svg';

const messages = ref([]);

const props = defineProps({
  avatarUrl: {
    type: String as PropType<string>,
    required: true,
  },
  chosenPaper: {
    type: Object,
    required: true,
  },
});

const avatar_info = ref([
  {
    name: 'user',
    avatar: props.avatarUrl,
  },
  {
    name: 'ChatGLM',
    avatar: zhipuaiLogo,
  },
  {
    name: 'Author',
    avatar: zhipuaiLogo,
  },
  {
    name: 'ChatGPT',
    avatar: openaiLogo,
  },
  {
    name: 'LitLink AI',
    avatar: litlinkLogo,
  },
  {
    name: 'Claude',
    avatar: claudeLogo,
  },
  {
    name: 'Web Search',
    avatar: web_search_Logo,
  },
  {
    name: 'Programmer',
    avatar: ProgrammerLogo,
  },
  {
    name: 'Doubao',
    avatar: doubaoLogo,
  },
  {
    name: 'Qwen',
    avatar: qwenLogo,
  },
  {
    name: 'Llama(local)',
    avatar: ollamaLogo,
  },
  {
    name: 'Gemma(local)',
    avatar: gemmaLogo,
  },
  {
    name: 'Mistral(local)',
    avatar: mistralLogo,
  }
]);

const agents = ref([
  {
    name: 'LitLink AI',
    details: 'Based on the glm-4-air model, the LitLink team fine-tuned it using a large amount of paper data, and connected it to the database of Flashcards associated with your paper.',
  },
  {
    name: 'Author',
    details: 'Based on the glm-4-long model, adept at processing long text inputs, utilizing prompt engineering to simulate a conversation between the author of this text and the user, the entire text content of the paper has been inputted to the model in the background.',
  },
  {
    name: 'Web Search',
    details: 'Based on the glm-4-long model, enhanced retrieval techniques were used to configure web search capabilities for the model, allowing it to autonomously access internet content and provide references citations when answering.',
  },
  {
    name: 'Programmer',
    details: 'Based on the codegeex-4 model, a model designed for programming that specializes in writing code or dealing with code-related problems.',
  },
  {
    name: 'ChatGPT',
    details: 'Using the gpt-4o-mini model, developed by OpenAI, with a few prompts built-in to help answer questions.',
  },
  {
    name: 'Llama(local)',
    details: 'Using the latest open source community llama3.1-8B model by Meta. The model will run entirely locally, suitable for question answering in a secure and confidential environment. There are a few prompts built-in to help answer questions.',
  },
  {
    name: 'Doubao',
    details: 'Using the doubao-lite model, developed by ByteDance, with a few prompts built-in to help answer questions.',
  },
  {
    name: 'Qwen',
    details: 'Using the qwen-turbo model, developed by Alibaba, with a few prompts built-in to help answer questions.',
  },
  {
    name: 'Gemma(local)',
    details: 'Using the latest open source community gemma2-9B model by Google. The model will run entirely locally, suitable for question answering in a secure and confidential environment. There are a few prompts built-in to help answer questions.',
  },
  {
    name: 'Mistral(local)',
    details: 'Using the latest open source community Mistral-nemo model by Mistral & NVIDIA. The model will run entirely locally, suitable for question answering in a secure and confidential environment. There are a few prompts built-in to help answer questions.',
  }
]);

const newMessage = ref('');

const usingAgent = ref('Author');

const isGenerating = ref(false);

// 设置当前智能体
function setAgent(agentName: string) {
  usingAgent.value = agentName;
}

// 发送消息到后端
async function sendMessage() {
  const paperId = props.chosenPaper.key;
  const messageText = newMessage.value;
  const agentName = usingAgent.value;
  const diving = false;

  // 在消息记录中添加新消息
  messages.value.push({role: 'user', content: messageText});
  newMessage.value = ''; // 清空输入框
  // 滚动到底部
  await nextTick();
  const chatMessages = document.querySelector('.chat-messages');
  chatMessages?.scrollTo(0, chatMessages.scrollHeight);

  isGenerating.value = true;

  // 构建完整消息记录并发送
  const response = await fetch(`http://localhost:8000/main/send_message/`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({document_id: paperId, messages: messageText, agent: agentName, diving: diving})
  });

  // 读取 AI 流式回复
  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let aiMessage = {role: agentName, content: ''};
  messages.value = [...messages.value, aiMessage];

  if (reader) {
    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      const text = decoder.decode(value);
      aiMessage.content += text;
      messages.value = [...messages.value];
      // 滚动到底部
      await nextTick();
      const chatMessages = document.querySelector('.chat-messages');
      chatMessages?.scrollTo(0, chatMessages.scrollHeight);
    }
  }
  isGenerating.value = false;
}

async function watchAIMessage() {
  const paperId = props.chosenPaper.key;
  const agentName = usingAgent.value;
  const diving = true;

  // 在消息记录中添加新消息
  const diveMessage = '你正在参与群聊，请根据现有的上下文内容进行回复，给出你的解答、观点或问题。如果不清楚群聊背景，可以主动提出问题或观点，以引导对话。';

  isGenerating.value = true;

  // 构建完整消息记录并发送
  const response = await fetch(`http://localhost:8000/main/send_message/`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({document_id: paperId, messages: diveMessage, agent: agentName, diving: diving})
  });

  // 读取 AI 流式回复
  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let aiMessage = {role: agentName, content: ''};
  messages.value = [...messages.value, aiMessage];

  if (reader) {
    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      const text = decoder.decode(value);
      aiMessage.content += text;
      messages.value = [...messages.value];
      // 滚动到底部
      await nextTick();
      const chatMessages = document.querySelector('.chat-messages');
      chatMessages?.scrollTo(0, chatMessages.scrollHeight);
    }
  }
  isGenerating.value = false;
}

// 初始加载该文档的消息
async function loadMessage() {
  const paperId = props.chosenPaper.key;

  try {
    const response = await fetch(`http://localhost:8000/main/load_messages/`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({document_id: paperId})
    });

    if (response.ok) {
      const data = await response.json();
      messages.value = data.messages || []; // 如果有记录，加载到消息列表
      // 使用 nextTick 等待 DOM 更新完成后滚动到底部
      await nextTick();
      const chatMessages = document.querySelector('.chat-messages');
      chatMessages?.scrollTo(0, chatMessages.scrollHeight);
    } else {
      console.error('Failed to load messages');
    }
  } catch (error) {
    console.error('Error loading messages:', error);
  }
}

onMounted(() => {
  loadMessage();  // 组件挂载时加载消息
});

watch(() => props.avatarUrl, (newAvatarUrl) => {
  currentAvatar.value = newAvatarUrl;
});

async function clear_messages() {
  try {
    const response = await fetch(`http://localhost:8000/main/clear_messages/`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({document_id: props.chosenPaper.key})
    });

    if (response.ok) {
      console.log('Messages cleared');
      messages.value = [];
      await nextTick();
    } else {
      console.error('Failed to clear messages');
    }
  } catch (error) {
    console.error('Error clearing messages:', error);
  }
}

function renderMarkdown(content: string) {
  return marked(content);
}

</script>

<template>
  <div class="chat-container">
    <!-- Chat Messages -->
    <div class="chat-messages">
      <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role === 'user' ? 'user-message' : 'ai-message']">
        <div>
          <a-avatar
              :src="avatar_info.find(agent => agent.name === message.role)?.avatar"
          />
        </div>
        <div class="message-content">
          {{ message.content.trim() }}
        </div>
      </div>
    </div>

    <!-- Message Input -->
    <div class="message-input">
      <a-input-group compact>
        <a-input
            v-model:value="newMessage"
            :placeholder='`Starting a conversation with the "${usingAgent}" agent...`'
            style="width: calc(100% - 200px)"
            @pressEnter="sendMessage"
            :disabled="isGenerating"
        />
        <a-button
            type="primary"
            style="width: 100px"
            @click="sendMessage"
            :disabled="!newMessage.trim()">
          <SendOutlined/>
          Send
        </a-button>
        <a-tooltip title="Dive in and watch the AI bots chat 🤿!">
          <a-button style="width: 50px" :disabled="isGenerating || messages.length === 0" @click="watchAIMessage">
            🤿
          </a-button>
        </a-tooltip>
        <a-popconfirm title="Sure you want to clear the chat log?" @confirm="clear_messages">
          <a-button style="width: 50px" :disabled="isGenerating || messages.length === 0">
            <LoadingOutlined v-if="isGenerating"/>
            <DeleteTwoTone v-else two-tone-color="#eb2f96"/>
          </a-button>
        </a-popconfirm>
      </a-input-group>
      <div style="margin-left: 5px">
        Click to chat with different AI agents:
      </div>
      <div style="display: flex; align-items: center; gap: 10px; overflow-x: auto;">
        <div
            v-for="(agent, index) in agents"
            :key="index"
            style="height: 50px; display: flex; align-items: center;">
          <a-tooltip :title="agent.details">
            <a-button
                type="text"
                @click="setAgent(agent.name)"
                :class="{'active-agent': usingAgent === agent.name}"
                :disabled="isGenerating"
                style="display: flex; align-items: center; gap: 8px;">
              <a-avatar size="small" :src="avatar_info.find(avatar => avatar.name === agent.name)?.avatar" style="background-color: #ffffff"/>
              <span style="line-height: 1;">{{ agent.name }}</span>
            </a-button>
          </a-tooltip>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-messages {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border: 1px solid #ddd;
  padding: 10px;
  overflow-y: auto;
  background: #f7f7f7;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 10px;
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.user-message {
  align-self: end;
  justify-content: flex-end;
  flex-direction: row-reverse;
  max-width: 65%;
}

.ai-message {
  align-self: start;
  justify-content: flex-start;
  max-width: 75%;
}

.message-content {
  background-color: #e8e8e8;
  padding: 10px;
  border-radius: 8px;
  width: 100%;
  white-space: pre-wrap;
}

.user-message .message-content {
  background: linear-gradient(135deg, #6a11cb 60%, #2575fc 100%);
  color: white;
  text-align: left;
}

.message-input {
  height: 110px;
  background-color: #f0f0f0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 5px;
  width: 100%;
}

.active-agent {
  border: 2px solid #5A54F9; /* 高亮边框 */
  border-radius: 8px;
}

</style>
