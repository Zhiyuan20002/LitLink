<script setup lang="ts">
import {ref} from 'vue';
import {
  SmileOutlined,
  EditOutlined,
  ReloadOutlined,
  BookOutlined,
  PaperClipOutlined,
  StarOutlined,
  ScheduleOutlined,
} from '@ant-design/icons-vue';
import type {SelectProps} from 'ant-design-vue';

const summary = ref('This is a summary of the paper');

const historyHighlights = ref([
  {
    number: 1,
    title: 'History FlashCard 1',
    content: 'content 1',
    Status: 'NEW',
    highlightBy: 'You',
    Notes: 'This is a note',
    AIAnalysis: 'This is AI analysis',
    relatedTo: 'Paper 1',
    pdfNo: '1111111111',
  },
  {
    number: 2,
    title: 'History FlashCard 2',
    content: 'content 1',
    Status: 'NEW',
    highlightBy: 'You',
    Notes: 'This is a note',
    AIAnalysis: 'This is AI analysis',
    relatedTo: 'Paper 2',
    pdfNo: '1111111111',
  },
  {
    number: 3,
    title: 'History FlashCard 3',
    content: 'content 1',
    Status: 'NEW',
    highlightBy: 'You',
    Notes: 'This is a note',
    AIAnalysis: 'This is AI analysis',
    relatedTo: 'Paper 3',
    pdfNo: '1111111111',
  },
  {
    number: 4,
    title: 'History FlashCard 4',
    content: 'content 1',
    Status: 'NEW',
    highlightBy: 'You',
    Notes: 'This is a note',
    AIAnalysis: 'This is AI analysis',
    relatedTo: 'Paper 4',
    pdfNo: '1111111111',
  },

]);

const textHighlights = ref([
  {
    number: 1,
    title: 'Highlight Text Learning FlashCard 1',
    content: 'content 1',
    Status: 'NEW',
    highlightBy: 'You',
    Notes: 'This is a note',
    AIAnalysis: 'This is AI analysis',
  },
  {
    number: 2,
    title: 'Highlight Text Learning FlashCard 2',
    content: 'content 2',
    Status: 'READING',
    highlightBy: 'You',
    Notes: 'This is a note',
    AIAnalysis: 'This is AI analysis',
  },
  {
    number: 3,
    title: 'Highlight Text Learning FlashCard 4',
    content: 'content 4',
    Status: 'EXAM',
    highlightBy: 'You',
    Notes: 'This is a note',
    AIAnalysis: 'This is AI analysis',
  },
  {
    number: 4,
    title: 'Highlight Text Learning FlashCard 4',
    content: 'content 4',
    Status: 'CODE',
    highlightBy: 'You',
    Notes: 'This is a note',
    AIAnalysis: 'This is AI analysis',
  },
]);

const activeKey = ref(['0']);

const activeKey_history = ref(['0']);

const options = ref<SelectProps['options']>([
  {
    value: 'EXAM',
    label: 'EXAM',
    color: 'red',
  },
  {
    value: 'READING',
    label: 'READING',
    color: 'green',
  },
  {
    value: 'NEW',
    label: 'NEW',
    color: 'blue',
  },
  {
    value: 'CODE',
    label: 'CODE',
    color: 'purple',
  },
]);

</script>

<template>
  <div>
    <h3>
      <StarOutlined/>
      Summary of the paper
      <a-textarea
          v-model:value="summary"
          show-count
          style="margin: 5px 0 5px 0"
          :rows="4"/>
    </h3>
    <!-- Highlight Text Section -->
    <h3 style="margin: 10px 0 5px 0">
      <ScheduleOutlined/>
      Learning FlashCards of This Paper
    </h3>
    <a-collapse
        v-model:activeKey="activeKey"
        :bordered="false"
        collapsible="icon">
      <a-collapse-panel
          v-for="(item) in textHighlights"
          :key="item.number"
          :header="item.title"
          class="custom-panel">
        <template #extra>
          <a-popconfirm
              width="200">
            <template #title>
              <a-select
                  v-model:value="item.Status"
                  :options="options"
                  style="width: 120px">
                <template #suffixIcon>
                  <SmileOutlined class="ant-select-suffix"/>
                </template>
              </a-select>
            </template>
            <a-tag
                :color="options.find(option => option.value === item.Status)?.color"
                style="width: 120px; text-align: center">
              For {{ item.Status }}
            </a-tag>
          </a-popconfirm>
        </template>

        <div>
          {{ item.content }}
        </div>

        <div style="margin-top: 16px">
          <h3 style="margin: 8px 0 8px 2px">
            <EditOutlined/>
            My Note
          </h3>
          <a-textarea
              v-model:value="item.Notes"
              show-count
              maxlength="500"
              size="small"
              :rows="2"/>
        </div>

        <div style="margin-top: 32px">
          <div style="margin: 8px 0 8px 2px; display: flex; justify-content: space-between; align-items: center;">
            <h3>
              <SmileOutlined/>
              AI Note By LitLink
            </h3>
            <div>
              <a-button>
                <ReloadOutlined/>
                Regenerate
              </a-button>
            </div>
          </div>
          <a-textarea
              v-model:value="item.AIAnalysis"
              show-count
              size="small"
              :rows="4"/>
        </div>
      </a-collapse-panel>
    </a-collapse>

    <!-- History Related Highlights -->
    <h3 style="margin: 10px 0 5px 0">
      <ScheduleOutlined/>
      History Related Learning Flashcards
    </h3>
    <a-collapse
        v-model:activeKey="activeKey_history"
        :bordered="false"
        collapsible="icon">
      <a-collapse-panel
          v-for="(item) in historyHighlights"
          :key="item.number"
          :header="item.title"
          class="custom-panel">
        <template #extra>
          <a-popconfirm
              width="200">
            <template #title>
              <a-select
                  v-model:value="item.Status"
                  :options="options"
                  style="width: 120px">
                <template #suffixIcon>
                  <SmileOutlined class="ant-select-suffix"/>
                </template>
              </a-select>
            </template>
            <a-tag
                :color="options.find(option => option.value === item.Status)?.color"
                style="width: 120px; text-align: center">
              For {{ item.Status }}
            </a-tag>
          </a-popconfirm>
        </template>

        <div>
          {{ item.content }}
        </div>

        <div style="margin: 8px 0 8px 2px; display: flex; justify-content: space-between; align-items: center;">
          <div>
            <PaperClipOutlined/>
            {{ item.relatedTo }}
          </div>
          <a-button type="link">
            <BookOutlined/>
            Open This Paper
          </a-button>
        </div>

        <div style="margin-top: 8px">
          <h3 style="margin: 8px 0 8px 2px">
            <EditOutlined/>
            My Note
          </h3>
          <a-textarea
              v-model:value="item.Notes"
              show-count
              size="small"
              :rows="4"/>
        </div>

        <div style="margin-top: 32px">
          <div style="margin: 8px 0 8px 2px; display: flex; justify-content: space-between; align-items: center;">
            <h3>
              <SmileOutlined/>
              AI Note By LitLink
            </h3>
            <div>
              <a-button>
                <ReloadOutlined/>
                Regenerate
              </a-button>
            </div>
          </div>
          <a-textarea
              v-model:value="item.AIAnalysis"
              show-count
              size="small"
              :rows="4"/>
        </div>
      </a-collapse-panel>
    </a-collapse>

  </div>
</template>

<style scoped>

.custom-panel {
  background: #f7f7f7;
  border-radius: 8px;
  margin-bottom: 8px;
  border: 0;
  overflow: hidden;
}

textarea {
  width: 100%;
  height: 60px;
  padding: 10px;
  font-size: 1em;
  border: 1px solid #ccc;
  border-radius: 4px;
}

</style>
