import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Login from './pages/Login'
import Register from './pages/Register'
import Chat from './pages/Chat'

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    setToken(localStorage.getItem('token'))
  }, [])

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login setToken={setToken} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={token ? <Chat token={token} /> : <Navigate to="/login" />} />
      </Routes>
    </Router>
  )
}

export default App
