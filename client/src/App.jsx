import { useState, useEffect } from 'react'
import io from 'socket.io-client'
import './App.css'

const socket = io('http://localhost:5000')

function App() {
  const [user, setUser] = useState(null)
  const [loginData, setLoginData] = useState({ username: '', password: '' })
  const [registerData, setRegisterData] = useState({ username: '', password: '' })
  const [isRegistering, setIsRegistering] = useState(false)
  const [chats, setChats] = useState([])
  const [currentChat, setCurrentChat] = useState(null)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')

  useEffect(() => {
    socket.on('new_message', (messageData) => {
      if (messageData.chat_id === currentChat?.id) {
        setMessages(prev => [...prev, messageData])
      }
    })

    return () => {
      socket.off('new_message')
    }
  }, [currentChat])

  const handleLogin = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginData)
      })
      const data = await response.json()
      if (data.success) {
        setUser({ username: loginData.username })
        fetchChats()
      } else {
        alert(data.message)
      }
    } catch (error) {
      console.error('Login error:', error)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('http://localhost:5000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registerData)
      })
      const data = await response.json()
      if (data.success) {
        setUser({ username: registerData.username })
        fetchChats()
      } else {
        alert(data.message)
      }
    } catch (error) {
      console.error('Register error:', error)
    }
  }

  const fetchChats = async () => {
    try {
      const response = await fetch('http://localhost:5000/chats')
      const data = await response.json()
      setChats(data)
    } catch (error) {
      console.error('Fetch chats error:', error)
    }
  }

  const selectChat = async (chat) => {
    // Leave the previous room if already in one
    if (currentChat) {
      socket.emit('leave_chat', { chat_id: currentChat.id })
    }
    setCurrentChat(chat)
    try {
      const response = await fetch(`http://localhost:5000/chat/${chat.id}`)
      const data = await response.json()
      setMessages(data)
      socket.emit('join_chat', { chat_id: chat.id })
    } catch (error) {
      console.error('Fetch messages error:', error)
    }
  }

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!newMessage.trim()) return
    try {
      const response = await fetch('http://localhost:5000/send_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: currentChat.id, message: newMessage })
      })
      const data = await response.json()
      if (data.success) {
        setNewMessage('')
      } else {
        alert(data.message)
      }
    } catch (error) {
      console.error('Send message error:', error)
    }
  }

  if (!user) {
    if (isRegistering) {
      return (
        <div className="register">
          <h1>Register</h1>
          <form onSubmit={handleRegister}>
            <input
              type="text"
              placeholder="Username"
              value={registerData.username}
              onChange={(e) => setRegisterData({ ...registerData, username: e.target.value })}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={registerData.password}
              onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
              required
            />
            <button type="submit">Register</button>
          </form>
          <button type="button" onClick={() => setIsRegistering(false)}>Already have an account? Login</button>
        </div>
      )
    } else {
      return (
        <div className="login">
          <h1>Login</h1>
          <form onSubmit={handleLogin}>
            <input
              type="text"
              placeholder="Username"
              value={loginData.username}
              onChange={(e) => setLoginData({ ...loginData, username: e.target.value })}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={loginData.password}
              onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
              required
            />
            <button type="submit">Login</button>
          </form>
          <button type="button" onClick={() => setIsRegistering(true)}>Not a user yet? Register</button>
        </div>
      )
    }
  }

  return (
    <div className="app">
      <div className="sidebar">
        <h2>Chats</h2>
        <ul>
          {chats.map(chat => (
            <li key={chat.id} onClick={() => selectChat(chat)}>
              {chat.name}
            </li>
          ))}
        </ul>
      </div>
      <div className="chat">
        {currentChat ? (
          <>
            <h2>{currentChat.name}</h2>
            <div className="messages">
              {messages.map(msg => (
                <div key={msg.id} className="message">
                  <strong>{msg.username}:</strong> {msg.message}
                  <small>{new Date(msg.timestamp).toLocaleString()}</small>
                </div>
              ))}
            </div>
            <form onSubmit={sendMessage}>
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type a message..."
                required
              />
              <button type="submit">Send</button>
            </form>
          </>
        ) : (
          <p>Select a chat to start messaging</p>
        )}
      </div>
    </div>
  )
}

export default App
