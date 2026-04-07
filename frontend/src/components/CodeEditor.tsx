// frontend/src/components/CodeEditor.tsx
interface Props {
  value: string
  onChange: (value: string) => void
  placeholder?: string
}

export default function CodeEditor({ value, onChange, placeholder }: Props) {
  return (
    <div className="panel">
      <div className="panel-header">Algorithm Code</div>
      <textarea
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder || '# Paste your algorithm here...'}
        style={{
          width: '100%',
          minHeight: 200,
          background: 'var(--bg)',
          border: 'none',
          borderTop: '1px solid var(--border)',
          padding: 16,
          resize: 'vertical',
          fontFamily: 'var(--font)',
          fontSize: 12,
          lineHeight: 1.7,
          color: 'var(--text)',
        }}
        spellCheck={false}
      />
    </div>
  )
}
