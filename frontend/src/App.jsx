import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import Documents from './pages/Documents'
import CodeIntelligence from './pages/CodeIntelligence'
import Users from './pages/Users'
import Roles from './pages/Roles'
import AuditLogs from './pages/AuditLogs'
import Settings from './pages/Settings'

import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route path="/dashboard" element={<Dashboard />} />

        <Route path="/chat" element={<Chat />} />

        <Route path="/documents" element={<Documents />} />

        <Route path="/code" element={<CodeIntelligence />} />

        <Route path="/users" element={<Users />} />

        <Route path="/roles" element={<Roles />} />

        <Route path="/audit-logs" element={<AuditLogs />} />

        <Route path="/settings" element={<Settings />} />

        {/* Default route */}
        <Route
          path="*"
          element={<Navigate to="/login" replace />}
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App