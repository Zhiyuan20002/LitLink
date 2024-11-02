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
import {
  HighlightOutlined,
} from '@ant-design/icons-vue';

import {reactive, onMounted, ref} from "vue";
import VuePdfEmbed from "vue-pdf-embed";
import {createLoadingTask} from "vue3-pdfjs";
// 引入 pdfjs 库和 worker 文件
import * as pdfjsLib from 'pdfjs-dist';

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

const loadingProgress = ref(0);  // 用于跟踪加载进度
const totalPages = ref(0);  // 总页数
const pdfContainer = ref<HTMLElement | null>(null);

// 初始化加载 PDF
onMounted(async () => {
  const loadingTask = createLoadingTask(state.source);
  loadingTask.onProgress = (progressData) => {
    loadingProgress.value = Math.round((progressData.loaded / progressData.total) * 100);
  };
  const pdf = await loadingTask.promise;
  state.numPages = pdf.numPages;
  totalPages.value = pdf.numPages;
  loadingProgress.value = 100;
});

// 在页面渲染时更新当前页码
function onPageRendered(page) {
  updatePageNum(page);
}

// 滚动事件中更新当前页码
function handleScroll() {
  if (pdfContainer.value) {
    const pageHeight = pdfContainer.value.scrollHeight / state.numPages;
    const newPageNum = Math.ceil((pdfContainer.value.scrollTop - 300) / pageHeight) + 1;
    if (newPageNum !== state.pageNum) {
      updatePageNum(newPageNum);
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

  const range = selection.getRangeAt(0);
  const spans = Array.from(textLayer.querySelectorAll("span"));

  let highlighting = false;
  let combinedText = ""; // 存储组合的高亮文本
  const highlightedTexts: { pageNum: number; text: string }[] = []; // 存储高亮文本信息

  // 创建转义特殊符号的函数
  const escapeHTML = (text: string) => {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
  };

  // 构建一个批量更新的高亮 HTML 映射，键为 span，值为修改后的内容
  const spanHTMLMap = new Map<HTMLElement, string>();

  for (const span of spans) {
    if (!range.intersectsNode(span)) continue;

    const spanText = span.textContent || "";

    if (span === range.startContainer.parentNode) {
      const startIndex = range.startOffset;
      const highlightText = spanText.substring(startIndex);

      highlightedTexts.push({
        pageNum: state.pageNum,
        text: highlightText.trim(),
      });

      combinedText += highlightText.trim() + " ";
      spanHTMLMap.set(
          span,
          escapeHTML(spanText).replace(
              escapeHTML(highlightText),
              `<span class="highlight">${escapeHTML(highlightText)}</span>`
          )
      );

      highlighting = true;
    } else if (span === range.endContainer.parentNode) {
      const endIndex = range.endOffset;
      const highlightText = spanText.substring(0, endIndex);

      combinedText += highlightText.trim();
      highlightedTexts.push({
        pageNum: state.pageNum,
        text: highlightText.trim(),
      });

      spanHTMLMap.set(
          span,
          escapeHTML(spanText).replace(
              escapeHTML(highlightText),
              `<span class="highlight">${escapeHTML(highlightText)}</span>`
          )
      );

      highlighting = false;
      break; // 结束循环，避免多余的遍历
    } else if (highlighting) {
      combinedText += spanText.trim() + " ";
      highlightedTexts.push({
        pageNum: state.pageNum,
        text: spanText.trim(),
      });
      spanHTMLMap.set(span, `<span class="highlight">${escapeHTML(spanText)}</span>`);
    }
  }

  // 批量更新 DOM，减少对 innerHTML 的多次操作
  spanHTMLMap.forEach((html, span) => {
    span.innerHTML = html;
  });

  // 一次性更新状态，减少频繁访问
  state.combine.push(combinedText.trim());
  state.highlightedTexts.push(...highlightedTexts);
}

// 卡片前后端功能
// 新高亮内容
const newHighlight = ref('');

// 先在前端push到state的highlight中向后端发送保存高亮请求，后端保存高亮并根据高亮新建学习卡片，然后刷新flashcard界面的卡片内容


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
