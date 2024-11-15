<template>
  <div class="pdf-container" ref="pdfContainer" @scroll="handleScroll">
    <div class="pdf-wrap">
      <vue-pdf-embed
          v-for="page in totalPages"
          :source="state.source"
          class="vue-pdf-embed"
          :page="page"
          :text-layer="true"
          @page-rendered="() => onPageRendered(page)"
      />
    </div>
  </div>

  <div class="progress-bar" v-if="loadingProgress < 100">
    <a-progress :percent="loadingProgress"/>
  </div>

  <div class="page-tool">
    <a-tooltip>
      <template #title>Page Number</template>
      <div
          style="width: 35px; margin-left: 10px; margin-right: 10px; text-align: center;">
        {{ state.pageNum }}/{{ state.numPages }}
      </div>
    </a-tooltip>
    <a-tooltip v-if="!state.isHighlightMode">
      <template #title>Highlight</template>
      <a-button type="text" @click="applyHighlight" style="margin: 0 2px 0 2px">
        <HighlightOutlined/>
      </a-button>
    </a-tooltip>
  </div>
</template>

<script setup lang="ts">
import {HighlightOutlined,} from '@ant-design/icons-vue';

import {nextTick, onMounted, reactive, ref, watch} from "vue";
import VuePdfEmbed from "vue-pdf-embed";
import {createLoadingTask} from "vue3-pdfjs";
// 引入 pdfjs 库和 worker 文件
import * as pdfjsLib from 'pdfjs-dist';
import {message} from "ant-design-vue";
import {useHighlightStore} from '../store/store';
import axios from "axios";

const highlightStore = useHighlightStore();

// 设置 PDF.js 使用 Web Worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

const props = defineProps({
  chosenPaper: {
    type: Object,
    required: true,
  },
});

const state = reactive({
  source: props.chosenPaper.pdfUrl, // PDF 文件 URL
  pageNum: 1, // 当前页码
  scale: 1, // 缩放比例
  numPages: 0, // 总页数
  selectedText: "", // 选中的文本
  highlightedTexts: [] as { pageNum: number; text: string }[],
});

const highlightData = ref([]); // 用于存储高亮数据
const loadingProgress = ref(0);  // 用于跟踪加载进度
const totalPages = ref(0);  // 总页数
const pdfContainer = ref<HTMLElement | null>(null);

// 初始化加载 PDF
onMounted(async () => {

  // 向后端请求高亮数据
  try {
    // 向后端发送请求获取该文档的flashcard高亮内容
    const response = await fetch(`http://localhost:8000/main/get_flashcard_highlights/${props.chosenPaper.key}/`, {
      method: 'GET',
    });

    if (response.ok) {
      const data = await response.json();
      highlightData.value = data.flashcard_contents;
      message.success("Flashcard highlights loaded successfully.");
    } else {
      message.error("Failed to load flashcard highlights.");
    }
  } catch (error) {
    message.error("Error loading flashcard highlights.");
    console.error("Fetch error:", error);
  }

  // 创建加载任务
  await nextTick(() => {
    if (!pdfContainer.value) return;
    const loadingTask = createLoadingTask(state.source);
    loadingTask.onProgress = (progressData) => {
      loadingProgress.value = Math.round((progressData.loaded / progressData.total) * 100);
    };

    onPageRendered(state.pageNum);
    loadingTask.promise.then((pdf) => {
      state.numPages = pdf.numPages;
      totalPages.value = pdf.numPages;
      loadingProgress.value = 100;
    });
  });

});

// 在页面渲染时更新当前页码
function onPageRendered(pageNumber) {
  console.log(`Page ${pageNumber} rendered.`);
  nextTick(() => {
    setTimeout(() => {
      applyHighlight(); // 页面渲染后重新应用高亮
      applyHighlightsFromData(pageNumber);
    }, 500);
  });
}

function applyHighlightsFromData(pageNumber) {
  console.log(`Applying highlights for page ${pageNumber}`);
  const textLayers = pdfContainer.value?.querySelectorAll(".textLayer");

  if (!textLayers || textLayers.length === 0) {
    console.warn("Text layers not found");
    return;
  }
  const textLayer = textLayers[pageNumber - 1];
  if (!textLayer) {
    console.warn(`Text layer for page ${pageNumber} not found`);
    return;
  }
  const spans = Array.from(textLayer.querySelectorAll("span"));
  if (spans.length === 0) {
    console.warn(`Text layer for page ${pageNumber} not yet populated, retrying...`);
    setTimeout(() => applyHighlightsFromData(pageNumber), 100);
    return;
  }
  processSpansForHighlighting(spans);
}

function processSpansForHighlighting(spans: HTMLSpanElement[]) {
  interface SpanData {
    text: string;
    element: HTMLSpanElement;
    start: number;
    end: number;
  }

  let spansData: SpanData[] = [];
  let originalFullText = '';
  let normalizedFullText = '';
  let indexMap: number[] = []; // 映射 normalizedFullText 的索引到 originalFullText
  let originalIndex = 0;

  // *originfulltext中有些span之间需要加上空格，否则无法匹配
  for (let i = 0; i < spans.length; i++) {
    const span = spans[i];
    let spanText = span.textContent || '';
    const spanLength = spanText.length;
    const endsWithHyphen = /-$/.test(spanText);
    // 如果存在短横，设置标记并去掉短横
    if (endsWithHyphen) {
      spanText = spanText.slice(0, -1); // 去掉结尾的 "-"
    }


    spansData.push({
      text: spanText,
      element: span,
      start: originalIndex,
      end: originalIndex + spanLength,
    });

    for (let j = 0; j < spanText.length; j++) {
      const char = spanText[j];
      originalFullText += char;

      if (/\s/.test(char)) {
        // 将空白字符替换为单个空格
        normalizedFullText += ' ';
      } else {
        normalizedFullText += char;
      }

      // 记录映射关系
      indexMap.push(originalIndex);
      originalIndex++;
    }
    //console.log(`${normalizedFullText}`)
    // 检查是否需要在当前 span 和下一个 span 之间插入空格
    // 如果前一span的最后不是空白字符(空格等)，后一span的开头不是空白字符，则插入空格
    if (i < spans.length - 1) {
      const nextSpanText = spans[i + 1].textContent || '';
      //const currentEndsWithSpace = /[\s-]$/.test(spanText);
      const nextStartsWithSpace = /^\s/.test(nextSpanText);
      if (endsWithHyphen) {
        //normalizedFullText = normalizedFullText.slice(0, -1);
      } else if (!nextStartsWithSpace) {
        // 在 normalizedFullText 中插入空格
        normalizedFullText += ' ';
        // 在 indexMap 中添加映射（映射到当前 originalIndex，没有增加 originalIndex）
        indexMap.push(originalIndex - 1);
      }
    }
  }

  const lowerNormalizedFullText = normalizedFullText.toLowerCase();
  const normalizedHighlightData = highlightData.value.map((str) =>
      str.replace(/\s+/g, ' ').trim().toLowerCase()
  );

  normalizedHighlightData.forEach((highlightStr) => {
    const escapedHighlightStr = escapeRegExp(highlightStr);
    const pattern = escapedHighlightStr.replace(/ /g, '\\s+');
    const regex = new RegExp(pattern, 'giu');

    let match: RegExpExecArray | null;
    while ((match = regex.exec(lowerNormalizedFullText)) !== null) {
      const matchStartInNormalized = match.index;
      const matchEndInNormalized = regex.lastIndex;

      const matchStart = indexMap[matchStartInNormalized];
      const matchEnd = indexMap[matchEndInNormalized - 1] + 1;

      // 查找涉及的 spans
      const involvedSpans = spansData.filter((spanData) => {
        return spanData.end > matchStart && spanData.start < matchEnd;
      });

      involvedSpans.forEach((spanData) => {
        const span = spanData.element;
        const spanText = spanData.text;
        const spanStart = spanData.start;
        const spanEnd = spanData.end;

        // 计算匹配在当前 span 中的起始和结束索引
        const overlapStart = Math.max(spanStart, matchStart);
        const overlapEnd = Math.min(spanEnd, matchEnd);

        const spanMatchStart = overlapStart - spanStart;
        const spanMatchEnd = overlapEnd - spanStart;

        // 获取原始文本（保持大小写）
        const originalSpanText = spanText;

        const beforeText = escapeHTML(originalSpanText.substring(0, spanMatchStart));
        const matchText = escapeHTML(originalSpanText.substring(spanMatchStart, spanMatchEnd));
        const afterText = escapeHTML(originalSpanText.substring(spanMatchEnd));

        // 更新 innerHTML
        span.innerHTML = `${beforeText}<span class="highlight">${matchText}</span>${afterText}`;
      });
    }
  });
}

function escapeRegExp(string: string): string {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function escapeHTML(text: string): string {
  return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;')
}

// 滚动事件中更新当前页码
function handleScroll() {
  if (pdfContainer.value) {
    const pageHeight = pdfContainer.value.scrollHeight / state.numPages;
    const newPageNum = Math.ceil((pdfContainer.value.scrollTop - 300) / pageHeight) + 1;
    if (newPageNum !== state.pageNum) {
      updatePageNum(newPageNum);
      onPageRendered(state.pageNum);
    }
  }
}

// 更新当前页码函数
function updatePageNum(newPageNum) {
  if (newPageNum !== state.pageNum && newPageNum > 0 && newPageNum <= state.numPages) {
    state.pageNum = newPageNum;
  }
}

// 应用高亮
function applyHighlight() {
  const selection = window.getSelection();
  if (selection && selection.toString().trim()) {
    highlightSelectedText(selection); // 调用高亮函数
    selection.removeAllRanges(); // 清除选择内容
    state.selectedText = ""; // 重置选中文本
  }
}

function highlightSelectedText(selection: Selection) {
  const textLayer = pdfContainer.value?.querySelector(".textLayer");
  if (!textLayer) return;
  // 对文本进行正则化处理，去掉换行符与单词连接符
  let normalizedText = selection.toString().replace(/\s+/g, ' ').trim();
  // 遇到连字符+换行符的情况，将其替换""
  normalizedText = normalizedText.replace(/-\s+|\s+-/g, '');
  console.log("Selected text:", normalizedText);

  highlightData.value.push(normalizedText);

  highlightStore.addHighlight(normalizedText);
  console.log("Updated highlights in store:", highlightStore.highlights);

  onPageRendered(state.pageNum);
}

watch(
    () => highlightStore.aiHighlights_flag,
    async (aiHighlights_flag) => {
      if (aiHighlights_flag) {
        // 获取新增的高亮文本
        const newHighlightText = highlightStore.aiHighlights;
        console.log("New AI highlights:", newHighlightText);
        highlightData.value = [...highlightData.value, ...newHighlightText];
        highlightStore.clearAIHighlights();
        highlightStore.aiHighlights_flag = false;
        onPageRendered(state.pageNum);
      }
    },
    {deep: true}
);

</script>

<style scoped>

.pdf-container {
  height: 100%;
  overflow: auto;
  border-radius: 8px;
}

.pdf-wrap {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.page-tool {
  position: absolute;
  top: 12px;
  right: 12px;
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
}

.progress-bar {
  position: absolute;
  bottom: 12px;
  right: 12px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 5px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  height: 12px;
  width: 50%;
}

.highlight {
  background-color: #00FF00 !important; /* 荧光绿色 */
  color: #000;
}

</style>
