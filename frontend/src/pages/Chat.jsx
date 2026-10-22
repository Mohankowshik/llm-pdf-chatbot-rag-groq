import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function Chat({ token }) {
  const [files, setFiles] = useState([])
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('')
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Fetch initial chat history
    const fetchHistory = async () => {
      try {
        const res = await axios.get(`${API_BASE}/api/history`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.data && res.data.history) {
          const historyList = [...res.data.history].reverse()
          const formattedMessages = historyList.flatMap(item => [
            { role: 'user', content: item.question },
            { role: 'assistant', content: item.answer, sources: item.sources }
          ])
          setMessages(formattedMessages)
        }
      } catch (err) {
        console.error('Failed to load chat history:', err)
        if (err.response?.status === 401) {
          handleLogout()
        }
      }
    }

    if (token) {
      fetchHistory()
    }
  }, [token])

  const handleFileChange = (e) => {
    setFiles(e.target.files)
  }

  const handleUpload = async () => {
    if (files.length === 0) return
    setUploading(true)
    setUploadStatus('')
    const formData = new FormData()
    const newFileNames = []
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i])
      newFileNames.push(files[i].name)
    }
    try {
      const res = await axios.post(`${API_BASE}/api/upload`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      })
      const failed = res.data?.results?.filter(r => r.status === 'failed') || []
      if (failed.length > 0) {
        setUploadStatus(`Upload completed with errors: ${failed.map(f => `${f.filename}: ${f.error}`).join(', ')}`)
      } else {
        setUploadStatus('Files processed and indexed successfully!')
        setUploadedFiles(prev => Array.from(new Set([...prev, ...newFileNames])))
        setFiles([])
      }
    } catch (err) {
      console.error(err)
      if (err.response?.status === 401) {
        setUploadStatus('Session expired. Please log in again.')
        setTimeout(() => handleLogout(), 1500)
      } else {
        const errorDetail = err.response?.data?.detail || err.message || 'Upload failed. Please try again.'
        setUploadStatus(`Upload failed: ${errorDetail}`)
      }
    } finally {
      setUploading(false)
    }
  }

  const handleSend = async () => {
    if (!input.trim()) return
    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    const question = input
    setInput('')
    setLoading(true)
    try {
      const res = await axios.post(`${API_BASE}/api/chat`, { question }, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const botMessage = { role: 'assistant', content: res.data.answer, sources: res.data.sources }
      setMessages(prev => [...prev, botMessage])
    } catch (err) {
      console.error(err)
      if (err.response?.status === 401) {
        setMessages(prev => [...prev, { role: 'assistant', content: '⚠️ Your session has expired. Please log in again.' }])
        setTimeout(() => handleLogout(), 2000)
      } else {
        const detail = err.response?.data?.detail || 'An error occurred while generating the answer. Please try again.'
        setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${detail}` }])
      }
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    window.location.href = '/login'
  }

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <nav className="bg-white border-b px-6 py-4 flex justify-between items-center shadow-sm">
        <div className="flex items-center space-x-2">
          <div className="bg-blue-600 text-white rounded-lg p-2 font-bold text-lg">PDF</div>
          <h1 className="text-xl font-bold text-gray-800">RAG Chatbot</h1>
        </div>
        <button
          onClick={handleLogout}
          className="text-gray-600 hover:text-red-600 font-medium transition"
        >
          Logout
        </button>
      </nav>
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 bg-white p-5 border-r flex flex-col justify-between shadow-sm">
          <div>
            <h2 className="font-semibold text-gray-700 text-lg mb-3">Upload Documents</h2>
            <div className="mb-4">
              <label className="block text-xs text-gray-500 mb-1 font-medium">Select PDF files</label>
              <input
                type="file"
                multiple
                accept=".pdf"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 border rounded-lg p-1"
              />
            </div>
            <button
              onClick={handleUpload}
              disabled={uploading || files.length === 0}
              className="w-full bg-blue-600 text-white font-medium py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
            >
              {uploading ? 'Processing PDFs...' : 'Upload & Index'}
            </button>
            {uploadStatus && (
              <p className={`text-xs mt-3 p-2 rounded ${uploadStatus.includes('failed') ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-700'}`}>
                {uploadStatus}
              </p>
            )}

            {uploadedFiles.length > 0 && (
              <div className="mt-6">
                <h3 className="font-semibold text-gray-700 text-sm mb-2">Uploaded Session Files</h3>
                <ul className="space-y-1">
                  {uploadedFiles.map((fn, idx) => (
                    <li key={idx} className="text-xs bg-gray-50 p-2 rounded border flex items-center text-gray-700">
                      <span className="truncate">📄 {fn}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="text-xs text-gray-400 border-t pt-4 text-center">
            Powered by Groq LLM & ChromaDB
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col bg-white m-3 rounded-xl shadow-sm border overflow-hidden">
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
                <div className="text-4xl mb-3">💬</div>
                <p className="text-lg font-medium text-gray-600">Welcome to PDF Chatbot!</p>
                <p className="text-sm max-w-sm mt-1">Upload your PDF documents on the left panel, then ask any question about their contents.</p>
              </div>
            )}
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[75%] p-4 rounded-2xl ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-gray-100 text-gray-800 rounded-tl-none border'}`}>
                  {msg.role === 'assistant' ? (
                    <div className="prose text-sm max-w-none">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  ) : (
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  )}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-300">
                      <p className="font-semibold text-xs text-gray-600 mb-1">Sources Referenced:</p>
                      {msg.sources.map((src, i) => (
                        <div key={i} className="text-xs bg-white text-gray-700 p-2 rounded mt-1 border">
                          <span className="font-medium">📄 {src.filename}</span> (Page {src.page}): <span className="italic">{src.snippet}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-500 text-sm p-4 rounded-2xl rounded-tl-none border flex items-center space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                  <span className="ml-2 font-medium">Analyzing documents...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="border-t p-4 bg-gray-50">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Type your question about the uploaded documents..."
                className="flex-1 px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-sm"
              />
              <button
                onClick={handleSend}
                disabled={loading || !input.trim()}
                className="bg-blue-600 text-white font-medium px-6 py-3 rounded-xl hover:bg-blue-700 disabled:opacity-50 transition text-sm"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Chat

