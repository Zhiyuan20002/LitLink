<script setup lang="ts">
import {ref} from 'vue';
import PdfC from "./PdfC.vue";
import FlashCards from "./FlashCards.vue";
import GroupChat from "./GroupChat.vue";
import {UserOutlined, LeftOutlined, ScheduleOutlined, CommentOutlined} from '@ant-design/icons-vue';
import jsPdf from "./example.pdf";
import logo from "../assets/litlink_logo.png";

const activeKey = ref("1");

</script>

<template>
  <a-layout class="page_content">
    <a-layout-header class="header-container">
      <a-image
          :src=logo
          :width=220
          :preview=false
          style="margin-top: 10px"
      />
      <a-avatar
          :style="{ backgroundColor: '#87d068' , marginTop: '10px'}"
      >
        <template #icon>
          <UserOutlined/>
        </template>
      </a-avatar>
    </a-layout-header>

    <!-- Content部分 -->
    <a-layout-content class="content">
      <a-row>
        <a-col :span="12">
          <div class="pdf_content">
            <div class="pdf_title">
              <a-tooltip>
                <template #title>Back to Home</template>
                <a-button
                    type="text"
                    style="width: 35px; padding: 0"
                    @click="backToHome"
                >
                  <LeftOutlined/>
                </a-button>
              </a-tooltip>
              <a-tooltip>
                <template #title>Paper's Title</template>
                Paper's Title
              </a-tooltip>
            </div>
            <div class="pdf_file">
              <!-- pdf组件 -->
              <PdfC :pdfUrl="jsPdf"/>
            </div>
          </div>
        </a-col>
        <a-col :span="12">
          <!-- FlashCards 和 Group Chat 标签页 -->
          <div class="user_content">
            <a-tabs
                v-model:activeKey="activeKey"
                style="border-radius: 8px">
              <a-tab-pane key="1">
                <template #tab>
                  <ScheduleOutlined/>
                  Flashcards
                </template>
                <div class="tab_content">
                  <FlashCards/>
                </div>
              </a-tab-pane>
              <a-tab-pane key="2">
                <template #tab>
                  <CommentOutlined/>
                  Group Chat
                </template>
                <div class="tab_content">
                  <GroupChat/>
                </div>
              </a-tab-pane>
            </a-tabs>
          </div>
        </a-col>
      </a-row>
    </a-layout-content>
  </a-layout>
</template>

<style scoped>
.page_content {
  height: 100vh;
  background-image: url('../assets/bg_light.png');
  background-size: cover; /* 调整图片大小，cover 将图片按比例缩放填充整个区域 */
  background-position: center; /* 图片居中显示 */
  background-repeat: no-repeat; /* 图片不重复 */
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 6vh;
  background: rgba(255, 255, 255, 0);
}

.content {
  padding: 10px;
  background: rgba(255, 255, 255, 0);
  height: 94vh;
}

.pdf_content {
  position: relative;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 5px;
  border-radius: 12px;
  height: 92vh;
  margin-right: 10px;
}

.pdf_title {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 5px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  height: 40px;
  width: 240px;
}

.pdf_title span,
.pdf_title LeftOutlined {
  font-size: 15px;
  margin: 5px;
}

.pdf_file {
  height: 100%;
  border-radius: 8px;
}

.user_content {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  padding: 0 15px 10px 15px;
  border-radius: 12px;
  height: 92vh;
  font-weight: bold;
}

.tab_content {
  height: 83vh;
  overflow: auto;
  border-radius: 12px;
  font-weight: normal;
}

</style>
