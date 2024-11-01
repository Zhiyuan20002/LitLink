<script setup lang="ts">
import {PropType, ref} from 'vue';
import {SendOutlined} from '@ant-design/icons-vue';
import zhipuaiLogo from '../assets/zhipuai.svg';
import openaiLogo from '../assets/openai.svg';
import litlinkLogo from '../assets/litlink_ai_logo.png';
import claudeLogo from '../assets/claude.svg';

const messages = ref([
  {
    from: 'ChatGPT',
    text: 'The paper uses softmax to convert scores into a probability distribution, highlighting the most significant elements.'
  },
  {
    from: 'user',
    text: 'What do you think, Tim?'
  },
  {
    from: 'ChatGLM',
    text: 'The softmax function is used to emphasize high-scoring elements, and selecting top-k elements helps in concentrating on the most relevant features.'
  }
]);

const props = defineProps({
  avatarUrl: {
    type: String as PropType<string>,
    required: true,
  }
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
  }
]);

const agents = ref([
  {
    name: 'LitLink AI',
    details: 'By Ourselves',
  },
  {
    name: 'ChatGLM',
    details: 'By Zhipuai',
  },
  {
    name: 'ChatGPT',
    details: 'By OpenAI',
  },
  {
    name: 'Claude',
    details: 'By Claude',
  },
]);

const newMessage = ref('');

// 添加 AI 助手名称到输入框内容
function addAgentToMessage(agentName: string) {
  newMessage.value += ` @${agentName} `;
}

</script>

<template>
  <div>
    <!-- Chat Messages -->
    <div class="chat-messages">
      <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.from === 'user' ? 'user-message' : 'ai-message']">
        <a-avatar :src="avatar_info.find(agent => agent.name === message.from)?.avatar" shape="circle"/>
        <div class="message-content">
          {{ message.text }}
        </div>
      </div>
    </div>

    <!-- Message Input -->
    <div class="message-input">
      <a-input-group compact>
        <a-input v-model:value="newMessage" placeholder="Starting a conversation with the author of the paper..."
                 style="width: calc(100% - 120px)"/>
        <a-button type="primary" style="width: 120px">
          <SendOutlined/>
          Send
        </a-button>
      </a-input-group>
      <div style="margin-left: 5px">
        Intelligent agents that can be used, click to use them:
      </div>
      <div style="display: flex; align-items: center; gap: 10px; overflow-x: auto;">
        <div
            v-for="(agent, index) in agents"
            :key="index"
            style="height: 50px; display: flex; align-items: center;">
          <a-button
              type="text"
              @click="addAgentToMessage(agent.name)"
              style="display: flex; align-items: center; gap: 8px;">
            <a-avatar size="small" :src="avatar_info.find(avatar => avatar.name === agent.name)?.avatar"/>
            <span style="line-height: 1;">{{ agent.name }}</span>
          </a-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 10px;
  border: 1px solid #ddd;
  padding: 10px;
  height: 68vh;
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
  max-width: 60%;
}

.ai-message {
  align-self: start;
  justify-content: flex-start;
  max-width: 60%;
}

.message-content {
  background-color: #f0f0f0;
  padding: 10px;
  border-radius: 8px;
  width: 100%;
}

.user-message .message-content {
  background-color: #5A54F9;
  color: white;
  text-align: right;
}

.message-input {
  height: 13vh;
  background-color: #f0f0f0;
  border-radius: 8px;
  padding: 5px;
  width: 100%;
}

</style>
