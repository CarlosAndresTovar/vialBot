const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatRequest {
  message: string
  thread_id?: string
}

export interface ChatResponse {
  answer: string
  thread_id: string
}

export async function sendMessage(
  request: ChatRequest,
  token: string,
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(error || 'Error al enviar el mensaje')
  }

  return response.json()
}

export async function sendMessageStream(
  request: ChatRequest,
  token: string,
  onChunk: (chunk: string) => void,
  onDone: (threadId: string) => void,
  onError: (error: Error) => void,
): Promise<void> {
  const response = await fetch(`${API_URL}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(request),
  })

  if (!response.ok || !response.body) {
    const errorText = await response.text()
    onError(new Error(errorText || 'Error al iniciar el stream'))
    return
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n\n')

      for (const line of lines) {
        if (!line.trim()) continue
        if (line.startsWith('event: done')) {
          const dataLine = line.split('\n')[1]
          const threadId = dataLine?.replace('data: ', '')
          if (threadId) onDone(threadId)
        } else if (line.startsWith('data: ')) {
          const data = line.replace('data: ', '')
          onChunk(data)
        }
      }
    }
  } catch (error) {
    onError(error instanceof Error ? error : new Error('Error en el stream'))
  } finally {
    reader.releaseLock()
  }
}
