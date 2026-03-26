export default function ProgressLog({ results }) {
  if (!results || results.length === 0) return null

  return (
    <div className="progress-log">
      {results.map((r, i) => (
        <div key={i} className={`log-entry ${r.status}`}>
          <span className="log-icon">{r.status === 'ok' ? '✅' : '❌'}</span>
          <span className="log-file">{r.file}</span>
          {r.error && <span className="log-error">{r.error}</span>}
        </div>
      ))}
    </div>
  )
}
