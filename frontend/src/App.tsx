import { AuthGuard } from './components/AuthGuard'
import { Chat } from './components/Chat'

function App() {
  return (
    <AuthGuard>
      <Chat />
    </AuthGuard>
  )
}

export default App
