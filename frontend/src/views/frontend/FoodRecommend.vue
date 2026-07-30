<template>
  <div class="food-recommend-page">
    <Header />

    <div class="page-container">
      <div class="chat-header">
        <div class="header-row">
          <div>
            <h2 class="page-title">AI 美食推荐</h2>
            <p class="page-desc">告诉我你的口味偏好、预算或想吃的菜系，我会为你推荐平台上的优质美食</p>
          </div>
          <el-button
            v-if="messages.length > 0"
            type="default"
            size="small"
            @click="aiChatStore.clearMessages(userKey)"
          >
            清空对话
          </el-button>
        </div>
      </div>

      <div class="chat-box">
        <div class="messages" ref="messagesRef">
          <div v-if="messages.length === 0" class="welcome">
            <div class="welcome-icon">🍽️</div>
            <p>你好！我是美食推荐助手。</p>
            <p>你可以告诉我：想吃什么口味、预算多少、喜欢哪个地域的美食，我会为你推荐平台上的美食。</p>
            <p class="hint">例如：「我想吃辣的川菜」「预算 50 左右有什么推荐」「江浙一带有什么清淡的」</p>
          </div>

          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            :class="['msg', msg.role]"
          >
            <div class="msg-avatar">
              <el-avatar
                v-if="msg.role === 'user'"
                :src="userAvatar"
                :size="36"
              >
                <el-icon><User /></el-icon>
              </el-avatar>
              <span v-else class="ai-avatar">AI</span>
            </div>
            <div class="msg-content">
              <div v-if="msg.role === 'user'" class="text">{{ msg.content }}</div>
              <div v-else class="text">
                <span v-html="formatContent(msg.content)"></span>
                <span v-if="msg.streaming" class="cursor">|</span>
              </div>
            </div>
          </div>
        </div>

        <div class="input-area">
          <el-input
            v-model="inputText"
            type="textarea"
            :rows="2"
            placeholder="输入你的需求，如：想吃辣的、预算50、江浙菜..."
            :disabled="sending"
            @keydown.enter.exact.prevent="send"
            resize="none"
          />
          <el-button
            type="primary"
            :loading="sending"
            :disabled="!inputText.trim()"
            @click="send"
          >
            发送
          </el-button>
        </div>
      </div>
    </div>

    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick, onMounted } from 'vue'
import { User } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useAiChatStore } from '@/stores/aiChat'
import { chatStream, type ChatMessage } from '@/api/ai'
import Header from '@/components/common/Header.vue'
import Footer from '@/components/common/Footer.vue'

const userStore = useUserStore()
const aiChatStore = useAiChatStore()
const userKey = computed(() => aiChatStore.getUserKey(userStore.user?.id))
const userAvatar = computed(() => {
  const avatar = userStore.user?.avatar
  if (!avatar) return ''
  if (avatar.startsWith('http')) return avatar
  return avatar.startsWith('/') ? avatar : `/${avatar}`
})

const messagesRef = ref<HTMLElement>()
const messages = computed(() => aiChatStore.getMessages(userKey.value))
const inputText = ref('')
const sending = ref(false)

function formatContent(text: string) {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
}

async function send() {
  const text = inputText.value.trim()
  if (!text || sending.value) return

  const userMsg: ChatMessage = { role: 'user', content: text }
  aiChatStore.addMessage(userKey.value, userMsg)
  inputText.value = ''
  sending.value = true

  const assistantMsg = reactive<ChatMessage>({ role: 'assistant', content: '', streaming: true })
  aiChatStore.addMessage(userKey.value, assistantMsg)

  await nextTick()
  scrollToBottom()

  try {
    const history: ChatMessage[] = aiChatStore.getMessages(userKey.value)
      .filter((m) => m.role !== 'system')
      .slice(0, -1)
      .map((m) => ({ role: m.role, content: m.content } as ChatMessage))

    await chatStream(history, (chunk) => {
      if (chunk.error) {
        assistantMsg.content += `[错误: ${chunk.error}]`
      } else if (chunk.content) {
        assistantMsg.content += chunk.content
        nextTick(() => scrollToBottom())
      }
      if (chunk.done) {
        assistantMsg.streaming = false
      }
    })
  } catch (e) {
    assistantMsg.content += `\n[请求失败: ${(e as Error).message}]`
    assistantMsg.streaming = false
  } finally {
    sending.value = false
    nextTick(() => scrollToBottom())
  }
}

function scrollToBottom() {
  nextTick(() => {
    messagesRef.value?.scrollTo({ top: messagesRef.value.scrollHeight, behavior: 'smooth' })
  })
}

onMounted(() => {
  if (aiChatStore.getMessages(userKey.value).length > 0) scrollToBottom()
})
</script>

<style scoped lang="scss">
.food-recommend-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.page-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 20px;
}

.chat-header {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-desc {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.chat-box {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 480px;
}

.messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  max-height: 420px;
}

.welcome {
  text-align: center;
  padding: 40px 24px;
  color: #606266;

  .welcome-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }

  p {
    margin: 8px 0;
    font-size: 14px;
    line-height: 1.6;
  }

  .hint {
    font-size: 13px;
    color: #909399;
    margin-top: 16px;
  }
}

.msg {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;

  &.user {
    flex-direction: row-reverse;

    .msg-content {
      background: #ecf5ff;
      color: #303133;
    }
  }

  &.assistant .msg-content {
    background: #f4f4f5;
    color: #303133;
  }
}

.msg-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;

  .ai-avatar {
    font-weight: 600;
    color: #409eff;
  }
}

.msg-content {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;

  .cursor {
    animation: blink 1s step-end infinite;
  }
}

@keyframes blink {
  50% { opacity: 0; }
}

.input-area {
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  gap: 12px;
  align-items: flex-end;

  .el-input {
    flex: 1;
  }

  .el-button {
    flex-shrink: 0;
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }

  .msg-content {
    max-width: 85%;
  }
}
</style>
