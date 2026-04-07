// frontend/src/pages/Profiler.tsx
import { useEffect, useState } from 'react'
import { api } from '../api/client'
import ScalingChart from '../components/ScalingChart'
import ResultsTable from '../components/ResultsTable'

export default function Profiler() {
  const [algorithms, setAlgorithms] = useState<any[]>([])
  const [selectedAlgo, setSelectedAlgo] = useState<number | ''>('')
  const [minN, setMinN] = useState(5)
  const [maxN, setMaxN] = useState(100)
  const [samples, setSamples] = useState(3)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => { api.listAlgorithms().then(setAlgorithms) }, [])

  const handleRun = async () => {
    if (!selectedAlgo) return
    setLoading(true)
    try {
      const run = await api.runProfiler({
        algorithm_id: +selectedAlgo,
        min_n: minN,
        max_n: maxN,
        samples_per_size: samples,
      })
      setResult(run)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ color: 'var(--accent)', fontSize: 16 }}>Complexity Profiler</h2>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <select value={selectedAlgo} onChange={e => setSelectedAlgo(+e.target.value || '')} style={{ width: 160 }}>
            <option value="">Select algorithm</option>
            {algorithms.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
          </select>
          <label style={{ color: 'var(--text-dim)', fontSize: 11 }}>n:</label>
          <input type="number" value={minN} onChange={e => setMinN(+e.target.value)} style={{ width: 50 }} />
          <span style={{ color: 'var(--text-dim)' }}>–</span>
          <input type="number" value={maxN} onChange={e => setMaxN(+e.target.value)} style={{ width: 60 }} />
          <label style={{ color: 'var(--text-dim)', fontSize: 11 }}>samples=</label>
          <input type="number" value={samples} onChange={e => setSamples(+e.target.value)} style={{ width: 40 }} />
          <button className="btn btn-primary" onClick={handleRun} disabled={loading || !selectedAlgo}>
            {loading ? 'Profiling...' : 'Profile'}
          </button>
        </div>
      </div>

      {result && (
        <div className="split">
          <ScalingChart data={result.data_points} bestFit={result.best_fit} />
          <div>
            <div className="panel" style={{ marginBottom: 16 }}>
              <div className="panel-header">Classification</div>
              <div className="panel-body" style={{ textAlign: 'center', padding: 24 }}>
                <div style={{ fontSize: 28, color: 'var(--primary)', fontWeight: 'bold' }} className="glow">
                  {result.best_fit || '–'}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 4 }}>
                  R² = {result.best_fit_r2?.toFixed(4) ?? '–'}
                </div>
              </div>
            </div>
            <ResultsTable
              columns={[
                { key: 'name', label: 'Complexity Class' },
                {
                  key: 'r_squared', label: 'R²',
                  render: (v: number) => (
                    <span style={{ color: v > 0.9 ? 'var(--primary)' : 'var(--text-dim)' }}>
                      {v.toFixed(4)}
                    </span>
                  ),
                },
              ]}
              rows={result.fits || []}
            />
          </div>
        </div>
      )}

      {!result && (
        <div className="panel">
          <div className="panel-body" style={{ color: 'var(--text-dim)', textAlign: 'center', padding: 64 }}>
            Select an algorithm and click Profile to measure scaling behavior
          </div>
        </div>
      )}
    </div>
  )
}
