import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ChatMessage } from '@/api/ai'

/** 按用户隔离的对话记录：key 为 user_${id} 或 'guest' */
const messagesByUser = ref<Record<string, ChatMessage[]>>({})

export const useAiChatStore = defineStore('aiChat', () => {
  function getUserKey(userId: number | null | undefined): string {
    return userId != null ? `user_${userId}` : 'guest'
  }

  function getMessages(userKey: string): ChatMessage[] {
    return messagesByUser.value[userKey] ?? []
  }

  function addMessage(userKey: string, msg: ChatMessage) {
    if (!messagesByUser.value[userKey]) {
      messagesByUser.value[userKey] = []
    }
    messagesByUser.value[userKey].push(msg)
  }

  function clearMessages(userKey: string) {
    messagesByUser.value[userKey] = []
  }

  return {
    getUserKey,
    getMessages,
    addMessage,
    clearMessages
  }
})
