export default function ThemeSelector({ themes, value, onChange }) {
  return (
    <div className="section">
      <label className="label">Theme</label>
      <div className="theme-grid">
        {themes.map(t => (
          <button
            key={t}
            className={`theme-btn ${value === t ? 'active' : ''}`}
            onClick={() => onChange(t)}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>
    </div>
  )
}
