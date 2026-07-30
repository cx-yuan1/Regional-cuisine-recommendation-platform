/**
 * AI 美食推荐对话 API（流式）
 */

const API_BASE = '/api'

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  streaming?: boolean
}

export type StreamChunk = { content?: string; error?: string; done?: boolean }

/**
 * 流式对话：POST /api/ai/chat
 * @param messages 对话历史
 * @param onChunk 每收到一块内容时回调
 */
export async function chatStream(
  messages: ChatMessage[],
  onChunk: (chunk: StreamChunk) => void
): Promise<void> {
  const url = `${API_BASE}/ai/chat`
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream'
    },
    credentials: 'include',
    body: JSON.stringify({ messages })
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.message || `请求失败 ${res.status}`)
  }

  const reader = res.body?.getReader()
  if (!reader) throw new Error('无法读取响应流')

  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('data:')) {
        const raw = line.slice(5).trim()
        if (!raw || raw === '[DONE]') {
          onChunk({ done: true })
          continue
        }
        try {
          const obj = JSON.parse(raw) as StreamChunk
          onChunk(obj)
        } catch {
          // 忽略解析错误
        }
      }
    }
  }

  if (buffer.trim()) {
    const line = buffer
    if (line.startsWith('data:')) {
      const raw = line.slice(5).trim()
      if (raw && raw !== '[DONE]') {
        try {
          const obj = JSON.parse(raw) as StreamChunk
          onChunk(obj)
        } catch {
          // ignore
        }
      }
    }
  }
  onChunk({ done: true })
}
