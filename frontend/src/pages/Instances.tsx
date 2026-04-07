// frontend/src/pages/Instances.tsx
import { useEffect, useState } from 'react'
import { api } from '../api/client'
import GraphViewer from '../components/GraphViewer'
import ResultsTable from '../components/ResultsTable'

export default function Instances() {
  const [instances, setInstances] = useState<any[]>([])
  const [selected, setSelected] = useState<any>(null)
  const [genType, setGenType] = useState('random')
  const [genN, setGenN] = useState(10)
  const [genCount, setGenCount] = useState(5)

  const refresh = () => api.listInstances().then(setInstances)
  useEffect(() => { refresh() }, [])

  const handleGenerate = async () => {
    await api.generateInstances({ instance_type: genType, n: genN, count: genCount })
    refresh()
  }

  const handleSelect = async (id: number) => {
    const inst = await api.getInstance(id)
    setSelected(inst)
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ color: 'var(--primary)', fontSize: 16 }} className="glow">Instances</h2>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <select value={genType} onChange={e => setGenType(e.target.value)} style={{ width: 120 }}>
            <option value="random">Random</option>
            <option value="clustered">Clustered</option>
            <option value="grid">Grid</option>
            <option value="adversarial">Adversarial</option>
          </select>
          <label style={{ color: 'var(--text-dim)', fontSize: 11 }}>n=</label>
          <input type="number" value={genN} onChange={e => setGenN(+e.target.value)} style={{ width: 60 }} min={3} max={500} />
          <label style={{ color: 'var(--text-dim)', fontSize: 11 }}>count=</label>
          <input type="number" value={genCount} onChange={e => setGenCount(+e.target.value)} style={{ width: 60 }} min={1} max={100} />
          <button className="btn btn-primary" onClick={handleGenerate}>Generate</button>
        </div>
      </div>

      <div className="split">
        <div>
          <ResultsTable
            columns={[
              { key: 'id', label: '#' },
              { key: 'instance_type', label: 'Type' },
              { key: 'n', label: 'N' },
              {
                key: 'id', label: '',
                render: (id: number) => (
                  <button className="btn" onClick={() => handleSelect(id)} style={{ padding: '2px 8px', fontSize: 10 }}>
                    view
                  </button>
                ),
              },
            ]}
            rows={instances}
            emptyMessage="Generate some instances to get started"
          />
        </div>

        <div>
          {selected ? (
            <GraphViewer points={selected.points} width={500} height={400} />
          ) : (
            <div className="panel">
              <div className="panel-body" style={{ color: 'var(--text-dim)', textAlign: 'center', padding: 64 }}>
                Select an instance to visualize
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
