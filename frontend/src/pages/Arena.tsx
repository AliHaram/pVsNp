// frontend/src/pages/Arena.tsx
import { useEffect, useState, useRef } from 'react'
import { api } from '../api/client'
import ResultsTable from '../components/ResultsTable'

export default function Arena() {
  const [algorithms, setAlgorithms] = useState<any[]>([])
  const [instances, setInstances] = useState<any[]>([])
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const refresh = () => {
    api.listAlgorithms().then(setAlgorithms)
    api.listInstances().then(setInstances)
  }

  useEffect(() => { refresh() }, [])

  const handleUpload = async () => {
    const file = fileRef.current?.files?.[0]
    if (!file) return
    await api.uploadAlgorithm(file)
    refresh()
    if (fileRef.current) fileRef.current.value = ''
  }

  const handleBenchmark = async () => {
    if (algorithms.length === 0 || instances.length === 0) return
    setLoading(true)
    try {
      const run = await api.runBenchmark({
        algorithm_ids: algorithms.map(a => a.id),
        instance_ids: instances.slice(0, 10).map(i => i.id),
      })
      setResults(run.results)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    await api.deleteAlgorithm(id)
    refresh()
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ color: 'var(--primary)', fontSize: 16 }} className="glow">Algorithm Arena</h2>
        <div style={{ display: 'flex', gap: 8 }}>
          <input ref={fileRef} type="file" accept=".py" style={{ width: 'auto' }} />
          <button className="btn btn-primary" onClick={handleUpload}>Upload</button>
          <button className="btn btn-primary" onClick={handleBenchmark} disabled={loading}>
            {loading ? 'Running...' : 'Run Benchmark'}
          </button>
        </div>
      </div>

      <div className="split">
        <div>
          <ResultsTable
            columns={[
              { key: 'name', label: 'Algorithm' },
              { key: 'category', label: 'Category' },
              { key: 'author', label: 'Author' },
              {
                key: 'id', label: '',
                render: (val: number) => (
                  <button className="btn btn-danger" onClick={() => handleDelete(val)} style={{ padding: '2px 8px', fontSize: 10 }}>
                    del
                  </button>
                ),
              },
            ]}
            rows={algorithms}
            emptyMessage="No algorithms uploaded yet"
          />
        </div>

        <div>
          <ResultsTable
            columns={[
              { key: 'algorithm_name', label: 'Algorithm' },
              {
                key: 'tour_length', label: 'Tour Length',
                render: (v: number | null) => v !== null ? v.toFixed(2) : '–',
              },
              {
                key: 'execution_time', label: 'Time',
                render: (v: number | null) => v !== null ? `${v.toFixed(4)}s` : '–',
              },
              {
                key: 'is_optimal', label: 'Optimal',
                render: (v: boolean | null) =>
                  v === null ? '–' :
                  v ? <span className="badge-success">yes</span> :
                  <span className="badge-warning">no</span>,
              },
              {
                key: 'error', label: 'Error',
                render: (v: string | null) => v ? <span className="badge-error">{v}</span> : '–',
              },
            ]}
            rows={results}
            emptyMessage="Run a benchmark to see results"
          />
        </div>
      </div>
    </div>
  )
}
