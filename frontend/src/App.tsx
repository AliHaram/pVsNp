// frontend/src/App.tsx
import { Routes, Route, NavLink } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { api } from './api/client'
import Arena from './pages/Arena'
import Instances from './pages/Instances'
import Counterexamples from './pages/Counterexamples'
import Profiler from './pages/Profiler'
import ComplexityFinder from './pages/ComplexityFinder'

function App() {
  const [status, setStatus] = useState<any>(null)

  useEffect(() => {
    const poll = () => api.getStatus().then(setStatus).catch(() => {})
    poll()
    const interval = setInterval(poll, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <nav className="nav">
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <span className="nav-brand glow">P vs NP</span>
          <span style={{ color: 'var(--text-ghost)' }}>│</span>
          <div className="nav-links">
            <NavLink to="/" end>Arena</NavLink>
            <NavLink to="/instances">Instances</NavLink>
            <NavLink to="/counterexamples">Counterexamples</NavLink>
            <NavLink to="/profiler">Profiler</NavLink>
            <NavLink to="/complexity">Complexity Finder</NavLink>
          </div>
        </div>
        <span className="nav-watermark">Connected</span>
      </nav>

      <div className="main">
        <Routes>
          <Route path="/" element={<Arena />} />
          <Route path="/instances" element={<Instances />} />
          <Route path="/counterexamples" element={<Counterexamples />} />
          <Route path="/profiler" element={<Profiler />} />
          <Route path="/complexity" element={<ComplexityFinder />} />
        </Routes>
      </div>

      <div className="status-bar">
        <span>
          workers: {status?.workers_active ?? '–'}/{status?.workers_total ?? '–'} idle
          {' · '}instances: {status?.instances_count ?? '–'}
          {' · '}algorithms: {status?.algorithms_count ?? '–'}
        </span>
        <span>
          sqlite: {status ? `${(status.db_size_bytes / 1024).toFixed(1)}KB` : '–'}
          {' · '}uptime: {status ? formatUptime(status.uptime_seconds) : '–'}
        </span>
      </div>
    </div>
  )
}

function formatUptime(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

export default App
