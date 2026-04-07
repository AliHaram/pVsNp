// frontend/src/pages/ComplexityFinder.tsx
import { useState } from 'react'
import { api } from '../api/client'
import ScalingChart from '../components/ScalingChart'
import CodeEditor from '../components/CodeEditor'
import ResultsTable from '../components/ResultsTable'

const TEMPLATE = `"""
name: My Algorithm
input_generator: random_list
"""

def run(data):
    # Your algorithm here
    result = sorted(data)
    return result
`

export default function ComplexityFinder() {
  const [code, setCode] = useState(TEMPLATE)
  const [inputGen, setInputGen] = useState('random_list')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleAnalyze = async () => {
    setLoading(true)
    try {
      const blob = new Blob([code], { type: 'text/x-python' })
      const file = new File([blob], 'algorithm.py', { type: 'text/x-python' })
      const analysis = await api.analyzeComplexity(file, inputGen)
      setResult(analysis)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ color: 'var(--secondary)', fontSize: 16 }}>Complexity Finder</h2>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <select value={inputGen} onChange={e => setInputGen(e.target.value)} style={{ width: 140 }}>
            <option value="random_list">Random List</option>
            <option value="sorted_list">Sorted List</option>
            <option value="reversed_list">Reversed List</option>
            <option value="random_string">Random String</option>
            <option value="random_graph">Random Graph</option>
          </select>
          <button className="btn btn-primary" onClick={handleAnalyze} disabled={loading}>
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
      </div>

      <div className="split">
        <div>
          <CodeEditor value={code} onChange={setCode} placeholder="# Implement run(data) -> result" />
        </div>

        <div>
          {result ? (
            <>
              <div className="panel" style={{ marginBottom: 16 }}>
                <div className="panel-header">Classification</div>
                <div className="panel-body" style={{ textAlign: 'center', padding: 24 }}>
                  <div style={{ fontSize: 28, color: 'var(--primary)', fontWeight: 'bold' }} className="glow">
                    {result.best_fit || '–'}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 4 }}>
                    confidence: {result.best_fit_r2 ? `${(result.best_fit_r2 * 100).toFixed(1)}%` : '–'}
                  </div>
                </div>
              </div>
              <ScalingChart data={result.data_points} bestFit={result.best_fit} />
              <div style={{ marginTop: 16 }}>
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
            </>
          ) : (
            <div className="panel">
              <div className="panel-body" style={{ color: 'var(--text-dim)', textAlign: 'center', padding: 64 }}>
                Write a run(data) function and click Analyze to determine its complexity
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
