<script setup lang="ts">
import {onMounted, reactive, ref} from 'vue';
import PdfC from "./PdfC.vue";
import FlashCards from "./FlashCards.vue";
import GroupChat from "./GroupChat.vue";
import {
  LeftOutlined,
  ScheduleOutlined,
  CommentOutlined,
  InboxOutlined,
  SearchOutlined,
} from '@ant-design/icons-vue';
import logo from "../assets/litlink_logo.png";
import {message, TableColumnsType} from 'ant-design-vue';
import loading_img from "../assets/base.png";

const activeKey = ref("1");

const chosenPaper = ref({
  key: "",
  title: "",
  pdfUrl: null,
});

const backToHome = async () => {
  chosenPaper.value.pdfUrl = null;
  try {
    const response = await fetch("http://localhost:8000/main/get_papers/");
    if (response.ok) {
      const data = await response.json();
      paperData.value = data.paperData;
      message.success("Paper data loaded successfully.");
    } else {
      message.error("Failed to load paper data.");
    }
  } catch (error) {
    message.error("Error loading paper data.");
    console.error(error);
  }
};

const paperData = ref([]);

// 页面加载时从后端获取 paperData 列表
onMounted(async () => {
  try {
    const response = await fetch("http://localhost:8000/main/get_papers/");
    if (response.ok) {
      const data = await response.json();
      paperData.value = data.paperData;
      message.success("Paper data loaded successfully.");
    } else {
      message.error("Failed to load paper data.");
    }
  } catch (error) {
    message.error("Error loading paper data.");
    console.error(error);
  }
});

const state = reactive({
  searchText: '',
  searchedColumn: '',
});

const searchInput = ref();

const handleSearch = (selectedKeys, confirm, dataIndex) => {
  confirm();
  state.searchText = selectedKeys[0];
  state.searchedColumn = dataIndex;
};

const handleReset = clearFilters => {
  clearFilters({confirm: true});
  state.searchText = '';
};

const columns = ref<TableColumnsType>([
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
    width: 500,
    minWidth: 200,
    maxWidth: 600,
    ellipsis: true,
    resizable: true,
    customFilterDropdown: true,
    customFilterIcon: true,
    onFilter: (value, record) => record.name.toString().toLowerCase().includes(value.toLowerCase()),
    onFilterDropdownOpenChange: visible => {
      if (visible) {
        setTimeout(() => {
          searchInput.value.focus();
        }, 100);
      }
    },
  },
  {
    title: 'Flashcards',
    dataIndex: 'highlightCardCount',
    key: 'highlightCardCount',
    width: 120,
    minWidth: 120,
    maxWidth: 200,
    resizable: true,
  },
  {
    title: 'Created At',
    dataIndex: 'createdAt',
    key: 'createdAt',
    width: 100,
    minWidth: 100,
    maxWidth: 200,
    resizable: true,
  },
  {
    title: 'Action',
    key: 'action',
    width: 300,
    minWidth: 100,
    maxWidth: 500,
    resizable: true,
  },
]);

function handleResizeColumn(w, col) {
  col.width = w;
}

const editableData = reactive({});

const edit = (key) => {
  editableData[key] = {...paperData.value.find((item) => item.key === key)};
};

const save = async (key) => {
  const paper = editableData[key];
  if (!paper) return;

  try {
    const requestData = {
      id: key,  // 假设每篇论文有唯一的 key 或 id
      name: paper.name,
      description: paper.description,
    };

    const response = await fetch("http://localhost:8000/main/update_paper/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestData),
    });

    if (response.ok) {
      const index = paperData.value.findIndex((item) => item.key === key);
      if (index !== -1) {
        paperData.value[index] = {...editableData[key]};
      }
      delete editableData[key];
      message.success("Save successful");
    } else {
      message.error("Failed to save paper.");
    }
  } catch (error) {
    message.error("Error saving paper.");
    console.error(error);
  }
};

const cancel = (key) => {
  delete editableData[key];
  message.info("Edit canceled");
};

const openPaper = (record) => {
  // 打开操作逻辑，将chosenPaper更新为所选论文
  chosenPaper.value.key = record.key;
  chosenPaper.value.title = record.name;
  chosenPaper.value.pdfUrl = record.pdfUrl;
  console.log(chosenPaper.value.pdfUrl);
};

const deletePaper = async (record) => {
  try {
    const response = await fetch("http://localhost:8000/main/delete_paper/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({id: record.key}),
    });

    if (response.ok) {
      paperData.value = paperData.value.filter(item => item.key !== record.key);
      message.success(`Successfully deleted ${record.name}`);
    } else {
      message.error("Failed to delete paper.");
    }
  } catch (error) {
    message.error("Error deleting paper.");
    console.error(error);
  }
};

const avatarUrl = ref('https://i.seadn.io/gae/VaqD0_hMN8ri9O8CWSjJpFBLoPzoeXy5NfvL1FTz8o-QnonxS_jY1TPeL7mmn6Sqwuoxz2x0hrlHmUmtBciZ19T2BaBDiNpgTsCY?auto=format&dpr=1&w=750');

const tempAvatarUrl = ref(avatarUrl.value);

const isModalVisible = ref(false);

const newImageText = ref('');

const showModal = () => {
  isModalVisible.value = true;
};

const isGenerating = ref(false);

// 提交新的文本内容生成头像
const handleGenerateAvatar = async () => {
  if (!newImageText.value) {
    message.warning("Please enter new image text.");
    return;
  }

  isGenerating.value = true;
  tempAvatarUrl.value = loading_img;

  try {
    const response = await fetch("http://localhost:8000/main/generate_avatar/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({content: newImageText.value}),
    });

    if (response.ok) {
      const data = await response.json();
      tempAvatarUrl.value = data.avatar_url;
      newImageText.value = ''; // 重置输入框内容
      message.success("Avatar generated successfully!");
    } else {
      const errorData = await response.json();
      message.error(errorData.error || "Failed to generate avatar.");
    }
  } catch (error) {
    console.error("Error generating avatar:", error);
    message.error("An error occurred while generating the avatar.");
  } finally {
    isGenerating.value = false;
  }
};

const handleSaveAvatar = () => {
  avatarUrl.value = tempAvatarUrl.value;
  isModalVisible.value = false;
};

const isUploadModalVisible = ref(false);
const isAIProcessing = ref(false);  // 标记是否AI正在处理
const uploading = ref(false);
const canEdit = ref(false);
const uploadedFileName = ref("");
const backendFileName = ref("");
const fileList = ref([]);
const paperInfo = ref({name: "", description: "", summary: ""});

const handleFileUpload = async ({file}) => {
  if (file.status === "uploading" && !uploading.value) {
    uploading.value = true;
    uploadedFileName.value = file.name;

    // 创建 FormData 对象，用于文件上传
    const formData = new FormData();
    formData.append("pdf_file", file.originFileObj);

    try {
      const response = await fetch("http://localhost:8000/main/upload_pdf/", {
        method: "POST",
        body: formData,
      });

      const responseData = await response.json();

      if (response.ok) {
        paperInfo.value = {name: "", description: "", summary: ""};
        canEdit.value = true;
        backendFileName.value = responseData.file_name;
        isUploadModalVisible.value = true;
        message.success("File uploaded successfully!");
      } else {
        message.error("File upload failed.");
        isUploadModalVisible.value = false;
      }
    } catch (error) {
      message.error("File upload error.");
      isUploadModalVisible.value = false;
    } finally {
      uploading.value = false;  // 无论成功或失败，都重置上传状态
    }
  }
};

// 点击“智能填写”按钮调用 AI 自动填写
const handleAutoFill = async () => {
  canEdit.value = false;
  isAIProcessing.value = true;

  try {
    const response = await fetch("http://localhost:8000/main/auto_fill_stream/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({file_name: backendFileName.value}),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let currentField = null;
    let isDone = false;

    while (!isDone) {
      const {value, done} = await reader.read();
      if (done) {
        isDone = true;
        continue;
      }

      const text = decoder.decode(value);
      console.log(text);

      // 检查数据中的标记并决定填充哪个字段
      if (text.includes("{StartTitle}")) {
        currentField = "name";
        paperInfo.value.name = "";
      } else if (text.includes("{StartContent}")) {
        currentField = "description";
        paperInfo.value.description = "";
      } else if (text.includes("{StartSummary}")) {
        currentField = "summary";
        paperInfo.value.summary = "";
      } else if (text.includes("{Done}")) {
        // 完成通知
        isAIProcessing.value = false;
        canEdit.value = true;
        message.success("AI has successfully filled the information.");
        return;
      } else if (currentField) {
        paperInfo.value[currentField] += text;
        console.log(paperInfo.value.name);
        console.log(paperInfo.value.description);
        console.log(paperInfo.value.summary);
      } else {
        console.error("Invalid field detected.");
      }
    }
  } catch (error) {
    message.error("Failed to process AI auto-fill.");
    isAIProcessing.value = false;
    canEdit.value = true;
    console.error(error);
  }
};

const savePaper = async () => {
  try {

    const requestData = {
      name: paperInfo.value.name,
      description: paperInfo.value.description,
      summary: paperInfo.value.summary,
      FileName: backendFileName.value
    };

    const response = await fetch("http://localhost:8000/main/save_paper/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestData),
    });
    if (response.ok) {
      message.success("Paper saved successfully!");
      const responseData = await response.json();
      paperData.value = responseData.paperData;
      isUploadModalVisible.value = false;
      uploading.value = false;
    } else {
      message.error("Failed to save paper.");
    }
  } catch (error) {
    message.error("Error saving paper.");
  }
};

const cancelUpload = async () => {
  const lastFilePath = backendFileName.value;
  await fetch("http://localhost:8000/main/delete_paper/", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({path: lastFilePath}),
  });
  message.info("Upload canceled and file deleted.");
  isUploadModalVisible.value = false;
  uploading.value = false;
};

</script>

<template>
  <a-layout class="page_content">
    <a-layout-header class="header-container">
      <a-image
          :src=logo
          :width=220
          :preview=false
          style="margin-top: 10px"/>
      <!-- 头像 -->
      <a-avatar :src="avatarUrl" :style="{ backgroundColor: '#fff', marginTop: '10px', cursor: 'pointer' }"
                @click="showModal"/>
      <!-- 弹窗 -->
      <a-modal
          v-model:open="isModalVisible"
          title="Update Avatar"
          @ok="handleSaveAvatar"
          @cancel="() => (isModalVisible = false)"
          :bodyStyle="{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '20px' }"
          width="400px">
        <!-- 展示大号头像 -->
        <a-image :src="tempAvatarUrl" width="300" style="border-radius: 50%;"/>
        <!-- 输入框和提交按钮组合 -->
        <a-input-group compact style="display: flex; justify-content: center; align-items: center;">
          <a-input
              v-model:value="newImageText"
              :disabled="isGenerating"
              placeholder="Enter new image text"
              @pressEnter="handleGenerateAvatar"
              style="margin-top: 30px; width: 60%; text-align: center;"/>
          <a-button type="primary" style="margin-top: 30px; width: 40%;" @click="handleGenerateAvatar"
                    :loading="isGenerating">
            Generate
          </a-button>
        </a-input-group>
      </a-modal>
    </a-layout-header>

    <!-- Content部分 -->
    <a-layout-content class="content">
      <div v-if="!chosenPaper.pdfUrl" class="home_content">
        <div class="upload_content">
          <a-upload-dragger
              v-model:fileList="fileList"
              name="pdf_file"
              :multiple="false"
              :showUploadList="false"
              @change="handleFileUpload"
              :disabled="uploading">
            <p class="ant-upload-drag-icon">
              <inbox-outlined/>
            </p>
            <p class="ant-upload-text">Click or drag Paper.pdf to this area to upload</p>
            <p class="ant-upload-hint">Support for data in non-image PDF format</p>
          </a-upload-dragger>

          <!-- 弹窗部分 -->
          <a-modal
              v-model:open="isUploadModalVisible"
              title="Fill in Paper Information"
              @ok="savePaper"
              @cancel="cancelUpload"
              :footer="null"
          >
            <h4>File Name: {{ uploadedFileName }}</h4>
            <p>Paper Title</p>
            <a-input
                :disabled="!canEdit"
                v-model:value="paperInfo.name"
                placeholder="Paper Title"
                style="margin-bottom: 1rem"
            />
            <p>Paper Description</p>
            <a-textarea
                :disabled="!canEdit"
                v-model:value="paperInfo.description"
                placeholder="Paper Description"
                :rows="3"
                style="margin-bottom: 1rem"
            />
            <p>Paper Summary</p>
            <a-textarea
                :disabled="!canEdit"
                v-model:value="paperInfo.summary"
                :rows="8"
                placeholder="Paper Summary"
            />
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
              <a-button @click="handleAutoFill" :loading="isAIProcessing"
                        :disabled="isAIProcessing || !canEdit">
                Intelligent Auto Fill
              </a-button>

              <div>
                <a-button
                    :disabled="!canEdit"
                    style="margin-right: 10px"
                    @click="cancelUpload">
                  Cancel
                </a-button>
                <a-button
                    :disabled="!canEdit"
                    type="primary"
                    @click="savePaper">
                  Save
                </a-button>
              </div>
            </div>
          </a-modal>
        </div>

        <div class="table_content">
          <!-- 论文表格 -->
          <a-table :dataSource="paperData" :columns="columns" bordered @resizeColumn="handleResizeColumn"
                   :scroll="{y:`55vh`}">
            <!-- 自定义搜索图标 -->
            <template #customFilterIcon="{ filtered }">
              <search-outlined :style="{ color: filtered ? '#5A54F9' : undefined }"/>
            </template>
            <!-- 自定义搜索弹出框 -->
            <template #customFilterDropdown="{ setSelectedKeys, selectedKeys, confirm, clearFilters, column }">
              <div style="padding: 8px">
                <a-input
                    ref="searchInput"
                    :placeholder="`Search ${column.name}`"
                    :value="selectedKeys[0]"
                    style="width: 188px; margin-bottom: 8px; display: block"
                    @change="e => setSelectedKeys(e.target.value ? [e.target.value] : [])"
                    @pressEnter="handleSearch(selectedKeys, confirm, column.dataIndex)"
                />
                <a-button
                    type="primary"
                    size="small"
                    style="width: 90px; margin-right: 8px"
                    @click="handleSearch(selectedKeys, confirm, column.dataIndex)"
                >
                  Search
                </a-button>
                <a-button size="small" style="width: 90px" @click="handleReset(clearFilters)">
                  Reset
                </a-button>
              </div>
            </template>
            <template #headerCell="{ column }">
              <template v-if="column.key === 'name'">
                <span style="color: #556B2F">Paper Title</span>
              </template>
            </template>
            <template #bodyCell="{ column, record }">
              <!-- 编辑表格内容 -->
              <template v-if="column.dataIndex === 'name'">
                <a-input v-if="editableData[record.key]" v-model:value="editableData[record.key].name"/>
                <span v-if="state.searchText && state.searchedColumn === column.dataIndex">
                <template
                    v-for="(fragment, i) in record[column.dataIndex]
                    .toString()
                    .split(new RegExp(`(?<=${state.searchText})|(?=${state.searchText})`, 'i'))"
                >
                  <mark
                      v-if="fragment.toLowerCase() === state.searchText.toLowerCase()"
                      :key="i"
                      class="highlight"
                  >
                    {{ fragment }}
                  </mark>
                  <template v-else>{{ fragment }}</template>
                </template>
              </span>
                <span v-else>{{ record[column.dataIndex] }}</span>
              </template>
              <!-- 操作按钮 -->
              <template v-else-if="column.key === 'action'">
                <div class="editable-row-operations">
                  <span v-if="editableData[record.key]">
                    <a-typography-link @click="save(record.key)">Save</a-typography-link>
                    <a-popconfirm title="Sure to cancel?" @confirm="cancel(record.key)">
                      <a>Cancel</a>
                    </a-popconfirm>
                  </span>
                  <span v-else>
                    <a-button type="text" size="small" style="color: green" @click="edit(record.key)">Edit</a-button>
                  </span>
                  <span>
                    <a-button type="text" size="small" style="color: #5A54F9" @click="openPaper(record)">
                      Open
                    </a-button>
                  </span>
                  <span>
                    <a-popconfirm title="Sure to delete?" @confirm="deletePaper(record)">
                      <a-button style="color: red" type="text" size="small">Delete</a-button>
                    </a-popconfirm>
                  </span>
                </div>
              </template>
            </template>
            <template #expandedRowRender="{ record }">
              <p style="margin: 0">
                {{ record.description }}
              </p>
            </template>
          </a-table>
        </div>
      </div>
      <div v-else>
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
                  <template #title>{{ chosenPaper.title }}</template>
                  <div class="truncate-text">{{ chosenPaper.title }}</div>
                </a-tooltip>
              </div>
              <div class="pdf_file">
                <!-- pdf组件 -->
                <PdfC :chosenPaper="chosenPaper"/>
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
                    Learning Flashcards
                  </template>
                  <div class="tab_content">
                    <FlashCards :chosenPaper="chosenPaper"/>
                  </div>
                </a-tab-pane>
                <a-tab-pane key="2">
                  <template #tab>
                    <CommentOutlined/>
                    Chat with the Author
                  </template>
                  <div class="tab_content">
                    <GroupChat :avatarUrl="avatarUrl" :chosenPaper="chosenPaper"/>
                  </div>
                </a-tab-pane>
              </a-tabs>
            </div>
          </a-col>
        </a-row>
      </div>
    </a-layout-content>
  </a-layout>
</template>

<style scoped>

.page_content {
  height: 100vh;
  background-image: url('../assets/bg_p.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 6vh;
  background: rgba(255, 255, 255, 0);
}

.home_content {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 5px;
  border-radius: 12px;
  height: 92vh;
}

.upload_content {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 10px;
  margin-bottom: 0.8vh;
  border-radius: 8px;
  height: 20vh;
}

.table_content {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 10px;
  border-radius: 8px;
  height: 70vh;
}

.editable-row-operations a {
  margin-right: 8px;
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
  border-radius: 8px;
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
  width: 50%;
  gap: 5px;
  font-weight: bold;
}

.pdf_title span,
.pdf_title LeftOutlined {
  font-size: 15px;
  margin: 5px;
}

.truncate-text {
  display: inline-block;
  max-width: 85%; /* 根据需要调整最大宽度 */
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  vertical-align: bottom;
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
  border-radius: 8px;
  height: 92vh;
  font-weight: bold;
}

.tab_content {
  height: 84vh;
  overflow: auto;
  border-radius: 8px;
  font-weight: normal;
}

.highlight {
  background-color: #5A54F9;
  color: #fff;
  padding: 0;
}

</style>
