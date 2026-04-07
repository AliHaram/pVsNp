// frontend/src/components/ResultsTable.tsx

interface Column {
  key: string
  label: string
  render?: (value: any, row: any) => React.ReactNode
}

interface Props {
  columns: Column[]
  rows: any[]
  emptyMessage?: string
}

export default function ResultsTable({ columns, rows, emptyMessage = 'No data' }: Props) {
  if (rows.length === 0) {
    return (
      <div className="panel">
        <div className="panel-body" style={{ color: 'var(--text-dim)', textAlign: 'center', padding: 32 }}>
          {emptyMessage}
        </div>
      </div>
    )
  }

  return (
    <div className="panel" style={{ overflow: 'auto' }}>
      <table className="table">
        <thead>
          <tr>
            {columns.map(col => <th key={col.key}>{col.label}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {columns.map(col => (
                <td key={col.key}>
                  {col.render ? col.render(row[col.key], row) : row[col.key] ?? '–'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
