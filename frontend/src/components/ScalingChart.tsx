// frontend/src/components/ScalingChart.tsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

interface DataPoint {
  n: number
  time: number
}

interface Props {
  data: DataPoint[]
  bestFit?: string
}

export default function ScalingChart({ data, bestFit }: Props) {
  return (
    <div className="panel">
      <div className="panel-header">
        Scaling Analysis {bestFit && <span style={{ color: 'var(--primary)', marginLeft: 8 }}>{bestFit}</span>}
      </div>
      <div className="panel-body">
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1a1a2e" />
            <XAxis dataKey="n" stroke="#475569" fontSize={10} fontFamily="JetBrains Mono" />
            <YAxis stroke="#475569" fontSize={10} fontFamily="JetBrains Mono" />
            <Tooltip
              contentStyle={{
                background: '#0f0f18',
                border: '1px solid #1a1a2e',
                fontFamily: 'JetBrains Mono',
                fontSize: 11,
              }}
            />
            <Line type="monotone" dataKey="time" stroke="#6ee7b7" dot={{ r: 2 }} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
