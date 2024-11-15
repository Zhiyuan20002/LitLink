import {defineStore} from 'pinia';
import {ref} from 'vue';

export const useHighlightStore = defineStore('highlightStore', () => {
    // 存储高亮文本列表，仅保存文本内容
    const highlights = ref<string[]>([]);
    const aiHighlights = ref<string[]>([]);
    const aiHighlights_flag = ref<boolean>(false);

    // 添加新的高亮文本
    function addHighlight(newHighlight: string) {
        highlights.value.push(newHighlight);
    }

    function addAIHighlight(newHighlight: string) {
        aiHighlights.value.push(newHighlight);
    }

    function setAIHighlightsFlag(flag: boolean) {
        aiHighlights_flag.value = flag;
    }

    // 从高亮列表中删除高亮
    function removeHighlight(index: number) {
        highlights.value.splice(index, 1);
    }

    function removeAIHighlight(index: number) {
        aiHighlights.value.splice(index, 1);
    }

    // 清除所有高亮数据（例如重新加载时）
    function clearHighlights() {
        highlights.value = [];
    }

    function clearAIHighlights() {
        aiHighlights.value = [];
    }

    return {
        highlights,
        addHighlight,
        removeHighlight,
        clearHighlights,
        aiHighlights,
        addAIHighlight,
        removeAIHighlight,
        clearAIHighlights,
        aiHighlights_flag,
        setAIHighlightsFlag,
    };
});