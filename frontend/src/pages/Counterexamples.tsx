// frontend/src/pages/Counterexamples.tsx
import { useEffect, useState } from 'react'
import { api } from '../api/client'
import GraphViewer from '../components/GraphViewer'
import ResultsTable from '../components/ResultsTable'

export default function Counterexamples() {
  const [algorithms, setAlgorithms] = useState<any[]>([])
  const [counterexamples, setCounterexamples] = useState<any[]>([])
  const [selectedAlgo, setSelectedAlgo] = useState<number | ''>('')
  const [selectedCE, setSelectedCE] = useState<any>(null)
  const [count, setCount] = useState(100)
  const [maxN, setMaxN] = useState(10)
  const [strategy, setStrategy] = useState('random')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.listAlgorithms().then(setAlgorithms)
    api.listCounterexamples().then(setCounterexamples)
  }, [])

  const handleHunt = async () => {
    if (!selectedAlgo) return
    setLoading(true)
    try {
      const found = await api.huntCounterexamples({
        algorithm_id: +selectedAlgo,
        strategy,
        count,
        max_n: maxN,
      })
      setCounterexamples(prev => [...found, ...prev])
    } finally {
      setLoading(false)
    }
  }

  const handleViewCE = async (ce: any) => {
    const inst = await api.getInstance(ce.instance_id)
    setSelectedCE({ ...ce, points: inst.points })
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ color: 'var(--danger)', fontSize: 16 }}>Counterexample Engine</h2>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <select value={selectedAlgo} onChange={e => setSelectedAlgo(+e.target.value || '')} style={{ width: 160 }}>
            <option value="">Select algorithm</option>
            {algorithms.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
          </select>
          <select value={strategy} onChange={e => setStrategy(e.target.value)} style={{ width: 110 }}>
            <option value="random">Random</option>
            <option value="structured">Structured</option>
          </select>
          <label style={{ color: 'var(--text-dim)', fontSize: 11 }}>count=</label>
          <input type="number" value={count} onChange={e => setCount(+e.target.value)} style={{ width: 60 }} />
          <label style={{ color: 'var(--text-dim)', fontSize: 11 }}>max_n=</label>
          <input type="number" value={maxN} onChange={e => setMaxN(+e.target.value)} style={{ width: 50 }} />
          <button className="btn btn-primary" onClick={handleHunt} disabled={loading || !selectedAlgo}>
            {loading ? 'Hunting...' : 'Hunt'}
          </button>
        </div>
      </div>

      <div className="split">
        <div>
          <ResultsTable
            columns={[
              { key: 'id', label: '#' },
              { key: 'algorithm_tour_length', label: 'Algo Tour', render: (v: number) => v.toFixed(2) },
              { key: 'optimal_tour_length', label: 'Optimal', render: (v: number) => v.toFixed(2) },
              {
                key: 'id', label: 'Gap',
                render: (_: any, row: any) => {
                  const gap = ((row.algorithm_tour_length / row.optimal_tour_length - 1) * 100).toFixed(1)
                  return <span style={{ color: 'var(--danger)' }}>+{gap}%</span>
                },
              },
              {
                key: 'id', label: '',
                render: (_: any, row: any) => (
                  <button className="btn" onClick={() => handleViewCE(row)} style={{ padding: '2px 8px', fontSize: 10 }}>
                    view
                  </button>
                ),
              },
            ]}
            rows={counterexamples}
            emptyMessage="No counterexamples found yet — run a hunt"
          />
        </div>

        <div>
          {selectedCE ? (
            <div>
              <GraphViewer
                points={selectedCE.points}
                tour={selectedCE.optimal_tour}
                width={500}
                height={200}
              />
              <div style={{ marginTop: 8 }}>
                <GraphViewer
                  points={selectedCE.points}
                  tour={selectedCE.algorithm_tour}
                  width={500}
                  height={200}
                />
              </div>
              <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-dim)' }}>
                Top: optimal tour ({selectedCE.optimal_tour_length.toFixed(2)}) · Bottom: algorithm tour ({selectedCE.algorithm_tour_length.toFixed(2)})
              </div>
            </div>
          ) : (
            <div className="panel">
              <div className="panel-body" style={{ color: 'var(--text-dim)', textAlign: 'center', padding: 64 }}>
                Select a counterexample to compare tours
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
