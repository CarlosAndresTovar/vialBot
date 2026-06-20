import { useEffect, useRef, useState } from 'react'
import { Send, Bot } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { sendMessageStream, type ChatMessage } from '../services/api'
import { Message } from './Message'

export function Chat() {
  const { token, logout } = useAuth()
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content:
        '¡Hola! Soy vialBot 🇨🇴, tu amigo experto en el Código Nacional de Tránsito. ¿Qué duda tienes hoy?',
    },
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [threadId, setThreadId] = useState<string | undefined>(undefined)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || !token) return

    const userMessage: ChatMessage = { role: 'user', content: input.trim() }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    const assistantMessage: ChatMessage = { role: 'assistant', content: '' }
    setMessages((prev) => [...prev, assistantMessage])

    try {
      await sendMessageStream(
        { message: userMessage.content, thread_id: threadId },
        token,
        (chunk) => {
          assistantMessage.content += chunk
          setMessages((prev) => {
            const updated = [...prev]
            updated[updated.length - 1] = { ...assistantMessage }
            return updated
          })
        },
        (newThreadId) => {
          setThreadId(newThreadId)
          setIsLoading(false)
        },
        (error) => {
          assistantMessage.content = `Ups, ocurrió un error: ${error.message}`
          setMessages((prev) => {
            const updated = [...prev]
            updated[updated.length - 1] = { ...assistantMessage }
            return updated
          })
          setIsLoading(false)
        },
      )
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Lo siento, ocurrió un error al procesar tu pregunta. Inténtalo de nuevo.',
        },
      ])
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-screen flex-col bg-gradient-to-br from-gray-50 to-blue-50">
      <header className="flex items-center justify-between border-b bg-white/80 px-6 py-4 shadow-sm backdrop-blur">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-600 text-white">
            <Bot className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">vialBot</h1>
            <p className="text-xs text-gray-500">Tu amigo experto en tránsito 🇨🇴</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
        >
          Cerrar sesión
        </button>
      </header>

      <main className="flex-1 overflow-y-auto p-4 scrollbar-thin">
        <div className="mx-auto flex max-w-3xl flex-col gap-4">
          {messages.map((message, index) => (
            <Message key={index} message={message} />
          ))}
          <div ref={messagesEndRef} />
          {isLoading && messages[messages.length - 1]?.role === 'user' && (
            <div className="flex gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-200">
                <span className="sr-only">vialBot</span>
              </div>
              <div className="flex items-center rounded-2xl rounded-bl-none bg-white px-4 py-2 shadow-sm">
                <div className="flex gap-1">
                  <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400" />
                  <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:0.1s]" />
                  <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:0.2s]" />
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="border-t bg-white/80 p-4 backdrop-blur">
        <div className="mx-auto flex max-w-3xl gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            placeholder="Escribe tu duda de tránsito..."
            className="max-h-32 flex-1 resize-none rounded-xl border border-gray-300 px-4 py-2.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="flex items-center justify-center rounded-xl bg-brand-600 px-4 text-white transition hover:bg-brand-700 disabled:opacity-50"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
        <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-gray-400">
          vialBot es un asistente orientativo. Verifica la información con la norma oficial.
        </p>
      </footer>
    </div>
  )
}
