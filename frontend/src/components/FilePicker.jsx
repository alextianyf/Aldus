export default function FilePicker({ value, onChange }) {
  return (
    <div className="section">
      <label className="label">Input</label>
      <div className="input-row">
        <input
          className="input"
          type="text"
          placeholder="Paste a file or folder path..."
          value={value}
          onChange={e => onChange(e.target.value)}
        />
      </div>
      <p className="hint">
        Single <code>.md</code> file → one PDF &nbsp;|&nbsp; Folder → converts all markdown files recursively
      </p>
    </div>
  )
}
