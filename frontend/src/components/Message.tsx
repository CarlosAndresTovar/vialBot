import { Bot, User } from 'lucide-react'
import type { ChatMessage } from '../services/api'

interface MessageProps {
  message: ChatMessage
}

export function Message({ message }: MessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
          isUser ? 'bg-brand-600' : 'bg-gray-200'
        }`}
      >
        {isUser ? <User className="h-5 w-5 text-white" /> : <Bot className="h-5 w-5 text-gray-700" />}
      </div>
      <div
        className={`max-w-[80%] whitespace-pre-wrap rounded-2xl px-4 py-2 text-sm ${
          isUser ? 'bg-brand-600 text-white rounded-br-none' : 'bg-white text-gray-800 shadow-sm rounded-bl-none'
        }`}
      >
        {message.content}
      </div>
    </div>
  )
}
