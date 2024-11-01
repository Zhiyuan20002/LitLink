<script setup lang="ts">
import {onMounted, ref} from 'vue';
import {message} from 'ant-design-vue';
import {
  SmileOutlined,
  EditOutlined,
  ReloadOutlined,
  BookOutlined,
  PaperClipOutlined,
  StarOutlined,
  ScheduleOutlined,
  DeleteTwoTone,
} from '@ant-design/icons-vue';
import type {SelectProps} from 'ant-design-vue';

const summary = ref('This is a summary of the paper');

const historyHighlights = ref([]);

const textHighlights = ref([]);

const activeKey = ref(['0']);

const options = ref<SelectProps['options']>([
  {
    value: 'TO_READ',
    label: 'TO_READ',
    color: 'blue',
  },
  {
    value: 'READING',
    label: 'READING',
    color: 'green',
  },
  {
    value: 'UNDERSTAND',
    label: 'UNDERSTAND',
    color: 'orange',
  },
  {
    value: 'REVIEW',
    label: 'REVIEW',
    color: 'yellow',
  },
  {
    value: 'KEY_POINT',
    label: 'KEY_POINT',
    color: 'gold',
  },
  {
    value: 'APPLY',
    label: 'APPLY',
    color: 'purple',
  },
  {
    value: 'TO_DISCUSS',
    label: 'TO_DISCUSS',
    color: 'red',
  },
]);

const props = defineProps({
  chosenPaper: {
    type: Object,
    required: true,
  },
});

// 初始化加载FlashCards和Summary
onMounted(async () => {

  try {
    const paperId = props.chosenPaper.key;  // 从 props 中获取 paperId
    if (!paperId) {
      message.error("Invalid paper ID");
      return;
    }

    const response = await fetch(`http://localhost:8000/main/get_summary_and_flashcards/${paperId}/`);
    if (response.ok) {
      const data = await response.json();

      // 设置摘要内容
      summary.value = data.summary || "No summary available.";  // 如果没有 summary，提供默认文本

      // 设置文本高亮学习卡片
      textHighlights.value = (data.flashcards || []).map((card) => ({
        number: card.flashcard_id,
        title: card.title,
        content: card.content,
        Status: card.status,
        highlightBy: card.highlight_by,
        Notes: card.notes,
        AIAnalysis: card.ai_analysis,
        history_related: card.related_to,
        activeKey: ['0'],
      }));

      // 如果没有历史高亮学习卡片，初始化为空列表
      historyHighlights.value = data.historyHighlights
          ? data.historyHighlights.map((historyItem) => ({
            number: historyItem.number,
            title: historyItem.title,
            content: historyItem.content,
            Status: historyItem.status,
            highlightBy: historyItem.highlight_by,
            Notes: historyItem.notes,
            AIAnalysis: historyItem.ai_analysis,
            relatedTo: historyItem.related_to,
            pdfNo: historyItem.pdfUrl,
          }))
          : [];

      message.success("Summary and flashcards loaded successfully.");
    } else {
      message.error("Failed to load summary and flashcards.");
    }
  } catch (error) {
    message.error("Error loading summary and flashcards.");
    console.error(error);
  }
});

// Function to save summary to backend
const handleSaveSummary = async () => {
  try {
    const response = await fetch(`http://localhost:8000/main/update_summary/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        paper_id: props.chosenPaper.key,
        summary: summary.value,
      }),
    });
    if (response.ok) {
      message.success('Summary updated successfully.');
    } else {
      message.error('Failed to update summary.');
    }
  } catch (error) {
    message.error('Error updating summary.');
    console.error(error);
  }
};

const isGenerating = ref(false);

// 生成新的学习卡片
const generateFlashcards = async () => {
  isGenerating.value = true;
  try {
    const response = await fetch(`http://localhost:8000/main/generate_flashcards/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        paper_id: props.chosenPaper.key,
      }),
    });

    if (response.ok) {
      const data = await response.json();

      console.log(data.flashcards);

      // 更新 textHighlights 数据
      textHighlights.value = (data.flashcards || []).map((card) => ({
        number: card.flashcard_id,
        title: card.title,
        content: card.content,
        Status: card.status,
        highlightBy: card.highlight_by,
        Notes: card.notes,
        AIAnalysis: card.ai_analysis,
        history_related: card.related_to,  // 使用 related_to 列表
        activeKey: ['0'],
      }));

      console.log(textHighlights);

      console.log(data.historyHighlights);

      // 更新 historyHighlights 数据
      historyHighlights.value = (data.historyHighlights || []).map((historyItem) => ({
        number: historyItem.number,
        title: historyItem.title,
        content: historyItem.content,
        Status: historyItem.Status,
        highlightBy: historyItem.highlightBy,
        Notes: historyItem.Notes,
        AIAnalysis: historyItem.AIAnalysis,
        relatedTo: historyItem.relatedTo,
        pdfNo: historyItem.pdfUrl,
      }));

      console.log(historyHighlights);

      message.success('Flashcards generated successfully.');
    } else {
      message.error('Failed to generate flashcards.');
    }
  } catch (error) {
    message.error('Error generating flashcards.');
    console.error(error);
  } finally {
    isGenerating.value = false;
  }
};

// 删除学习卡片
const deleteFlashcard = async (flashcardId) => {
  try {
    const response = await fetch(`http://localhost:8000/main/delete_flashcard/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        flashcard_id: flashcardId,
      }),
    });

    if (response.ok) {
      textHighlights.value = textHighlights.value.filter((item) => item.number !== flashcardId);
      message.success('Flashcard deleted successfully.');
    } else {
      message.error('Failed to delete flashcard.');
    }
  } catch (error) {
    message.error('Error deleting flashcard.');
    console.error(error);
  }
};

// 更新学习卡片状态
const updateFlashcard = async (flashcardId, status, note, ai_analysis) => {
  try {
    const response = await fetch(`http://localhost:8000/main/update_flashcard/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        flashcard_id: flashcardId,
        status: status,
        notes: note,
        ai_analysis: ai_analysis,
      }),
    });

    if (response.ok) {
      message.success('Flashcard updated successfully.');
    } else {
      message.error('Failed to update flashcard.');
    }
  } catch (error) {
    message.error('Error updating flashcard.');
    console.error(error);
  }
};

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
          :rows="6"
          @blur="handleSaveSummary"/>
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
              :showCancel="false"
              width="200">
            <template #title>
              <a-select
                  v-model:value="item.Status"
                  :options="options"
                  @change="updateFlashcard(item.number, item.Status, item.Notes, item.AIAnalysis)"
                  style="width: 120px">
                <template #suffixIcon>
                  <SmileOutlined class="ant-select-suffix"/>
                </template>
              </a-select>
            </template>
            <a-tag
                :color="options.find(option => option.value === item.Status)?.color"
                style="width: 120px; text-align: center">
              {{ item.Status }}
            </a-tag>
          </a-popconfirm>
          <a-popconfirm title="Sure to delete?" @confirm="deleteFlashcard(item.number)">
            <a-button type="text" size="small">
              <DeleteTwoTone two-tone-color="#eb2f96"/>
            </a-button>
          </a-popconfirm>
        </template>

        <h4>
          {{ item.content }}
        </h4>

        <div style="margin-top: 16px">
          <h4 style="margin: 8px 0 8px 2px">
            <SmileOutlined/>
            AI Note By LitLink
          </h4>
          <a-textarea
              v-model:value="item.AIAnalysis"
              show-count
              size="small"
              :rows="3"/>
        </div>

        <div style="margin-top: 16px">
          <h4 style="margin: 8px 0 8px 2px">
            <EditOutlined/>
            My Note
          </h4>
          <a-textarea
              v-model:value="item.Notes"
              show-count
              size="small"
              @blur="updateFlashcard(item.number, item.Status, item.Notes, item.AIAnalysis)"
              :rows="2"/>
        </div>

        <h4 style="margin: 16px 0 8px 2px">
          <ScheduleOutlined/>
          History Related Learning Flashcards
        </h4>

        <span v-if="!(item.history_related && item.history_related.length > 0)">
          There are no history related study cards for this card.
        </span>

        <a-collapse
            v-model:activeKey="item.activeKey"
            :bordered="false"
            collapsible="icon">
          <a-collapse-panel
              v-for="historyItem in historyHighlights.filter(h => item.history_related.includes(h.number))"
              :key="historyItem.number"
              :header="historyItem.title"
              class="history-panel">
            <template #extra>
              <a-popconfirm
                  width="200">
                <template #title>
                  <a-select
                      v-model:value="historyItem.Status"
                      :options="options"
                      style="width: 120px">
                    <template #suffixIcon>
                      <SmileOutlined class="ant-select-suffix"/>
                    </template>
                  </a-select>
                </template>
                <a-tag
                    :color="options.find(option => option.value === historyItem.Status)?.color"
                    style="width: 120px; text-align: center">
                  {{ historyItem.Status }}
                </a-tag>
              </a-popconfirm>
            </template>

            <h4>
              {{ historyItem.content }}
            </h4>

            <div style="margin: 8px 0 8px 2px; display: flex; justify-content: space-between; align-items: center;">
              <div>
                <PaperClipOutlined/>
                <!--                {{ historyItem.relatedTo }}-->
              </div>
              <a-button type="text" style="color: #5A54F9">
                <BookOutlined/>
                Open This Paper
              </a-button>
            </div>

            <div style="margin-top: 16px">
              <h4 style="margin: 8px 0 8px 2px">
                <SmileOutlined/>
                AI Note By LitLink
              </h4>
              <a-textarea
                  v-model:value="historyItem.AIAnalysis"
                  show-count
                  size="small"
                  :rows="3"/>
            </div>

            <div style="margin-top: 16px; margin-bottom: 16px">
              <h4 style="margin: 8px 0 8px 2px">
                <EditOutlined/>
                My Note
              </h4>
              <a-textarea
                  v-model:value="historyItem.Notes"
                  show-count
                  size="small"
                  :rows="2"/>
            </div>

          </a-collapse-panel>
        </a-collapse>

      </a-collapse-panel>
    </a-collapse>

    <a-button
        type="primary"
        style="margin: 10px 0 20px 0; width: 100%;"
        @click="generateFlashcards"
        :disabled="isGenerating"
        :loading="isGenerating"
    >
      <template #icon>
        <EditOutlined/>
      </template>
      Generate new Flashcards by LitLink AI
    </a-button>
    <a-skeleton active v-if="isGenerating"/>

  </div>
</template>

<style scoped>

.custom-panel {
  background: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 8px;
  border: 0;
  overflow: hidden;
}

.history-panel {
  background: linear-gradient(135deg, rgba(245, 245, 245, 0.3), rgba(90, 84, 249, 0.3));
  border-radius: 8px;
  margin-bottom: 8px;
  border: 1px solid #5A54F9;
  overflow: hidden;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.custom-panel:last-of-type {
  border-radius: 8px;
}

.history-panel:last-of-type {
  border-radius: 8px;
  border: 1px solid #5A54F9;
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
